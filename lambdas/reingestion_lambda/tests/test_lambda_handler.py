"""MBTP Splunk Cloudwatch Reingestion Lambda Tests"""

import base64
import gzip
import io
import json
from os import environ
from unittest import mock

import boto3
import botocore
import pytest
from botocore.response import StreamingBody
from botocore.stub import Stubber
from src.mbtp_splunk_cloudwatch_reingestion.handler import (
    add_log_to_output_list,
    check_required_env_vars,
    get_logs_from_record,
    get_s3_lines,
    lambda_handler,
    get_records_from_s3,
    send_to_firehose,
    send_to_s3,
    does_file_exist,
)

REGION = environ["AWS_REGION"]
STREAM_NAME = environ["STREAM_NAME"]


test_json_events = [
    '{"foo1": "bar1"}\n{"foo12": "bar12"}',
    '{"foo2": "bar2"}',
    '{"foo3": "bar3", "fields": {"firehose_errors": 3}}',
]


def test_get_records_from_s3_splunk_failed(mocker):
    encoded_message = "\n".join(
        json.dumps({"rawData": base64.b64encode(x.encode()).decode()})
        for x in test_json_events
    ).encode()

    mocked_s3_client = boto3.client("s3", region_name=environ["AWS_REGION"])
    s3_stubber = Stubber(mocked_s3_client)

    s3_stubber.add_response(
        "get_object",
        {"Body": StreamingBody(io.BytesIO(encoded_message), len(encoded_message))},
        {
            "Bucket": "TEST_BUCKET",
            "Key": "retries/splunk-failed/TEST_KEY",
            "VersionId": "TEST_VERSION_ID",
        },
    )
    s3_stubber.activate()

    mocker.patch(
        "src.mbtp_splunk_cloudwatch_reingestion.handler.s3_client",
        new=mocked_s3_client,
    )
    results = get_records_from_s3(
        "TEST_BUCKET", "retries/splunk-failed/TEST_KEY", "TEST_VERSION_ID"
    )

    assert results == test_json_events


def test_get_records_from_s3_processing_failed(mocker):
    encoded_message = "\n".join(
        json.dumps({"rawData": base64.b64encode(gzip.compress(x.encode())).decode()})
        for x in test_json_events
    ).encode()

    mocked_s3_client = boto3.client("s3", region_name=environ["AWS_REGION"])
    s3_stubber = Stubber(mocked_s3_client)

    s3_stubber.add_response(
        "get_object",
        {"Body": StreamingBody(io.BytesIO(encoded_message), len(encoded_message))},
        {
            "Bucket": "TEST_BUCKET",
            "Key": "retries/processing-failed/TEST_KEY",
            "VersionId": "TEST_VERSION_ID",
        },
    )
    s3_stubber.activate()

    mocker.patch(
        "src.mbtp_splunk_cloudwatch_reingestion.handler.s3_client",
        new=mocked_s3_client,
    )
    results = get_records_from_s3(
        "TEST_BUCKET", "retries/processing-failed/TEST_KEY", "TEST_VERSION_ID"
    )

    assert results == test_json_events


def test_get_logs_from_record():
    assert get_logs_from_record(test_json_events[0]) == [
        {"foo1": "bar1"},
        {"foo12": "bar12"},
    ]
    assert get_logs_from_record(test_json_events[1]) == [
        {"foo2": "bar2"},
    ]
    assert get_logs_from_record(test_json_events[2]) == [
        {"foo3": "bar3", "fields": {"firehose_errors": 3}},
    ]


def test_add_log_to_output_list():
    data_to_firehose = []
    data_to_s3 = []
    add_log_to_output_list({"foo1": "bar1"}, data_to_firehose, data_to_s3)
    add_log_to_output_list({"foo2": "bar2", "fields": {}}, data_to_firehose, data_to_s3)
    add_log_to_output_list(
        {"foo3": "bar3", "fields": {"firehose_errors": 3}}, data_to_firehose, data_to_s3
    )

    assert data_to_firehose == [
        {"foo1": "bar1", "fields": {"firehose_errors": 1}},
        {"foo2": "bar2", "fields": {"firehose_errors": 1}},
    ]
    assert data_to_s3 == [{"foo3": "bar3", "fields": {"firehose_errors": 4}}]


def test_get_s3_lines():
    data = [
        {"foo1": "bar1", "fields": {"firehose_errors": 4}},
        {"foo3": "bar3", "fields": {"firehose_errors": 4}},
    ]
    result = get_s3_lines(data)

    for i, entry in enumerate(result):
        assert (
            json.loads(gzip.decompress(base64.b64decode(json.loads(entry)["rawData"])))
            == data[i]
        )


def test_send_to_s3(mocker):
    mocked_s3_client = boto3.client("s3", region_name=environ["AWS_REGION"])
    s3_stubber = Stubber(mocked_s3_client)

    s3_stubber.add_response(
        "put_object",
        {},
        {
            "Body": mock.ANY,
            "Bucket": "TEST_BUCKET",
            "Key": "retries/TEST_KEY",
        },
    )
    s3_stubber.activate()

    mocker.patch(
        "src.mbtp_splunk_cloudwatch_reingestion.handler.s3_client",
        new=mocked_s3_client,
    )

    send_to_s3(
        [
            {"foo1": "bar1", "fields": {"firehose_errors": 4}},
            {"foo3": "bar3", "fields": {"firehose_errors": 4}},
        ],
        "TEST_BUCKET",
        "retries/TEST_KEY",
    )


def test_send_to_firehose_log_too_big():
    # Record too big
    data_to_firehose = [{"foo": "bar"}]
    data_to_s3 = []
    send_to_firehose(data_to_firehose, data_to_s3, max_record_size=1)
    assert data_to_s3 == data_to_firehose


def test_send_to_firehose_split_max_records(mocker):
    mocked_firehose_client = boto3.client("firehose", region_name=environ["AWS_REGION"])
    firehose_stubber = Stubber(mocked_firehose_client)

    firehose_stubber.add_response(
        "put_record_batch",
        {"FailedPutCount": 0, "RequestResponses": [{}, {}]},
        {
            "DeliveryStreamName": STREAM_NAME,
            "Records": [
                {"Data": mock.ANY},
                {"Data": mock.ANY},
            ],
        },
    )
    firehose_stubber.add_response(
        "put_record_batch",
        {"FailedPutCount": 0, "RequestResponses": [{}, {}]},
        {
            "DeliveryStreamName": STREAM_NAME,
            "Records": [{"Data": mock.ANY}],
        },
    )
    firehose_stubber.activate()
    mocker.patch(
        "src.mbtp_splunk_cloudwatch_reingestion.handler.firehose_client",
        new=mocked_firehose_client,
    )

    data_to_firehose = [{"foo": "bar"}, {"foo2": "bar2"}, {"foo3": "bar3"}]
    data_to_s3 = []
    send_to_firehose(data_to_firehose, data_to_s3, max_records=2)


def test_send_to_firehose_split_max_request_size(mocker):
    mocked_firehose_client = boto3.client("firehose", region_name=environ["AWS_REGION"])
    firehose_stubber = Stubber(mocked_firehose_client)

    firehose_stubber.add_response(
        "put_record_batch",
        {"FailedPutCount": 0, "RequestResponses": [{}, {}]},
        {
            "DeliveryStreamName": STREAM_NAME,
            "Records": [
                {"Data": mock.ANY},
                {"Data": mock.ANY},
            ],
        },
    )
    firehose_stubber.add_response(
        "put_record_batch",
        {"FailedPutCount": 0, "RequestResponses": [{}, {}]},
        {
            "DeliveryStreamName": STREAM_NAME,
            "Records": [{"Data": mock.ANY}],
        },
    )
    firehose_stubber.activate()
    mocker.patch(
        "src.mbtp_splunk_cloudwatch_reingestion.handler.firehose_client",
        new=mocked_firehose_client,
    )

    data_to_firehose = [{"foo": "bar"}, {"foo2": "bar2"}, {"foo3": "bar3"}]
    data_to_s3 = []
    send_to_firehose(data_to_firehose, data_to_s3, max_request_size=185 * 2)


def test_push_to_firehose_failures(mocker):
    mocked_firehose_client = boto3.client("firehose", region_name=environ["AWS_REGION"])
    firehose_stubber = Stubber(mocked_firehose_client)
    firehose_stubber.add_response(
        "put_record_batch",
        {"FailedPutCount": 1, "RequestResponses": [{"ErrorCode": "blah"}, {}, {}]},
        {
            "DeliveryStreamName": STREAM_NAME,
            "Records": [
                {"Data": mock.ANY},
                {"Data": mock.ANY},
                {"Data": mock.ANY},
            ],
        },
    )
    for _ in range(0, 19):
        firehose_stubber.add_response(
            "put_record_batch",
            {"FailedPutCount": 1, "RequestResponses": [{"ErrorCode": "blah"}, {}, {}]},
            {
                "DeliveryStreamName": STREAM_NAME,
                "Records": [
                    {"Data": mock.ANY},
                ],
            },
        )
    firehose_stubber.activate()
    mocker.patch(
        "src.mbtp_splunk_cloudwatch_reingestion.handler.firehose_client",
        new=mocked_firehose_client,
    )

    data_to_firehose = [{"foo": "bar"}, {"foo2": "bar2"}, {"foo3": "bar3"}]
    data_to_s3 = []
    send_to_firehose(data_to_firehose, data_to_s3)
    assert data_to_s3 == [{"foo": "bar"}]


def test_push_to_firehose_errored(mocker):
    mocked_firehose_client = boto3.client("firehose", region_name=environ["AWS_REGION"])
    firehose_stubber = Stubber(mocked_firehose_client)
    for _ in range(0, 20):
        firehose_stubber.add_client_error("put_record_batch")

    firehose_stubber.activate()
    mocker.patch(
        "src.mbtp_splunk_cloudwatch_reingestion.handler.firehose_client",
        new=mocked_firehose_client,
    )

    data_to_firehose = [{"foo": "bar"}, {"foo2": "bar2"}, {"foo3": "bar3"}]
    data_to_s3 = []
    send_to_firehose(data_to_firehose, data_to_s3)
    assert data_to_s3 == data_to_firehose


def test_does_file_exist_exists(mocker):
    mocked_s3_client = boto3.client("s3", region_name=environ["AWS_REGION"])
    s3_stubber = Stubber(mocked_s3_client)
    s3_stubber.add_response(
        "head_object",
        {},
        {
            "Bucket": "TEST_BUCKET",
            "Key": "retries/TEST_KEY",
            "VersionId": "TEST_VERSION_ID",
        },
    )
    s3_stubber.activate()
    mocker.patch(
        "src.mbtp_splunk_cloudwatch_reingestion.handler.s3_client",
        new=mocked_s3_client,
    )
    assert does_file_exist("TEST_BUCKET", "retries/TEST_KEY", "TEST_VERSION_ID") == True


def test_does_file_exist_not_exists(mocker):
    mocked_s3_client = boto3.client("s3", region_name=environ["AWS_REGION"])
    s3_stubber = Stubber(mocked_s3_client)
    s3_stubber.add_client_error("head_object", "404", http_status_code=404)
    s3_stubber.activate()
    mocker.patch(
        "src.mbtp_splunk_cloudwatch_reingestion.handler.s3_client",
        new=mocked_s3_client,
    )
    assert (
        does_file_exist("TEST_BUCKET", "retries/TEST_KEY", "TEST_VERSION_ID") == False
    )


def test_does_file_exist_error(mocker):
    mocked_s3_client = boto3.client("s3", region_name=environ["AWS_REGION"])
    s3_stubber = Stubber(mocked_s3_client)
    s3_stubber.add_client_error("head_object", "500", http_status_code=500)
    s3_stubber.activate()
    mocker.patch(
        "src.mbtp_splunk_cloudwatch_reingestion.handler.s3_client",
        new=mocked_s3_client,
    )
    with pytest.raises(botocore.exceptions.ClientError):
        does_file_exist("TEST_BUCKET", "retries/TEST_KEY", "TEST_VERSION_ID")


def test_handler(mocker):
    """Test to check that handler functions without error and calls the correct AWS APIs"""

    encoded_message = "\n".join(
        json.dumps({"rawData": base64.b64encode(x.encode()).decode()})
        for x in test_json_events
    ).encode()

    test_event = {
        "Records": [
            {
                "body": json.dumps(
                    {
                        "Records": [
                            {
                                "s3": {
                                    "bucket": {"name": "TEST_BUCKET"},
                                    "object": {
                                        "key": "retries/splunk-failed/TEST_KEY",
                                        "versionId": "TEST_VERSION_ID",
                                    },
                                }
                            },
                            {
                                "s3": {
                                    "bucket": {"name": "TEST_BUCKET"},
                                    "object": {
                                        "key": "retries/splunk-failed/NOT_EXIST",
                                        "versionId": "NOT_EXIST",
                                    },
                                }
                            },
                        ]
                    }
                )
            }
        ]
    }

    # Create mocked clients
    mocked_s3_client = boto3.client("s3", region_name=environ["AWS_REGION"])
    s3_stubber = Stubber(mocked_s3_client)
    mocked_firehose_client = boto3.client("firehose", region_name=environ["AWS_REGION"])
    firehose_stubber = Stubber(mocked_firehose_client)

    s3_stubber.add_response(
        "head_object",
        {},
        {
            "Bucket": "TEST_BUCKET",
            "Key": "retries/splunk-failed/TEST_KEY",
            "VersionId": "TEST_VERSION_ID",
        },
    )
    s3_stubber.add_response(
        "get_object",
        {"Body": StreamingBody(io.BytesIO(encoded_message), len(encoded_message))},
        {
            "Bucket": "TEST_BUCKET",
            "Key": "retries/splunk-failed/TEST_KEY",
            "VersionId": "TEST_VERSION_ID",
        },
    )
    s3_stubber.add_response(
        "put_object",
        {},
        {
            "Body": mock.ANY,
            "Bucket": "TEST_BUCKET",
            "Key": "failed/splunk-failed/TEST_KEY",
        },
    )
    s3_stubber.add_response(
        "delete_object",
        {},
        {
            "Bucket": "TEST_BUCKET",
            "Key": "retries/splunk-failed/TEST_KEY",
            "VersionId": "TEST_VERSION_ID",
        },
    )
    s3_stubber.add_client_error("head_object", "404", http_status_code=404)

    s3_stubber.activate()

    firehose_stubber.add_response(
        "put_record_batch",
        {"FailedPutCount": 0, "RequestResponses": [{}, {}]},
        {
            "DeliveryStreamName": STREAM_NAME,
            "Records": [
                {"Data": mock.ANY},
                {"Data": mock.ANY},
                {"Data": mock.ANY},
            ],
        },
    )
    firehose_stubber.activate()

    mocker.patch(
        "src.mbtp_splunk_cloudwatch_reingestion.handler.s3_client",
        new=mocked_s3_client,
    )
    mocker.patch(
        "src.mbtp_splunk_cloudwatch_reingestion.handler.firehose_client",
        new=mocked_firehose_client,
    )
    # Call the main handler function
    lambda_handler(test_event, {})


def test_missing_env_vars():
    """Test to check that a missing env var throws an error."""
    del environ["AWS_REGION"]
    with pytest.raises(EnvironmentError):
        check_required_env_vars()
    environ["AWS_REGION"] = "eu-west-1"
