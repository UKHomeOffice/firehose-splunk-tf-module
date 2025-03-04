"""MBTP Splunk Cloudwatch Ingestion - Reingestion Lambda"""

import base64
import gzip
import json
import logging
from os import environ

import boto3
import botocore

logger = logging.getLogger()


REQUIRED_ENV_VARS = {
    "AWS_REGION",
    "MAX_RETRIES",
    "STREAM_NAME",
    "RETRIES_PREFIX",
    "FAILED_PREFIX",
}


def check_required_env_vars():
    """Function to check all required environment variables exist"""
    if missing_variables := REQUIRED_ENV_VARS.difference(environ):
        raise EnvironmentError(
            f"The following environment variables need to be set: {missing_variables}"
        )


REGION = environ["AWS_REGION"]
MAX_RETRIES = int(environ["MAX_RETRIES"])
STREAM_NAME = environ["STREAM_NAME"]
RETRIES_PREFIX = environ["RETRIES_PREFIX"]
FAILED_PREFIX = environ["FAILED_PREFIX"]

s3_client = boto3.client("s3", region_name=REGION)
firehose_client = boto3.client("firehose", region_name=REGION)


def get_records_from_s3(bucket: str, key: str, version_id: str) -> list[str]:
    """Gets a file from S3 and extracts all the firehose records within it.

    Args:
        bucket (str): S3 Bucket to download from.
        key (str): Key within the bucket to download.
        version_id (str): Version ID to download.

    Returns:
        list[str]: A list of the records/lines from the S3 file.
                    The contents of the rawData key has been extracted and base64 decoded.
    """
    # Grab the file from S3 and loop through the lines in it
    s3_file = s3_client.get_object(Bucket=bucket, Key=key, VersionId=version_id)
    records = []
    s3_file_data = s3_file["Body"].read().decode()
    logger.debug("S3 file data", extra={"data": s3_file_data})

    for line in s3_file_data.splitlines():
        if line.strip():
            # Parse the line as JSON, extract the rawData and b64 decode it
            batch = json.loads(line)
            try:
                record = gzip.decompress(base64.b64decode(batch["rawData"])).decode()
            except gzip.BadGzipFile:
                record = base64.b64decode(batch["rawData"]).decode()

            records.append(record)
    logger.debug(f"Downloaded {key} and extracted {records}")
    logger.debug("S3 parsed data", extra={"data": records})
    return records


def get_logs_from_record(record: str) -> list[dict]:
    """Loops through a the records logs and parses them to json

    Args:
        record (str): The rawData field from a firehose failure extracted from S3.

    Returns:
        list[dict]: A list of JSON objects
            i.e. the logs after they were transformed by the transformation lambda.
    """
    logs = [json.loads(log) for log in record.splitlines()]
    logger.debug("Extracted logs from record", extra={"data": logs})
    return logs


def add_log_to_output_list(
    log: dict, data_to_firehose: list[dict], data_to_s3: list[dict]
):
    """Checks if a log has looped retrying too many times and
        assigns it's destination to either Firehose or S3.

    Args:
        log (dict): _description_
        data_to_firehose (list[dict]): _description_
        data_to_s3 (list[dict]): _description_
    """
    if "fields" not in log:
        log["fields"] = {}

    # Increase the error count, check if it's greater than MAX_RETRIES
    # and add it to the appropriate list.
    log["fields"]["firehose_errors"] = log["fields"].get("firehose_errors", 0) + 1
    if log["fields"]["firehose_errors"] >= MAX_RETRIES:
        logger.info(f"Greater than MAX_RETRIES, sending to S3 - {log}")
        data_to_s3.append(log)
    else:
        logger.info(
            f"{log["fields"]["firehose_errors"]} is less than MAX_RETRIES, sending to Firehose - {log}"
        )
        data_to_firehose.append(log)


def get_s3_lines(data_to_s3: list[dict]) -> list:
    s3_lines = []
    for log in data_to_s3:
        # Remove the firehose_errors key from the log so that when Splunk/Firehose
        # is fixed, we will allow this file to be processed again and not end up back in S3.
        log["fields"].pop("firehose_errors")
        # Place the log back in S3 in the same format it we received it from Firehose in.
        s3_lines.append(
            json.dumps(
                {
                    "rawData": base64.b64encode(
                        gzip.compress(json.dumps(log).encode())
                    ).decode()
                }
            )
        )
    return s3_lines


def send_to_s3(data_to_s3: list[dict], bucket: str, key: str):
    """Takes a list of log messages and puts them in S3

    Args:
        data_to_s3 (list[dict]): List of the json logs to put in S3
        bucket (str): S3 bucket to put them in
        key (str): Key to save them to.
    """
    if data_to_s3:
        logger.debug(f"Sending data to S3", extra={"data": data_to_s3})
        s3_lines = "\n".join(get_s3_lines(data_to_s3)).encode()
        logger.debug(f"Sending lines to S3", extra={"data": s3_lines})
        s3_client.put_object(Bucket=bucket, Key=key, Body=s3_lines)
        logger.debug(f"Written file to {bucket}/{key}")


# https://docs.aws.amazon.com/firehose/latest/APIReference/API_PutRecordBatch.html
def send_to_firehose(
    data_to_firehose: list[dict],
    data_to_s3: list[dict],
    max_records: int = 500,
    max_record_size: int = 1_000_000,
    max_request_size: int = 4_000_000,
):
    """Sends logs back into firehose for reingestion

    Args:
        data_to_firehose (list[dict]): List of logs to send to firehose
        data_to_s3 (list[dict]): Data to send to S3
            (in case we can't send to firehose, we add them to this as a fallback)
        max_records (int, optional): Maximum number of records to send to Firehose at once.
            Defaults to 500.
        max_record_size (int, optional): Maximum size of a single record.
            Defaults to 1_000_000.
        max_request_size (int, optional): Maximum size per request to Firehose.
            Defaults to 4_000_000.
    """
    if data_to_firehose:
        records = []
        predicted_size = 0
        for log in data_to_firehose:
            # Compress the log with GZIP so we can process it the same as the
            # Cloudwatch logs when we receive it back on the transformation lambda.
            logger.debug("Sending to firehose", extra={"data": log})

            compressed_data = gzip.compress(json.dumps(log).encode())
            record = {"Data": compressed_data}
            record_size = len(
                json.dumps(
                    {"Data": base64.b64encode(compressed_data).decode()}
                ).encode()
            )
            # Check that the record/log isn't greater than the max_record_size
            # It shouldn't be as Firehose transformed it before.
            if record_size < max_record_size:
                # Check that we don't have too many records, or our request isn't too big.
                if (
                    len(records) == max_records
                    or predicted_size + record_size >= max_request_size
                ):
                    # If it is, flush the current list to Firehose
                    push_to_firehose(data_to_s3, records)
                    records = []
                    predicted_size = 0
                predicted_size += record_size
                records.append(record)
            else:
                logger.debug(f"Log is too big, adding to S3 instead - {log}")
                data_to_s3.append(log)
        if records:
            # Catch any leftover records at the end
            push_to_firehose(data_to_s3, records)


def push_to_firehose(
    data_to_s3: list[dict],
    records: list[dict],
    attempts_made: int = 0,
    max_attempts: int = 20,
):
    """Calls the Firehose put_record_batch API and checks for errors.

    Args:
        data_to_s3 (list[dict]): Data to send to S3
            (in case we can't send to firehose, we add them to this as a fallback)
        records (list[dict]): Records to send to Firehose.
        attempts_made (int, optional): Number of attempts we've made sending already.
            Defaults to 0.
        max_attempts (int, optional): Maximum number of attempts before we give up and put it in S3.
            Defaults to 20.
    """
    logger.debug(f"Sending {len(records)} to Firehose")

    failed_records = []
    codes = []
    err_msg = ""
    response = None

    # Try to send the logs to firehose, catch any errors doing it.
    try:
        response = firehose_client.put_record_batch(
            DeliveryStreamName=STREAM_NAME, Records=records
        )
    except Exception as e:  # pylint: disable=broad-exception-caught
        failed_records = records
        err_msg = str(e)
        logger.warning(
            (
                "Some records failed while calling ",
                f"PutRecordBatch to Firehose stream, retrying. {err_msg}",
            )
        )

    # If it was accepted by firehose, check if any of the logs failed to process
    if not failed_records and response and response["FailedPutCount"] > 0:
        for idx, res in enumerate(response["RequestResponses"]):
            if not res.get("ErrorCode"):
                continue

            codes.append(res["ErrorCode"])
            failed_records.append(records[idx])

        err_msg = "Individual error codes: " + ",".join(codes)

    # If any logs failed to process, increase the counter and try sending them again
    if failed_records:
        if attempts_made + 1 < max_attempts:
            logger.warning(
                (
                    "Some records failed while calling ",
                    f"PutRecordBatch to Firehose stream, retrying. {err_msg}",
                )
            )
            push_to_firehose(
                data_to_s3, failed_records, attempts_made + 1, max_attempts
            )
        else:
            # If we failed to send them to firehose after max_attempts,
            # fallback to the S3 bucket for a manual fix
            for failed_record in failed_records:
                data_to_s3.append(json.loads(gzip.decompress(failed_record["Data"])))


def does_file_exist(bucket: str, key: str, version_id: str) -> bool:
    """Checks if a file exists in S3

    Args:
        bucket (str): S3 Bucket to check.
        key (str): Key within the bucket to check.
        version_id (str): Version ID to check.

    Returns:
        bool: True if exists
    """
    try:
        s3_client.head_object(Bucket=bucket, Key=key, VersionId=version_id)
        return True
    except botocore.exceptions.ClientError as e:
        if str(e.response["Error"]["Code"]) in ["403", "404"]:
            return False
        else:
            raise


def lambda_handler(event: dict, _context: dict):
    """Lambda Handler to download logs from S3 and retry sending them to Firehose.

    Args:
        event (dict): SQS Event from AWS
        _context (dict): Lambda execution context - not used.
    """
    logger.debug("Incoming event", extra={"data": event})

    # https://docs.aws.amazon.com/lambda/latest/dg/with-sqs.html#example-standard-queue-message-event
    for sqs_record in event.get("Records", []):
        s3_event = json.loads(sqs_record.get("body", {}))
        # https://docs.aws.amazon.com/AmazonS3/latest/userguide/notification-content-structure.html
        for s3_record in s3_event.get("Records", []):
            data_to_s3: list[dict] = []
            data_to_firehose: list[dict] = []

            bucket = s3_record["s3"]["bucket"]["name"]
            key = s3_record["s3"]["object"]["key"]
            version_id = s3_record["s3"]["object"]["versionId"]

            if not does_file_exist(bucket, key, version_id):
                continue

            # Get the logs from the file and assign them to firehose or S3
            logger.info(f"Processing {key}")
            records = get_records_from_s3(bucket, key, version_id)
            for record in records:
                for log in get_logs_from_record(record):
                    add_log_to_output_list(log, data_to_firehose, data_to_s3)

            logger.info(f"Processed {bucket}/{key}")
            logger.info(f"Sending {len(data_to_firehose)} to Firehose")
            send_to_firehose(data_to_firehose, data_to_s3)

            logger.info(f"Sending {len(data_to_s3)} to S3")
            send_to_s3(
                data_to_s3, bucket, f"{FAILED_PREFIX}{key.removeprefix(RETRIES_PREFIX)}"
            )

            logger.info(f"Deleting {bucket}/{key}")
            s3_client.delete_object(Bucket=bucket, Key=key, VersionId=version_id)
