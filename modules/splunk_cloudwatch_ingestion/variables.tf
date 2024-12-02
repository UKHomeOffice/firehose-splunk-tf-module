variable "hec_url" {
  description = "Splunk Kinesis URL for submitting CloudWatch logs to splunk"
}

variable "python_runtime" {
  description = "Runtime version of python for Lambda function"
  default     = "python3.12"
}

variable "kinesis_firehose_buffer" {
  description = "https://www.terraform.io/docs/providers/aws/r/kinesis_firehose_delivery_stream.html#buffer_size"
  default     = 1 # Megabytes
}

variable "kinesis_firehose_transform_buffer" {
  description = "https://www.terraform.io/docs/providers/aws/r/kinesis_firehose_delivery_stream.html#buffer_size"
  default     = 0.25 # Megabytes
}

variable "kinesis_firehose_buffer_interval" {
  description = "Buffer incoming data for the specified period of time, in seconds, before delivering it to the destination"
  default     = 60 # Seconds
}

variable "kinesis_firehose_transform_buffer_interval" {
  description = "Buffer incoming data for the specified period of time, in seconds, before delivering it to the destination"
  default     = 60 # Seconds
}

variable "hec_acknowledgment_timeout" {
  description = "The amount of time, in seconds between 180 and 600, that Kinesis Firehose waits to receive an acknowledgment from Splunk after it sends it data."
  default     = 300
}

variable "hec_endpoint_type" {
  description = "Splunk HEC endpoint type; `Raw` or `Event`"
  default     = "Event"
}

variable "retry_duration" {
  description = "How long Kinesis Data Firehose retries sending data to Splunk"
  default     = "60"
}

variable "s3_backup_mode" {
  description = "Defines how documents should be delivered to Amazon S3. Valid values are FailedEventsOnly and AllEvents."
  default     = "FailedEventsOnly"
}

variable "enable_fh_cloudwatch_logging" {
  description = "Enable kinesis firehose CloudWatch logging. (It only logs errors)"
  default     = true
}

variable "log_stream_name" {
  description = "Name of the CloudWatch log stream for Kinesis Firehose CloudWatch log group"
  default     = "SplunkDelivery"
}

variable "kinesis_firehose_role_name" {
  description = "Name of IAM Role for the Kinesis Firehose"
  default     = "SplunkKinesisFHRole"
}

variable "transform_lambda_function_timeout" {
  description = "The function execution time at which Lambda should terminate the function."
  default     = 900
}

variable "transform_lambda_transform_memory_size" {
  description = "The function execution memory limit at which Lambda should terminate the function."
  default     = 1536
}

variable "retry_lambda_function_timeout" {
  description = "The function execution time at which Lambda should terminate the function."
  default     = 900
}

variable "retry_lambda_transform_memory_size" {
  description = "The function execution memory limit at which Lambda should terminate the function."
  default     = 1536
}

variable "failed_lambda_function_timeout" {
  description = "The function execution time at which Lambda should terminate the function."
  default     = 900
}

variable "failed_lambda_transform_memory_size" {
  description = "The function execution memory limit at which Lambda should terminate the function."
  default     = 1536
}

variable "kinesis_firehose_iam_policy_name" {
  description = "Name of the IAM Policy attached to IAM Role for the Kinesis Firehose"
  default     = "KinesisFH-Policy"
}

variable "firehose_failures_bucket_name" {
  description = "The name of the bucket in which logs are stored when they fail being sent to splunk."
  default     = ""
}

variable "firehose_failures_bucket_arn" {
  description = "The arn of the bucket in which logs are stored when they fail being sent to splunk."
  default     = ""
}

variable "splunk_hec_token" {
  description = "splunk hec token for the index which logs should be forwarded to."
}

variable "sns_failed_splunk_subscription_emails" {
  description = "List of emails for people who need to be aware when a log event is moved ot the /failed prefix of the s3 bucket."
  default     = []
  type        = list(string)
}

variable "environment_prefix_variable" {
  description = "Envirment prefix provided by the importing module in order to ensure resources have unique names."
}

variable "region" {
  description = "the AWS region where the firehose is running"
}

variable "tags" {
  description = "A map of additional tags to associate with the resource"
  type        = map(string)
  default     = {}
}

variable "account_id" {
  description = "The aws account id where the firehose is hosted."
}

variable "s3_retries_prefix" {
  description = "Prefix to store failed Firehose logs that need reingesting."
  default     = "retries/"
}
variable "s3_failed_prefix" {
  description = "Prefix to store failed Firehose logs that failed to be reingested."
  default     = "failed/"
}
variable "s3_kms_key_arn" {
  description = "KMS Key ARN used to protect the S3 bucket."
}
variable "s3_config_file_key" {
  description = "Location of the key to find the config file in S3."
}
