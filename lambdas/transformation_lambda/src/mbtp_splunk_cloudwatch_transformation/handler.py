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


REQUIRED_ENV_VARS = {"AWS_REGION", "config_S3_BUCKET", "config_S3_KEY"}


def check_required_env_vars():
    """Function to check all required environment variables exist"""
    if missing_variables := REQUIRED_ENV_VARS.difference(environ):
        raise EnvironmentError(
            f"The following environment variables need to be set: {missing_variables}"
        )


check_required_env_vars()

REGION = environ["AWS_REGION"]

s3_client = boto3.client("s3", region_name=REGION)
firehose_client = boto3.client("firehose", region_name=REGION)


def get_validate_config() -> dict:
    s3_config_file: dict = s3_client.get_object(
        Bucket=environ["config_S3_BUCKET"], Key=environ["config_S3_KEY"]
    )
    config_yaml: dict = yaml.safe_load(s3_config_file["Body"].read().decode())

    log_group_schema = {
        "accounts": {
            "type": "list",
            "schema": {"type": ["string", "integer"], "coerce": str},
            "required": True,
        },
        "index": {"type": "string", "required": True},
        "sourcetype": {
            "type": "string",
            "required": True,
            "allowed": list(config_yaml.get("sourcetypes", {}).keys()),
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
    if not v.validate(config_yaml):
        raise Exception(f"Config failed to parse - {v.errors}")

    return config_yaml


def compile_regexes(config_obj: dict):
    # Not sure there is much performance improvements from compiling regexes prior to using them, but may as well.
    COMPILED_REGEXES = {}
    for details in config_obj["sourcetypes"].values():
        for regex_type in ["allowlist_regexes", "denylist_regexes", "redact_regexes"]:
            if regex_type in details:
                regex_key = f"{regex_type}_compiled"
                details[regex_key] = []
                for regex in details[regex_type]:
                    compiled_regex = COMPILED_REGEXES.get(regex)
                    if not compiled_regex:
                        compiled_regex = re.compile(regex)
                        COMPILED_REGEXES[regex] = compiled_regex

                    details[regex_key].append(compiled_regex)


def is_json(j: str) -> bool:
    try:
        json.loads(j)
    except ValueError:
        return False
    return True


def load_json_gzip_base64(base64_data: str) -> dict:
    return json.loads(gzip.decompress(base64.b64decode(base64_data)))


config = get_validate_config()
compile_regexes(config)


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
    log = event["message"]

    for deny_regex in sourcetype.get("denylist_regexes_compiled", []):
        if deny_regex.search(log):
            return None

    allowed = False
    for allow_regex in sourcetype.get("allowlist_regexes_compiled", []):
        if allow_regex.search(log):
            allowed = True
            break
    if not allowed:
        return None

    for regex_index, redact_regex in enumerate(
        sourcetype.get("redact_regexes_compiled", [])
    ):
        if match := redact_regex.search(log):
            for group_index, _ in enumerate(match.groups()):
                group_span = match.span(group_index + 1)
                log = (
                    log[: group_span[0]]
                    + f'*** REDACTED BY {sourcetype_name}["redact_regexes"][{regex_index}]***'
                    + log[group_span[1] :]
                )

    if is_json(log):
        log = json.loads(event["message"])

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


def process_cloudwatch_log_record(data: dict, rec_id: str, firehose_arn: str):
    # CONTROL_MESSAGE are sent by CWL to check if the subscription is reachable.
    # They do not contain actual data.
    if data["messageType"] == "CONTROL_MESSAGE":
        return {"result": "Dropped", "recordId": rec_id}
    elif data["messageType"] == "DATA_MESSAGE":
        account_id = data["owner"]
        log_group = data["logGroup"]
        log_stream = data["logStream"]

        if log_group not in config["log_groups"] or str(account_id) not in config[
            "log_groups"
        ].get(log_group, {}).get("accounts", []):
            logging.info("TODO DROPPING")
            return {"result": "Dropped", "recordId": rec_id}

        index = config["log_groups"][log_group]["index"]
        sourcetype_name = config["log_groups"][log_group]["sourcetype"]
        sourcetype = config["sourcetypes"][sourcetype_name]

        log_events = [
            event
            for e in data["logEvents"]
            if (
                event := transform_cloudwatch_log_event(
                    e,
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
    else:
        return {"result": "ProcessingFailed", "recordId": rec_id}


def process_records(records: list[dict], firehose_arn: str) -> list:
    returned_records = []
    for r in records:
        data = load_json_gzip_base64(r["data"])
        rec_id = r["recordId"]

        if set(("messageType", "logGroup", "owner", "logEvents")) <= data.keys():
            # If it's a Cloudwatch log record
            returned_records.append(
                process_cloudwatch_log_record(data, rec_id, firehose_arn)
            )
        elif set(("index", "sourcetype", "event")) <= data.keys():
            # Else if it's a reingested log which can skip processing
            returned_records.append(
                {"data": r["data"], "result": "Ok", "recordId": rec_id}
            )
        else:
            # Else it's an unknown log, so reject it
            returned_records.append({"result": "ProcessingFailed", "recordId": rec_id})
    return returned_records


def split_cwl_record(cwl_record):
    # TODO only CWL
    """
    Splits one CWL record into two, each containing half the log events.
    Serializes and compresses the data before returning. That data can then be
    re-ingested into the stream, and it'll appear as though they came from CWL
    directly.
    """
    logEvents = cwl_record["logEvents"]
    mid = len(logEvents) // 2
    rec1 = {k: v for k, v in cwl_record.items()}
    rec1["logEvents"] = logEvents[:mid]
    rec2 = {k: v for k, v in cwl_record.items()}
    rec2["logEvents"] = logEvents[mid:]
    return [gzip.compress(json.dumps(r).encode()) for r in [rec1, rec2]]


def put_records_to_firehose_stream(
    stream_name: str,
    records: list[dict],
    attempts_made: int = 0,
    max_attempts: int = 20,
):
    failed_records = []
    codes = []
    err_msg = ""
    # if put_record_batch throws for whatever reason, response['xx'] will error out, adding a check for a valid
    # response will prevent this
    response = None
    try:
        response = firehose_client.put_record_batch(
            DeliveryStreamName=stream_name, Records=records
        )
    except Exception as e:
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
            print(
                "Some records failed while calling Putrecord_batch to Firehose stream, retrying. %s"
                % (err_msg)
            )
            put_records_to_firehose_stream(
                stream_name, failed_records, attempts_made + 1, max_attempts
            )
        else:
            raise RuntimeError(
                "Could not put records after %s attempts. %s"
                % (str(max_attempts), err_msg)
            )


def create_reingestion_record(original_record, data=None):
    if data is None:
        data = base64.b64decode(original_record["data"])
    r = {"Data": data}
    return r


def lambda_handler(event, _context):
    firehose_arn = event["deliveryStreamArn"]
    stream_name = firehose_arn.split("/")[1]

    records = process_records(event["records"], firehose_arn)
    projected_size = 0
    record_lists_to_reingest = []

    for idx, rec in enumerate(records):
        original_record = event["records"][idx]

        if rec["result"] != "Ok":
            continue

        # If a single record is too large after processing, split the original CWL data into two, each containing half
        # the log events, and re-ingest both of them (note that it is the original data that is re-ingested, not the
        # processed data). If it's not possible to split because there is only one log event, then mark the record as
        # ProcessingFailed, which sends it to error output.

        # If the record is greater than 6MB
        if len(rec["data"]) > 6_000_000:
            # Reload original data
            cwl_record = load_json_gzip_base64(original_record["data"])
            # If there is more than one log event, split log events in half and re-process - seems overkill TODO
            if len(cwl_record["logEvents"]) > 1:
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
                print(
                    (
                        "Record %s contains only one log event but is still too large after processing (%d bytes), "
                        + "marking it as %s"
                    )
                    % (rec["recordId"], len(rec["data"]), rec["result"])
                )
            del rec["data"]
        else:
            # If the record is less than 6MB,
            projected_size += len(rec["data"]) + len(rec["recordId"])
            # 6000000 instead of 6291456 to leave ample headroom for the stuff we didn't account for
            if projected_size > 6000000:
                record_lists_to_reingest.append(
                    [create_reingestion_record(original_record)]
                )
                del rec["data"]
                rec["result"] = "Dropped"

    # call putrecord_batch/putRecords for each group of up to 500 records to be re-ingested
    if record_lists_to_reingest:
        records_reingested_so_far = 0
        max_batch_size = 500
        flattened_list = [r for sublist in record_lists_to_reingest for r in sublist]
        for i in range(0, len(flattened_list), max_batch_size):
            record_batch = flattened_list[i : i + max_batch_size]
            # last argument is maxAttempts
            put_records_to_firehose_stream(stream_name, record_batch)
            records_reingested_so_far += len(record_batch)
            print("Reingested %d/%d" % (records_reingested_so_far, len(flattened_list)))

    print(
        "%d input records, %d returned as Ok or ProcessingFailed, %d split and re-ingested, %d re-ingested as-is"
        % (
            len(event["records"]),
            len([r for r in records if r["result"] != "Dropped"]),
            len([l for l in record_lists_to_reingest if len(l) > 1]),
            len([l for l in record_lists_to_reingest if len(l) == 1]),
        )
    )

    return {"records": records}
