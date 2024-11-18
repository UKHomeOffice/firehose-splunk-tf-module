from src.mbtp_splunk_cloudwatch_process_failures.handler import handler
from os import environ

BUCKET = environ["S3_BUCKET_NAME"]
REGION = environ["AWS_REGION"]

import boto3
from botocore.stub import Stubber


def test_get_item(mocker):
    mocked_sqs_client = boto3.client("sqs", region_name=environ["AWS_REGION"])
    sqs_stubber = Stubber(mocked_sqs_client)
    mocked_s3_client = boto3.client("s3", region_name=environ["AWS_REGION"])
    s3_stubber = Stubber(mocked_s3_client)

    sqs_stubber.add_response(
        "start_message_move_task",
        {"TaskHandle": "test"},
        {"SourceArn": "SQS_QUEUE_ARN", "DestinationArn": "DLQ_QUEUE_ARN"},
    )
    sqs_stubber.activate()

    s3_stubber.add_response(
        "list_objects_v2",
        {
            "IsTruncated": True,
            "Contents": [
                {"Key": "failed/testfile"},
                {"Key": "failed/testfile2"},
            ],
        },
        {"Bucket": BUCKET, "Prefix": "failed/"},
    )
    s3_stubber.add_response(
        "copy_object",
        {},
        {
            "Bucket": BUCKET,
            "Key": "retries/testfile",
            "CopySource": {"Bucket": BUCKET, "Key": "failed/testfile"},
        },
    )
    s3_stubber.add_response(
        "delete_object",
        {},
        {
            "Bucket": BUCKET,
            "Key": "failed/testfile",
        },
    )
    s3_stubber.add_response(
        "copy_object",
        {},
        {
            "Bucket": BUCKET,
            "Key": "retries/testfile2",
            "CopySource": {"Bucket": BUCKET, "Key": "failed/testfile2"},
        },
    )
    s3_stubber.add_response(
        "delete_object",
        {},
        {
            "Bucket": BUCKET,
            "Key": "failed/testfile2",
        },
    )
    s3_stubber.add_response(
        "list_objects_v2",
        {
            "IsTruncated": False,
            "Contents": [
                {"Key": "failed/testfile3"},
            ],
        },
        {"Bucket": BUCKET, "Prefix": "failed/"},
    )
    s3_stubber.add_response(
        "copy_object",
        {},
        {
            "Bucket": BUCKET,
            "Key": "retries/testfile",
            "CopySource": {"Bucket": BUCKET, "Key": "failed/testfile3"},
        },
    )
    s3_stubber.add_response(
        "delete_object",
        {},
        {
            "Bucket": BUCKET,
            "Key": "failed/testfile3",
        },
    )
    s3_stubber.activate()

    mocker.patch(
        "src.mbtp_splunk_cloudwatch_process_failures.handler.sqs_client",
        new=mocked_sqs_client,
    )
    mocker.patch(
        "src.mbtp_splunk_cloudwatch_process_failures.handler.s3_client",
        new=mocked_s3_client,
    )
    handler()
