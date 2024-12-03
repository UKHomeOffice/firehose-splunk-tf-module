resource "aws_cloudwatch_log_group" "firehose_log_group" {
  name              = "/aws/kinesisfirehose/${local.firehose_stream_name}"
  retention_in_days = var.cloudwatch_log_retention
  tags              = var.tags
}

resource "aws_cloudwatch_log_stream" "firehose_log_stream" {
  name           = var.log_stream_name
  log_group_name = aws_cloudwatch_log_group.firehose_log_group.name
}
