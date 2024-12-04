# Bucket notification to populate the SQS each time an object is added to the retries/ prefix of the s3 bucket.
# S3 bucket notification to trigger SNS topic
resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = var.s3_bucket_name

  topic {
    topic_arn     = aws_sns_topic.sns_topic_failed_splunk_events.arn
    events        = ["s3:ObjectCreated:*"]
    filter_prefix = var.s3_failed_prefix
  }
  queue {
    queue_arn     = aws_sqs_queue.retry_notification_queue.arn
    events        = ["s3:ObjectCreated:*"]
    filter_prefix = var.s3_retries_prefix
  }
}
