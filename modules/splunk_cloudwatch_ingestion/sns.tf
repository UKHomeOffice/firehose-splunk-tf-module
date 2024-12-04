

# SNS Topic
resource "aws_sns_topic" "sns_topic_alerts" {
  name              = "${var.environment_prefix_variable}-${var.alerts_sns_topic_name}"
  kms_master_key_id = aws_kms_key.firehose_key.id
}

# SNS subscriptions
resource "aws_sns_topic_subscription" "subscription_to_failed_splunk_sns_topic" {
  for_each = toset(var.alerts_subscription_emails)

  topic_arn = aws_sns_topic.sns_topic_alerts.arn
  protocol  = "email"
  endpoint  = each.value
}

# IAM policy for s3 to publish to sns
resource "aws_sns_topic_policy" "s3_to_sns_policy" {
  arn = aws_sns_topic.sns_topic_alerts.arn

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect    = "Allow",
        Principal = "*",
        Action    = "SNS:Publish",
        Resource  = aws_sns_topic.sns_topic_alerts.arn,
        Condition = {
          ArnLike = {
            "aws:SourceArn" : var.s3_bucket_arn
          }
        }
      }
    ]
  })
}
