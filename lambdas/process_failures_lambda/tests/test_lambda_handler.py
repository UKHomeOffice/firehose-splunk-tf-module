"""MBTP Splunk Cloudwatch Process Failures Lambda Tests"""

from os import environ

import boto3
from botocore.stub import Stubber
import pytest
from src.mbtp_splunk_cloudwatch_process_failures.handler import (
    check_required_env_vars,
    handler,
)

BUCKET = environ["S3_BUCKET_NAME"]
REGION = environ["AWS_REGION"]


def test_handler(mocker):
    """Test to check that handler functions without error and calls the correct AWS APIs"""
    # Create mocked clients
    mocked_sqs_client = boto3.client("sqs", region_name=environ["AWS_REGION"])
    sqs_stubber = Stubber(mocked_sqs_client)
    mocked_s3_client = boto3.client("s3", region_name=environ["AWS_REGION"])
    s3_stubber = Stubber(mocked_s3_client)

    # Add a mocked response for start_message_move_task
    sqs_stubber.add_response(
        "start_message_move_task",
        {"TaskHandle": "test"},
        {"SourceArn": "SQS_QUEUE_ARN", "DestinationArn": "DLQ_QUEUE_ARN"},
    )
    sqs_stubber.activate()

    # Simulate a bucket with 4 test files returned as 2 pages of results
    files_to_mock = [
        ["failed/testfile", "failed/testfile2"],
        ["failed/testfile3", "failed/testfile4"],
    ]

    for i, page in enumerate(files_to_mock):
        expected_params = {"Bucket": BUCKET, "Prefix": "failed/"}
        if i != 0:
            expected_params["ContinuationToken"] = str(i)

        # Mock the list_objects_v2 response (one per page)
        s3_stubber.add_response(
            "list_objects_v2",
            {
                "IsTruncated": True if i != len(page) - 1 else False,
                "Contents": [{"Key": file} for file in page],
                "Name": BUCKET,
                "Prefix": "failed/",
                "MaxKeys": 10,
                "KeyCount": len(page),
                "ContinuationToken": str(i),
                "NextContinuationToken": str(i + 1),
            },
            expected_params,
        )
        for file in page:
            # For each file in the page, mock the copy and delete calls
            s3_stubber.add_response(
                "copy_object",
                {},
                {
                    "Bucket": BUCKET,
                    "Key": file.replace("failed/", "retries/"),
                    "CopySource": {"Bucket": BUCKET, "Key": file},
                },
            )
            s3_stubber.add_response(
                "delete_object",
                {},
                {
                    "Bucket": BUCKET,
                    "Key": file,
                },
            )

    s3_stubber.activate()

    # Replace the clients in the code with our mocked ones
    mocker.patch(
        "src.mbtp_splunk_cloudwatch_process_failures.handler.sqs_client",
        new=mocked_sqs_client,
    )
    mocker.patch(
        "src.mbtp_splunk_cloudwatch_process_failures.handler.s3_client",
        new=mocked_s3_client,
    )

    # Call the main handler function
    handler()


def test_missing_env_vars():
    """Test to check that a missing env var throws an error."""
    del environ["AWS_REGION"]
    with pytest.raises(EnvironmentError):
        check_required_env_vars()
    environ["AWS_REGION"] = "eu-west-1"
