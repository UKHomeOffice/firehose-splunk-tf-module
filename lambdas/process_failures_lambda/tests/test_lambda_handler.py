"""MBTP Splunk Cloudwatch Process Failures Lambda Tests"""

from os import environ

import boto3
from botocore.stub import Stubber
import pytest
from src.mbtp_splunk_cloudwatch_process_failures.handler import (
    check_required_env_vars,
    lambda_handler,
)

REGION = environ["AWS_REGION"]


def test_handler(mocker):
    """Test to check that handler functions without error and calls the correct AWS APIs"""
    # Create mocked clients
    mocked_sqs_client = boto3.client("sqs", region_name=environ["AWS_REGION"])
    sqs_stubber = Stubber(mocked_sqs_client)

    # Add a mocked response for start_message_move_task
    sqs_stubber.add_response(
        "start_message_move_task",
        {"TaskHandle": "test"},
        {"SourceArn": "DLQ_QUEUE_ARN", "DestinationArn": "SQS_QUEUE_ARN"},
    )
    sqs_stubber.activate()

    # Replace the clients in the code with our mocked ones
    mocker.patch(
        "src.mbtp_splunk_cloudwatch_process_failures.handler.sqs_client",
        new=mocked_sqs_client,
    )

    # Call the main handler function
    lambda_handler({}, {})


def test_missing_env_vars():
    """Test to check that a missing env var throws an error."""
    del environ["AWS_REGION"]
    with pytest.raises(EnvironmentError):
        check_required_env_vars()
    environ["AWS_REGION"] = "eu-west-1"
