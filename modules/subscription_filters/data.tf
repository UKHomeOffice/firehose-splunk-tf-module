# Enforce Terraform version and define backend as S3
terraform {
  required_version = ">= 0.12.31"

  backend "s3" {}
}

# Configure AWS provider
provider "aws" {
  region  = var.region
  version = ">= 5.40.0"
}


data "aws_s3_object" "config_file" {
  bucket = var.config_s3_bucket
  key    = var.config_s3_key
}

data "template_file" "parsed_config" {
  template = base64decode(data.aws_s3_object.config_file.body)
}

locals {
  config = yamldecode(data.template_file.parsed_config.rendered)
}