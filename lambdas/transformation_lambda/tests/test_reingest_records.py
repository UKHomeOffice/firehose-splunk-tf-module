from unittest import mock

import pytest
from src.mbtp_splunk_cloudwatch_transformation.handler import reingest_records
from os import environ
import boto3

from botocore.stub import Stubber


records = [
    [
        {"Data": "1"},
        {"Data": "2"},
    ],
    [{"Data": "3"}],
]


def test_reingest_records_failures(mocker):
    mocked_firehose_client = boto3.client("firehose", region_name=environ["AWS_REGION"])
    firehose_stubber = Stubber(mocked_firehose_client)
    firehose_stubber.add_response(
        "put_record_batch",
        {"FailedPutCount": 1, "RequestResponses": [{"ErrorCode": "blah"}, {}]},
        {
            "DeliveryStreamName": "STREAM_NAME",
            "Records": [
                {"Data": "1"},
                {"Data": "2"},
            ],
        },
    )
    firehose_stubber.add_response(
        "put_record_batch",
        {"FailedPutCount": 0, "RequestResponses": [{}]},
        {
            "DeliveryStreamName": "STREAM_NAME",
            "Records": [
                {"Data": "1"},
            ],
        },
    )
    firehose_stubber.add_response(
        "put_record_batch",
        {"FailedPutCount": 0, "RequestResponses": [{}]},
        {
            "DeliveryStreamName": "STREAM_NAME",
            "Records": [
                {"Data": "3"},
            ],
        },
    )

    firehose_stubber.activate()
    mocker.patch(
        "src.mbtp_splunk_cloudwatch_transformation.handler.firehose_client",
        new=mocked_firehose_client,
    )
    reingest_records(records, "STREAM_NAME", 2)


def test_reingest_records_errored(mocker):
    mocked_firehose_client = boto3.client("firehose", region_name=environ["AWS_REGION"])
    firehose_stubber = Stubber(mocked_firehose_client)
    for _ in range(0, 20):
        firehose_stubber.add_client_error("put_record_batch")

    firehose_stubber.activate()
    mocker.patch(
        "src.mbtp_splunk_cloudwatch_transformation.handler.firehose_client",
        new=mocked_firehose_client,
    )
    with pytest.raises(RuntimeError):
        reingest_records(records, "STREAM_NAME")
