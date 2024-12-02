# SQS for retry lambda
resource "aws_sqs_queue" "retry_notification_queue" {
  name                       = "${var.environment_prefix_variable}-retry-sqs-queue"
  kms_master_key_id          = aws_kms_key.firehose_key.id
  visibility_timeout_seconds = 5400

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.retry_sqs_dql.arn
    maxReceiveCount     = 5
  })
}

# Bucket notification to populate the SQS each time an object is added to the retries/ prefix of the s3 bucket.
resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = var.firehose_failures_bucket_name

  queue {
    queue_arn     = aws_sqs_queue.retry_notification_queue.arn
    events        = ["s3:ObjectCreated:*"]
    filter_prefix = var.s3_retries_prefix
  }
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
            "aws:SourceArn" = var.firehose_failures_bucket_arn
          }
        }
      }
    ]
  })
}


# SQS for retry sqs deadletter queue.
resource "aws_sqs_queue" "retry_sqs_dql" {
  name                       = "${var.environment_prefix_variable}-splunk-fh-retry-dlq"
  kms_master_key_id          = aws_kms_key.firehose_key.id
  visibility_timeout_seconds = 5400
}
