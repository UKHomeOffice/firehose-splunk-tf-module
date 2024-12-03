

# SNS Topic
resource "aws_sns_topic" "sns_topic_failed_splunk_events" {
  name              = "${var.environment_prefix_variable}-failed-splunk-send-notifications"
  kms_master_key_id = aws_kms_key.firehose_key.id
}


# SNS subscriptions
resource "aws_sns_topic_subscription" "subscription_to_failed_splunk_sns_topic" {
  for_each = toset(var.sns_failed_splunk_subscription_emails)

  topic_arn = aws_sns_topic.sns_topic_failed_splunk_events.arn
  protocol  = "email"
  endpoint  = each.value
}

# IAM policy for s3 to plublish to sns
resource "aws_sns_topic_policy" "s3_to_sns_policy" {
  arn = aws_sns_topic.sns_topic_failed_splunk_events.arn

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect    = "Allow",
        Principal = "*",
        Action    = "SNS:*",
        Resource  = aws_sns_topic.sns_topic_failed_splunk_events.arn,
        Condition = {
          ArnLike = {
            "aws:SourceArn" : var.firehose_failures_bucket_arn
          }
        }
      }
    ]
  })
}
