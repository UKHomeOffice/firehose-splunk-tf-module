resource "aws_s3_object" "config_yaml" {
  bucket = var.firehose_failures_bucket_name
  key = "config.yaml"
  source = "${path.module}/modules/splunk_cloudwatch_ingestion/config.yaml"
}