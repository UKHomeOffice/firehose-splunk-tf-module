"""MBTP Splunk Cloudwatch Ingestion - Manual Process Failures Lambda"""

import logging
from os import environ

import boto3

logger = logging.getLogger()
logger.setLevel(environ.get("LOG_LEVEL", "INFO"))


REQUIRED_ENV_VARS = {
    "AWS_REGION",
    "S3_BUCKET_NAME",
    "SQS_QUEUE_ARN",
    "DLQ_QUEUE_ARN",
    "RETRIES_PREFIX",
    "FAILED_PREFIX",
}


def check_required_env_vars():
    """Function to check all required environment variables exist"""
    if missing_variables := REQUIRED_ENV_VARS.difference(environ):
        raise EnvironmentError(
            f"The following environment variables need to be set: {missing_variables}"
        )


check_required_env_vars()

REGION = environ["AWS_REGION"]
RETRIES_PREFIX = environ["RETRIES_PREFIX"]
FAILED_PREFIX = environ["FAILED_PREFIX"]

s3_client = boto3.client("s3", region_name=REGION)
sqs_client = boto3.client("sqs", region_name=REGION)


def redrive_dlq_sqs(source_arn: str, dest_arn: str):
    """Initiates a SQS redrive from a source queue to a destination queue.

    Args:
        source_arn (str): ARN of the source queue.
        dest_arn (str): ARN of the destination queue.
    """
    logging.info(f"Initiating DQL redrive from {source_arn} to {dest_arn}")
    sqs_client.start_message_move_task(SourceArn=source_arn, DestinationArn=dest_arn)


def reprocess_failed_files(
    bucket_name: str,
    failed_prefix: str = FAILED_PREFIX,
    retry_prefix: str = RETRIES_PREFIX,
):
    """Moves files from the failed prefix to the retries prefix.

    Args:
        bucket_name (str): Name of the S3 bucket to do the operation on.
        failed_prefix (str, optional): Prefix of the failed folder. Defaults to "failed/".
        retry_prefix (str, optional): Prefix of the retries folder. Defaults to "retries/".
    """
    paginator = s3_client.get_paginator("list_objects_v2")
    pages = paginator.paginate(Bucket=bucket_name, Prefix=failed_prefix)

    for page in pages:
        for file in page.get("Contents", []):
            key: str = file["Key"]
            new_key = f"{retry_prefix}{key.removeprefix(failed_prefix)}"
            logging.info(f"Moving {key} to {new_key}")
            s3_client.copy_object(
                Bucket=bucket_name,
                CopySource={"Bucket": bucket_name, "Key": key},
                Key=new_key,
            )
            s3_client.delete_object(Bucket=bucket_name, Key=key)


def lambda_handler(_event, _context):
    """Lambda function to re-processed any files that
    failed to be sent to Splunk after the retries."""
    redrive_dlq_sqs(environ["DLQ_QUEUE_ARN"], environ["SQS_QUEUE_ARN"])
    reprocess_failed_files(environ["S3_BUCKET_NAME"])
