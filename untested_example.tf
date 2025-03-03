provider "aws" {}
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

locals {
  account_id                  = data.aws_caller_identity.current.account_id
  region                      = data.aws_region.current.name
  config_file                 = "./untested_example_config.yaml"
  environment_prefix_variable = "example"
  bucket_name                 = "EXAMPLE_BUCKET_NAME"
  bucket_arn                  = "EXAMPLE_BUCKET_ARN"
  bucket_kms_arn              = "EXAMPLE_BUCKET_KEY_ARN"
}

# S3 module
# NOTE: Although we provide a module for creating a S3 bucket, 
# we recommend using your own bucket creation templates.
# module "bucket" {
#   source                      = "./modules/s3_bucket"
#   bucket_name                 = local.bucket_name
#   approved_s3_resources       = []
#   account_id                  = local.account_id
#   environment_prefix_variable = local.environment_prefix_variable
# }

# Upload the config file to the bucket
resource "aws_s3_object" "config_upload" {
  bucket = local.bucket_name
  key    = "config.yaml"
  source = local.config_file
  etag   = filemd5(local.config_file)
}

# Splunk Cloudwatch Ingestion module
module "firehose" {
  source                      = "./modules/splunk_cloudwatch_ingestion"
  environment_prefix_variable = local.environment_prefix_variable
  s3_bucket_name              = local.bucket_name
  s3_bucket_arn               = local.bucket_arn
  hec_token                   = "EXAMPLE_HEC_TOKEN"
  hec_url                     = "EXAMPLE_HEC_URL"
  alerts_subscription_emails  = ["EXAMPLE_ALERTS_EMAIL_ADDRESS"]
  region                      = local.region
  account_id                  = local.account_id
  s3_config_file_key          = aws_s3_object.config_upload.key
  s3_kms_key_arn              = local.bucket_kms_arn
}

# Subscription module
module "subscription-filters" {
  source                      = "./modules/subscription_filters"
  firehose_arn                = module.splunk-firehose.destination_firehose_arn
  account_id                  = local.account_id
  config_disk_path            = local.config_file
  environment_prefix_variable = local.environment_prefix_variable
}
