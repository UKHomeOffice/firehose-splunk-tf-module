variable "firehose_arn" {
  description = "The ARN of the Firehose delivery stream"
  type        = string
}

variable "config_s3_bucket" {
  description = "The S3 bucket where the YAML configuration file is stored"
  type        = string
}

variable "config_s3_key" {
  description = "The key (path) to the YAML configuration file in the S3 bucket"
  type        = string
}

variable "account" {
  description = "The aws account where the firehose is hosted."
}

variable "region" {
  description = "the AWS region where the firehose is running"
}