

# SNS Topic
resource "aws_sns_topic" "sns_topic_alerts" {
  name              = "${var.environment_prefix_variable}-${var.alerts_sns_topic_name}"
  kms_master_key_id = aws_kms_key.firehose_key.id
  tags              = var.tags
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
        Sid    = "Allow S3",
        Effect = "Allow",
        Principal = {
          Service = "s3.amazonaws.com"
        }
        Action   = "SNS:Publish",
        Resource = aws_sns_topic.sns_topic_alerts.arn,
      },
      {
        Sid    = "Allow Cloudwatch",
        Effect = "Allow",
        Principal = {
          Service = "cloudwatch.amazonaws.com"
        }
        Action   = "SNS:Publish",
        Resource = aws_sns_topic.sns_topic_alerts.arn,
      }
    ]
  })
}
