data "aws_s3_object" "config_file" {
  bucket = var.config_s3_bucket
  key    = var.config_s3_key
}

locals {
  config = yamldecode(data.aws_s3_object.config_file.body)
}