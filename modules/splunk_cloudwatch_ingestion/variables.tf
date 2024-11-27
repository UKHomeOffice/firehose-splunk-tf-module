variable "use_regional_sts_endpoint" {
  description = "The region the resource belongs to instead of a global host"
  default     = "false"
  type        = string
}

variable "hec_url" {
  description = "Splunk Kinesis URL for submitting CloudWatch logs to splunk"
}

variable "python_runtime" {
  description = "Runtime version of python for Lambda function"
  default     = "python3.12"
}

variable "firehose_processing" {
  description = "Name of the Kinesis Firehose"
  default     = []
  type        = list(string)
}

variable "firehose_processing_elements" {
  description = "Amount of columns for firehose config variable"
  default     = 2
}

variable "cloudwatch_log_group_subscription_to_firehose" {
  description = "List of the log groups that need no data processing but need a subscription"
  default     = []
  type        = list(string)
}

variable "cloudwatch_log_group_subscription_to_firehose_elements" {
  description = "Amount of columns for firehose config variable"
  default     = 2
}

variable "kinesis_firehose_buffer" {
  description = "https://www.terraform.io/docs/providers/aws/r/kinesis_firehose_delivery_stream.html#buffer_size"
  default     = 1 # Megabytes
}

variable "kinesis_firehose_transform_buffer" {
  description = "https://www.terraform.io/docs/providers/aws/r/kinesis_firehose_delivery_stream.html#buffer_size"
  default     = 3 # Megabytes
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
  default     = "Raw"
}

variable "retry_duration" {
  description = "How long Kinesis Data Firehose retries sending data to Splunk"
  default     = "60"
}

variable "s3_backup_mode" {
  description = "Defines how documents should be delivered to Amazon S3. Valid values are FailedEventsOnly and AllEvents."
  default     = "FailedEventsOnly"
}

variable "s3_compression_format" {
  description = "The compression format for what the Kinesis Firehose puts in the s3 bucket"
  default     = "GZIP"
}

variable "enable_fh_cloudwatch_logging" {
  description = "Enable kinesis firehose CloudWatch logging. (It only logs errors)"
  default     = true
}

variable "cloudwatch_log_retention" {
  description = "Length in days to keep CloudWatch logs of Kinesis Firehose"
  default     = 30
}

variable "log_stream_name" {
  description = "Name of the CloudWatch log stream for Kinesis Firehose CloudWatch log group"
  default     = "SplunkDelivery"
}

variable "kinesis_firehose_lambda_role_name" {
  description = "Name of IAM Role for Lambda function that transforms CloudWatch data for Kinesis Firehose into Splunk compatible format"
  default     = "SplunkKinesisFHToLambdaRole"
}

variable "kinesis_firehose_reingest_lambda_role_name" {
  description = ""
  default     = "LambdaToKinesisFirehoseReingestRole"
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

variable "lambda_iam_policy_name" {
  description = "Name of the IAM policy that is attached to the IAM Role for the lambda transform function"
  default     = "Kinesis-FH-to-Splunk-Policy"
}

variable "kinesis_firehose_iam_policy_name" {
  description = "Name of the IAM Policy attached to IAM Role for the Kinesis Firehose"
  default     = "KinesisFH-Policy"
}

variable "cloudwatch_to_firehose_trust_iam_role_name" {
  description = "IAM Role name for CloudWatch to Kinesis Firehose subscription"
  default     = "CWToSplunkFHTrust"
}

variable "cloudwatch_to_fh_access_policy_name" {
  description = "Name of IAM policy attached to the IAM role for CloudWatch to Kinesis Firehose subscription"
  default     = "SplunkKinesisCWToFHPolicy"
}

variable "cloudwatch_log_filter_name" {
  description = "Name of Log Filter for CloudWatch Log subscription to Kinesis Firehose"
  default     = "SplunkFirehoseSubscriptionFilter"
}

variable "subscription_filter_pattern" {
  description = "Filter pattern for the CloudWatch Log Group subscription to the Kinesis Firehose. See [this](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/FilterAndPatternSyntax.html) for filter pattern info."
  default     = "" # nothing is being filtered
}

variable "firehose_failures_bucket_name" {
  description = "The name of the bucket in which logs are stored when they fail being sent to splunk."
  default     = ""
}

variable "firehose_failures_bucket_arn" {
  description = "The arn of the bucket in which logs are stored when they fail being sent to splunk."
  default     = ""
}

variable "firehose_failures_bucket_id" {
  description = "The id of the bucket in which logs are stored when they fail being sent to splunk."
  default     = ""
}

variable "transform_lambda_concurrency_limit" {
  description = "The number of concurrent lambdas that can run"
  default = 100
}

variable "retry_lambda_concurrency_limit" {
  description = "The number of concurrent lambdas that can run"
  default = 100
}

variable "failed_lambda_concurrency_limit" {
  description = "The number of concurrent lambdas that can run"
  default = 100
}

variable "terraform_iam_role" {
  description = "Role name for the CPT deploy agent."
  default = ""
}

variable "config_file_path" {
  description = "Path to the YAML config path"
}

variable "splunk_hec_token" {
  description = "splunk hec token for the index which logs should be forwarded to."
}

variable "transform_lambda_path" {
  description = "path to the transform lambda handler (N.B. include file name but not extention)"
  default = "../../lambdas/transformation_lambda/src/mbtp_splunk_cloudwatch_transformation"
}

variable "retry_lambda_path" {
  description = "path to the retry lambda handler (N.B. include file name but not extention)"
  default = "../../lambdas/reingestion_lambda/src/mbtp_splunk_cloudwatch_reingestion"
}

variable "failed_lambda_path" {
  description = "path to failed lambda handler (N.B. include file name but not extention)"
  default = "../../lambdas/process_failures_lambda/src/mbtp_splunk_cloudwatch_process_failures"
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