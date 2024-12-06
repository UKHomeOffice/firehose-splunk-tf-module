# Copyright 2014, Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Amazon Software License (the "License").
# You may not use this file except in compliance with the License.
# A copy of the License is located at
#
#  http://aws.amazon.com/asl/
#
# or in the "license" file accompanying this file. This file is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.

"""
MBTP Splunk Cloudwatch Ingestion - Transformation Lambda


For processing data sent to Firehose by Cloudwatch Logs subscription filters.

Cloudwatch Logs sends to Firehose records that look like this:

{
  "messageType": "DATA_MESSAGE",
  "owner": "123456789012",
  "logGroup": "log_group_name",
  "logStream": "log_stream_name",
  "subscriptionFilters": [
    "subscription_filter_name"
  ],
  "logEvents": [
    {
      "id": "01234567890123456789012345678901234567890123456789012345",
      "timestamp": 1510109208016,
      "message": "log message 1"
    },
    {
      "id": "01234567890123456789012345678901234567890123456789012345",
      "timestamp": 1510109208017,
      "message": "log message 2"
    }
    ...
  ]
}

The data is additionally compressed with GZIP.

The code below will:

1) Gunzip the data
2) Parse the json
3) Set the result to ProcessingFailed for any record whose messageType is not DATA_MESSAGE, thus redirecting them to the
   processing error output. Such records do not contain any log events. You can modify the code to set the result to
   Dropped instead to get rid of these records completely.
4) For records whose messageType is DATA_MESSAGE, extract the individual log events from the logEvents field, and pass
   each one to the transform_log_event method. You can modify the transform_log_event method to perform custom
   transformations on the log events.
5) Concatenate the result from (4) together and set the result as the data of the record returned to Firehose. Note that
   this step will not add any delimiters. Delimiters should be appended by the logic within the transform_log_event
   method.
6) Any individual record exceeding 6,000,000 bytes in size after decompression, processing and base64-encoding is marked
   as Dropped, and the original record is split into two and re-ingested back into Firehose or Kinesis. The re-ingested
   records should be about half the size compared to the original, and should fit within the size limit the second time
   round.
7) When the total data size (i.e. the sum over multiple records) after decompression, processing and base64-encoding
   exceeds 6,000,000 bytes, any additional records are re-ingested back into Firehose or Kinesis.
8) The retry count for intermittent failures during re-ingestion is set 20 attempts. If you wish to retry fewer number
   of times for intermittent failures you can lower this value.

                                              ***IMPORTANT NOTE***
When using this blueprint, it is highly recommended to change the Amazon Data Firehose Lambda setting for buffer size to
256KB to avoid 6MB Lambda limit.
"""

import base64
import gzip
import json
import logging
import re
from os import environ

import boto3
import yaml
from cerberus import Validator

logger = logging.getLogger()
logger.setLevel(environ.get("LOG_LEVEL", "INFO"))


REQUIRED_ENV_VARS = {"AWS_REGION", "CONFIG_S3_BUCKET", "CONFIG_S3_KEY"}


def check_required_env_vars():
    """Function to check all required environment variables exist"""
    if missing_variables := REQUIRED_ENV_VARS.difference(environ):
        raise EnvironmentError(
            f"The following environment variables need to be set: {missing_variables}"
        )


check_required_env_vars()

REGION = environ["AWS_REGION"]

firehose_client = boto3.client("firehose", region_name=REGION)
s3_client = boto3.client("s3", region_name=REGION)


class InvalidConfigException(Exception):
    """Invalid Config Exception"""


def get_validated_config() -> dict:
    """Downloads a configuration file from S3 and checks it matches the required schema.

    Raises:
        InvalidConfigException: Raised if the config does not match what's required.

    Returns:
        dict: Processed configuration.
    """
    s3_config_file: dict = s3_client.get_object(
        Bucket=environ["CONFIG_S3_BUCKET"], Key=environ["CONFIG_S3_KEY"]
    )
    config_yaml: dict = yaml.safe_load(s3_config_file["Body"].read().decode())

    log_group_schema = {
        "accounts": {
            "type": "list",
            "schema": {"type": "integer"},
            "required": True,
        },
        "index": {"type": "string", "required": True},
        "log_streams": {
            "type": "list",
            "schema": {
                "type": "dict",
                "schema": {
                    "regex": {
                        "type": "string",
                        "required": True,
                    },
                    "sourcetype": {
                        "type": "string",
                        "required": True,
                        "allowed": list(config_yaml.get("sourcetypes", {}).keys()),
                    },
                },
            },
            "required": True,
        },
    }
    sourcetypes_schema = {
        "allowlist_regexes": {"type": "list", "schema": {"type": "string"}},
        "denylist_regexes": {"type": "list", "schema": {"type": "string"}},
        "redact_regexes": {"type": "list", "schema": {"type": "string"}},
    }
    schema = {
        "sourcetypes": {
            "type": "dict",
            "keysrules": {"type": "string"},
            "valuesrules": {"type": "dict", "schema": sourcetypes_schema},
            "required": True,
        },
        "log_groups": {
            "type": "dict",
            "keysrules": {"type": "string"},
            "valuesrules": {"type": "dict", "schema": log_group_schema},
            "dependencies": "sourcetypes",
            "required": True,
        },
    }
    v = Validator(schema)
    v.allow_unknown = True
    if not v.validate(config_yaml):
        raise InvalidConfigException(f"Config failed to parse - {v.errors}")

    return config_yaml


CONFIG = {}
if not environ.get("PYTEST_VERSION"):  # pragma: no cover
    CONFIG = get_validated_config()

DEFAULT_ALLOW_REGEX = ".*"


def is_json(j: str) -> bool:
    """Checks if a string is json parsable

    Args:
        j (str): JSON to test

    Returns:
        bool: True if string is json parsable
    """
    try:
        json.loads(j)
    except ValueError:
        return False
    return True


def load_json_gzip_base64(base64_data: str) -> dict:
    """Converts a b64, gzip compressed string into a dictionary

    Args:
        base64_data (str): Base64 encoded data

    Returns:
        dict: Decoded, decompressed, loaded dictionary
    """
    return json.loads(gzip.decompress(base64.b64decode(base64_data)))


def transform_cloudwatch_log_event(
    event: dict,
    index: str,
    sourcetype: dict,
    sourcetype_name: str,
    firehose_arn: str,
    account_id: str,
    log_group: str,
    log_stream: str,
) -> None | str:
    """Transforms a CW event into a Splunk one

    Args:
        event (dict): Initial event
        index (str): Splunk Index
        sourcetype (dict): Sourcetype object containing regexes
        sourcetype_name (str): Splunk Sourcetype name
        firehose_arn (str): Firehose ARN
        account_id (str): AWS Account ID of the initial log
        log_group (str): Log group name
        log_stream (str): Log group stream

    Returns:
        None | str: The processed message or None if we dropped it
    """
    log = event["message"]

    for deny_regex in sourcetype.get("denylist_regexes", []):
        if re.search(deny_regex, log):
            logging.info(f"Dropping log due to matching {deny_regex}. Log = {log}")
            return None

    allowed = False
    for allow_regex in sourcetype.get("allowlist_regexes", [DEFAULT_ALLOW_REGEX]):
        if re.search(allow_regex, log):
            allowed = True
            break
    if not allowed:
        logging.info(
            f"Dropping log because it did not match any allowlist regexes. Log = {log}"
        )
        return None

    for regex_index, redact_regex in enumerate(sourcetype.get("redact_regexes", [])):
        if match := re.search(redact_regex, log):
            for group_index, _ in enumerate(match.groups()):
                group_span = match.span(group_index + 1)
                log = (
                    log[: group_span[0]]
                    + f"***REDACTED BY {sourcetype_name}.redact_regexes.{regex_index}***"
                    + log[group_span[1] :]
                )

    if is_json(log):
        log = json.loads(log)

    new_log = {
        "index": index,
        "sourcetype": sourcetype_name,
        "time": str(event["timestamp"]),
        "host": firehose_arn,
        "source": log_group,
        "fields": {
            "aws_account_id": account_id,
            "cw_log_stream": log_stream,
        },
        "event": log,
    }

    return json.dumps(new_log)


def process_cloudwatch_log_record(
    data: dict, rec_id: str, firehose_arn: str, config: dict
) -> dict:
    """Matches a CW event to a Splunk index and source type

    Args:
        data (dict): CW Event
        rec_id (str): Firehose Record ID
        firehose_arn (str): Firehose ARN
        config (dict): Configuration to match against

    Returns:
        dict: Processed records
    """
    # CONTROL_MESSAGE are sent by CWL to check if the subscription is reachable.
    # They do not contain actual data.
    if data["messageType"] == "CONTROL_MESSAGE":
        return {"result": "Dropped", "recordId": rec_id}
    if data["messageType"] == "DATA_MESSAGE":
        account_id = data["owner"]
        log_group = data["logGroup"]
        log_stream = data["logStream"]

        if log_group not in config["log_groups"]:
            logging.info(
                f"Dropping as we cannot locate a log_group({log_group}) match for it."
            )
            return {"result": "Dropped", "recordId": rec_id}

        if int(account_id) not in config["log_groups"][log_group]["accounts"]:
            logging.info(
                f"Dropping as we cannot locate a log_group({log_group}) and account_id({account_id}) match for it."
            )
            return {"result": "Dropped", "recordId": rec_id}

        index = config["log_groups"][log_group]["index"]

        sourcetype_name = None
        for sourcetype in config["log_groups"][log_group]["log_streams"]:
            if re.match(sourcetype["regex"], log_stream):
                sourcetype_name = sourcetype["sourcetype"]
                break

        if not sourcetype_name:
            logging.info(
                f"Dropping as we cannot locate a sourcetype match for log_stream({log_stream})/log_group({log_group})."
            )
            return {"result": "Dropped", "recordId": rec_id}

        sourcetype = config["sourcetypes"][sourcetype_name]

        log_events = [
            event
            for log_event in data["logEvents"]
            if (
                event := transform_cloudwatch_log_event(
                    log_event,
                    index,
                    sourcetype,
                    sourcetype_name,
                    firehose_arn,
                    account_id,
                    log_group,
                    log_stream,
                )
            )
        ]

        return {
            "data": base64.b64encode("\n".join(log_events).encode()).decode(),
            "result": "Ok",
            "recordId": rec_id,
        }
    return {"result": "ProcessingFailed", "recordId": rec_id}


def get_record_size(record: dict) -> int:
    """Dumps to a dict to a string and calculates the length of it in bytes.

    Args:
        record (dict): Dictionary to get the size of

    Returns:
        int: Size of the dictionary
    """
    return len(json.dumps(record).encode())


def process_records(records: list[dict], firehose_arn: str, config: dict) -> list:
    """Loops through records, works out their type and processes them accordingly.

    Args:
        records (list[dict]): Records to process
        firehose_arn (str): Firehose ARN that received them
        config (dict): Configuration used to process the CW events

    Returns:
        list: Processed records
    """
    returned_records = []
    for r in records:
        data = load_json_gzip_base64(r["data"])
        rec_id = r["recordId"]

        if set(("messageType", "logGroup", "owner", "logEvents")) <= data.keys():
            # If it's a Cloudwatch log record
            returned_records.append(
                process_cloudwatch_log_record(data, rec_id, firehose_arn, config)
            )
        elif set(("index", "sourcetype", "event")) <= data.keys():
            # Else if it's a reingested log which can skip processing
            logging.info(f"Reingested log detected, forwarding it on. {r}")
            returned_records.append(
                {
                    "data": base64.b64encode(json.dumps(data).encode()).decode(),
                    "result": "Ok",
                    "recordId": rec_id,
                }
            )
        else:
            # Else it's an unknown log, so reject it
            returned_records.append({"result": "ProcessingFailed", "recordId": rec_id})
    return returned_records


def split_cwl_record(cwl_record: dict) -> list:
    """
    Splits one CWL record into two, each containing half the log events.
    Serializes and compresses the data before returning. That data can then be
    re-ingested into the stream, and it'll appear as though they came from CWL
    directly.

    Args:
        cwl_record (dict): Cloudwatch Record

    Returns:
        list: Split up cloudwatch events, compressed ready for reingestion
    """

    log_events = cwl_record["logEvents"]
    mid = len(log_events) // 2
    rec1 = dict(cwl_record.items())
    rec1["logEvents"] = log_events[:mid]
    rec2 = dict(cwl_record.items())
    rec2["logEvents"] = log_events[mid:]
    return [gzip.compress(json.dumps(r).encode()) for r in [rec1, rec2]]


def put_records_to_firehose_stream(
    stream_name: str,
    records: list[dict],
    attempts_made: int = 0,
    max_attempts: int = 20,
):
    """Tries to send records back to firehose.

    Args:
        stream_name (str): Stream to send the logs to.
        records (list[dict]): Records to send.
        attempts_made (int, optional): How many attempts we've already made. Defaults to 0.
        max_attempts (int, optional): How many attempts to make. Defaults to 20.

    Raises:
        RuntimeError: If we fail to send them, raise this error
    """
    failed_records = []
    codes = []
    err_msg = ""
    response = None
    try:
        response = firehose_client.put_record_batch(
            DeliveryStreamName=stream_name, Records=records
        )
    except Exception as e:  # pylint: disable=broad-exception-caught
        failed_records = records
        err_msg = str(e)

    # if there are no failed_records (put_record_batch succeeded), iterate over the response to gather results
    if not failed_records and response and response["FailedPutCount"] > 0:
        for idx, res in enumerate(response["RequestResponses"]):
            # (if the result does not have a key 'ErrorCode' OR if it does and is empty) => we do not need to re-ingest
            if not res.get("ErrorCode"):
                continue

            codes.append(res["ErrorCode"])
            failed_records.append(records[idx])

        err_msg = "Individual error codes: " + ",".join(codes)

    if failed_records:
        if attempts_made + 1 < max_attempts:
            logging.info(
                f"Some records failed while calling Putrecord_batch to Firehose stream, retrying. {err_msg}"
            )
            put_records_to_firehose_stream(
                stream_name, failed_records, attempts_made + 1, max_attempts
            )
        else:
            raise RuntimeError(
                f"Could not put records after {str(max_attempts)} attempts. {err_msg}"
            )


def create_reingestion_record(original_record: dict, data: bytes | None = None) -> dict:
    """Creates a reingestion record to send back to firehose

    Args:
        original_record (dict): Original Record
        data (bytes | None, optional): Data to include in the record. Defaults to None.

    Returns:
        dict: Record to send back to firehose
    """
    if data is None:
        data = base64.b64decode(original_record["data"])
    r = {"Data": data}
    return r


def reingest_records(
    record_lists_to_reingest: list[list[dict]],
    stream_name: str,
    max_batch_size: int = 500,
):
    """Reingests records back into firehose

    Args:
        record_lists_to_reingest (list[list[dict]]): Records to reingest.
        stream_name (str): Name of the firehose stream.
        max_batch_size (int, optional): Maximum number of records to send to firehose at once. Defaults to 500.
    """
    # call putrecord_batch/putRecords for each group of up to 500 records to be re-ingested
    if record_lists_to_reingest:
        records_reingested_so_far = 0
        flattened_list = [r for sublist in record_lists_to_reingest for r in sublist]
        for i in range(0, len(flattened_list), max_batch_size):
            record_batch = flattened_list[i : i + max_batch_size]
            # last argument is maxAttempts
            put_records_to_firehose_stream(stream_name, record_batch)
            records_reingested_so_far += len(record_batch)
            logging.info(
                f"Reingested {records_reingested_so_far}/{len(flattened_list)}"
            )


def work_out_records_to_reingest(
    event: dict, records: list[dict], max_return_size: int = 6_000_000
) -> list[list[dict]]:
    """Goes through all the processed records and works out what cannot be returned through the lambda return.

    Args:
        event (dict): Initial event object
        records (list[dict]): Transformed records
        max_return_size (int, optional): Maximum lambda return size. Defaults to 6_000_000.

    Returns:
        list[dict]: Records which cannot be returned and need resubmitting to Firehose.
    """
    record_lists_to_reingest = []
    projected_return_size = 0

    for idx, rec in enumerate(records):
        original_record = event["records"][idx]

        record_size = get_record_size(rec)

        if rec["result"] != "Ok":
            projected_return_size += record_size
            continue

        # If a single record is too large after processing, split the original CWL data into two, each containing half
        # the log events, and re-ingest both of them (note that it is the original data that is re-ingested, not the
        # processed data). If it's not possible to split because there is only one log event, then mark the record as
        # ProcessingFailed, which sends it to error output.

        # If the record is greater than 6MB
        # We shouldn't get any processed reingested logs hitting this as they will be less than 6MB (reingestion already checked that)
        if record_size > max_return_size:
            # Reload original data
            cwl_record = load_json_gzip_base64(original_record["data"])
            # If there is more than one log event, split log events in half and re-process
            if len(cwl_record.get("logEvents", [])) > 1:
                rec["result"] = "Dropped"
                record_lists_to_reingest.append(
                    [
                        create_reingestion_record(original_record, data)
                        for data in split_cwl_record(cwl_record)
                    ]
                )
            else:
                # Else if it's just one large message, drop it
                rec["result"] = "ProcessingFailed"
                logging.info(
                    f"Record {rec["recordId"]} contains only one log event but is still too large after processing ({record_size} bytes), marking it as {rec["result"]}"
                )
            del rec["data"]
        else:
            # If the record is less than 6MB,
            projected_return_size += record_size
            # 6000000 instead of 6291456 to leave ample headroom for the stuff we didn't account for
            if projected_return_size > max_return_size:
                record_lists_to_reingest.append(
                    [create_reingestion_record(original_record)]
                )
                del rec["data"]
                rec["result"] = "Dropped"
    return record_lists_to_reingest


def lambda_handler(event: dict, _context: dict) -> dict:
    """Lambda function to transform cloudwatch logs to Splunk HEC events.

    Args:
        event (dict): Cloudwatch event
        _context (dict): Lambda context

    Returns:
        dict: Transformed logs
    """
    firehose_arn = event["deliveryStreamArn"]
    stream_name = firehose_arn.split("/")[1]

    records = process_records(event["records"], firehose_arn, CONFIG)
    record_lists_to_reingest = work_out_records_to_reingest(event, records)
    reingest_records(record_lists_to_reingest, stream_name)

    logging.info(
        "%d input records, %d returned as Ok or ProcessingFailed, %d split and re-ingested, %d re-ingested as-is"
        % (
            len(event["records"]),
            len([r for r in records if r["result"] != "Dropped"]),
            len([l for l in record_lists_to_reingest if len(l) > 1]),
            len([l for l in record_lists_to_reingest if len(l) == 1]),
        )
    )

    return {"records": records}
