# SQS for retry lambda
resource "aws_sqs_queue" "retry_notification_queue" {
  name                       = "${var.environment_prefix_variable}-${var.retry_sqs_name}"
  kms_master_key_id          = aws_kms_key.firehose_key.id
  visibility_timeout_seconds = var.reingestion_lambda_timeout*6 # aws recommends 6x lambda timeout 
  delay_seconds              = 60

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.retry_sqs_dql.arn
    maxReceiveCount     = 3
  })
  tags = var.tags
}

resource "aws_sqs_queue_policy" "s3_sqs" {
  queue_url = aws_sqs_queue.retry_notification_queue.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "s3.amazonaws.com"
        }
        Action   = "sqs:SendMessage"
        Resource = aws_sqs_queue.retry_notification_queue.arn
        Condition = {
          ArnEquals = {
            "aws:SourceArn" = var.s3_bucket_arn
          }
        }
      }
    ]
  })
}

# SQS for retry sqs dead letter queue.
resource "aws_sqs_queue" "retry_sqs_dql" {
  name                       = "${var.environment_prefix_variable}-${var.retry_dlq_name}"
  kms_master_key_id          = aws_kms_key.firehose_key.id
  visibility_timeout_seconds = var.reingestion_lambda_timeout*6 # aws recommends 6x lambda timeout 
  tags                       = var.tags
}
