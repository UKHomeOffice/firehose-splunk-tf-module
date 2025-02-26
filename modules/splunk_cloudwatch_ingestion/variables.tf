#
# General
#
variable "account_id" {
  description = "The aws account id where the firehose is hosted."
}

variable "region" {
  description = "the AWS region where the firehose is running"
}

variable "environment_prefix_variable" {
  description = "Envirment prefix provided by the importing module in order to ensure resources have unique names."
}

variable "tags" {
  description = "A map of additional tags to associate with the resource"
  type        = map(string)
  default     = {}
}

#
# Splunk 
#
variable "hec_token" {
  description = "splunk hec token for the index which logs should be forwarded to."
}

variable "hec_url" {
  description = "Splunk Kinesis URL for submitting CloudWatch logs to splunk"
}

variable "hec_acknowledgment_timeout" {
  description = "The amount of time, in seconds between 180 and 600, that Kinesis Firehose waits to receive an acknowledgment from Splunk after it sends it data."
  default     = 300
}

#
# Firehose
#
variable "firehose_role_name" {
  description = "Name of IAM Role for the Kinesis Firehose"
  default     = "cw2splunk-fh-role"
}

variable "firehose_buffer" {
  description = "https://www.terraform.io/docs/providers/aws/r/kinesis_firehose_delivery_stream.html#buffer_size"
  default     = 1 # Megabytes
}

variable "firehose_buffer_interval" {
  description = "Buffer incoming data for the specified period of time, in seconds, before delivering it to the destination"
  default     = 60 # Seconds
}

variable "firehose_transform_buffer" {
  description = "https://www.terraform.io/docs/providers/aws/r/kinesis_firehose_delivery_stream.html#buffer_size"
  default     = 0.25 # Megabytes
}

variable "firehose_transform_buffer_interval" {
  description = "Buffer incoming data for the specified period of time, in seconds, before delivering it to the destination"
  default     = 60 # Seconds
}

variable "firehose_retry_duration" {
  description = "How long Kinesis Data Firehose retries sending data to Splunk"
  default     = 60
}

variable "firehose_log_group_name" {
  description = "Name of the CloudWatch log group for Kinesis Firehose"
  default     = "cw2splunk-log-group"
}

variable "firehose_log_stream_name" {
  description = "Name of the CloudWatch log stream for Kinesis Firehose CloudWatch log group"
  default     = "cw2splunk-logs"
}

variable "firehose_log_retention" {
  description = "Log retention for the firehose cloudwatch logs"
  default     = 30
}

#
# S3
#
variable "s3_kms_key_arn" {
  description = "KMS Key ARN used to protect the S3 bucket."
}

variable "s3_config_file_key" {
  description = "Location of the key to find the config file in S3."
}

variable "s3_bucket_name" {
  description = "The name of the bucket in which logs are stored when they fail being sent to splunk."
}

variable "s3_bucket_arn" {
  description = "The arn of the bucket in which logs are stored when they fail being sent to splunk."
}

variable "s3_retries_prefix" {
  description = "Prefix to store failed Firehose logs that need reingesting."
  default     = "retries/"
}

variable "s3_failed_prefix" {
  description = "Prefix to store failed Firehose logs that failed to be reingested."
  default     = "failed/"
}

#
# Lambda Functions
#
variable "python_runtime" {
  description = "Runtime version of python for Lambda functions"
  default     = "python3.12"
}
variable "lambda_log_retention" {
  description = "Log retention for the lambda cloudwatch logs"
  default     = 30
}

# Transformation Lambda
variable "transformation_lambda_name" {
  description = "Name of Lambda function responsible for parsing messages heading to splunk"
  default     = "cw2splunk-transformation-lambda"
}
variable "transformation_lambda_timeout" {
  description = "The function execution time at which Lambda should terminate the function."
  default     = 900
}
variable "transformation_lambda_memory_size" {
  description = "The function execution memory limit at which Lambda should terminate the function."
  default     = 512
}

# Reingestion Lambda
variable "reingestion_lambda_name" {
  description = "Name of Lambda function to try reingesting logs back into firehose"
  default     = "cw2splunk-reingestion-lambda"
}
variable "reingestion_lambda_timeout" {
  description = "The function execution time at which Lambda should terminate the function."
  default     = 900
}
variable "reingestion_lambda_memory_size" {
  description = "The function execution memory limit at which Lambda should terminate the function."
  default     = 512
}

# Process Failures Lambda
variable "process_failures_lambda_name" {
  description = "Name of Lambda function to process any failures"
  default     = "cw2splunk-process-failures-lambda"
}
variable "process_failures_lambda_timeout" {
  description = "The function execution time at which Lambda should terminate the function."
  default     = 900
}
variable "process_failures_lambda_memory_size" {
  description = "The function execution memory limit at which Lambda should terminate the function."
  default     = 256
}

#
# Alerting
#
variable "alerts_sns_topic_name" {
  description = "Name of SNS topic to send alerts to"
  default     = "cw2splunk-alerts-sns"
}
variable "alerts_subscription_emails" {
  description = "List of emails for people who need to be aware when a log event is moved ot the /failed prefix of the s3 bucket."
  default     = []
  type        = list(string)
}

#
# SQS Queues
#
variable "retry_sqs_name" {
  description = "Name of SQS queue that reingestion events get sent to"
  default     = "cw2splunk-retry-sqs"
}

variable "retry_dlq_name" {
  description = "Name of SQS DLQ queue that events get sent to if the reingestion lambda breaks"
  default     = "cw2splunk-retry-dlq"
}

#
# KMS Key
#
variable "kms_key_name" {
  description = "Name of KMS key for the Kinesis Firehose"
  default     = "cw2splunk-key"
}
