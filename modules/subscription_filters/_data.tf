data "aws_s3_object" "config_file" {
  bucket = var.config_s3_bucket
  key    = var.config_s3_key
}

data "template_file" "parsed_config" {
  template = filebase64decode(data.aws_s3_object.config_file.body)
}

locals {
  config = yamldecode(data.template_file.parsed_config.rendered)
}