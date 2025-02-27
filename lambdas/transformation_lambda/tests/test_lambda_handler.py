"""MBTP Splunk Cloudwatch Transformation Lambda Tests"""

import base64
from os import environ
import io
import json
import re
import boto3

from botocore.stub import Stubber
from tests.test_pre_reingest import b64compress
from src.mbtp_splunk_cloudwatch_transformation.handler import (
    check_required_env_vars,
    lambda_handler,
)
import pytest

config = {
    "log_groups": {
        "TEST_LOG_GROUP": {
            "accounts": [123456789012],
            "index": "TEST_INDEX",
            "log_streams": [
                {"regex": "^TEST_LOG_STREAM$", "sourcetype": "TEST_SOURCETYPE"}
            ],
        }
    },
    "sourcetypes": {"TEST_SOURCETYPE": {}},
}
data = {
    "messageType": "DATA_MESSAGE",
    "owner": "123456789012",
    "logGroup": "TEST_LOG_GROUP",
    "logStream": "TEST_LOG_STREAM",
    "subscriptionFilters": ["subscription_filter_name"],
    "logEvents": [
        {
            "id": "01234567890123456789012345678901234567890123456789012345",
            "timestamp": 1510109208016,
            "message": "log message 1",
        },
        {
            "id": "01234567890123456789012345678901234567890123456789012345",
            "timestamp": 1510109208017,
            "message": "log message 2",
        },
    ],
}

returned = [
    {
        "index": "TEST_INDEX",
        "sourcetype": "TEST_SOURCETYPE",
        "time": 1510109208016,
        "host": "ARN/STREAM_NAME",
        "source": "TEST_LOG_GROUP",
        "fields": {
            "aws_account_id": "123456789012",
            "cw_log_stream": "TEST_LOG_STREAM",
        },
        "event": "log message 1",
    },
    {
        "index": "TEST_INDEX",
        "sourcetype": "TEST_SOURCETYPE",
        "time": 1510109208017,
        "host": "ARN/STREAM_NAME",
        "source": "TEST_LOG_GROUP",
        "fields": {
            "aws_account_id": "123456789012",
            "cw_log_stream": "TEST_LOG_STREAM",
        },
        "event": "log message 2",
    },
]


def test_handler(mocker):
    mocker.patch(
        "src.mbtp_splunk_cloudwatch_transformation.handler.CONFIG",
        new=config,
    )
    event = {
        "deliveryStreamArn": "ARN/STREAM_NAME",
        "records": [
            {"recordId": "1", "data": b64compress(data)},
        ],
    }
    assert lambda_handler(event, {}) == {
        "records": [
            {
                "result": "Ok",
                "recordId": "1",
                "data": base64.b64encode(
                    "\n".join(json.dumps(x) for x in returned).encode()
                ).decode(),
            }
        ]
    }


def test_missing_env_vars():
    """Test to check that a missing env var throws an error."""
    del environ["AWS_REGION"]
    with pytest.raises(EnvironmentError):
        check_required_env_vars()
    environ["AWS_REGION"] = "eu-west-1"
