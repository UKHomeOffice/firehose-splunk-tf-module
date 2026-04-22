"""MBTP Splunk Cloudwatch Ingestion - Manual Process Failures Lambda"""

import logging
from os import environ

import boto3

logger = logging.getLogger()


REQUIRED_ENV_VARS = {
    "AWS_REGION",
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

sqs_client = boto3.client("sqs", region_name=REGION)


def redrive_dlq_sqs(source_arn: str, dest_arn: str):
    """Initiates a SQS redrive from a source queue to a destination queue.

    Args:
        source_arn (str): ARN of the source queue.
        dest_arn (str): ARN of the destination queue.
    """
    logger.info(f"Initiating DQL redrive from {source_arn} to {dest_arn}")
    sqs_client.start_message_move_task(SourceArn=source_arn, DestinationArn=dest_arn)


def lambda_handler(_event, _context):
    """Lambda function to re-processed any files that
    failed to be sent to Splunk after the retries."""
    redrive_dlq_sqs(environ["DLQ_QUEUE_ARN"], environ["SQS_QUEUE_ARN"])
