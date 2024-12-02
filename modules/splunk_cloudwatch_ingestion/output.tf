output "destination_firehose_arn" {
  description = "cloudwatch log subscription filter - Firehose destination arn"
  value       = aws_kinesis_firehose_delivery_stream.kinesis_firehose.arn
}
