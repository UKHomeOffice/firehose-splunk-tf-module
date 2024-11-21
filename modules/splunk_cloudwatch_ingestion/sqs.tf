# SQS for transform lambda deadletter queue
resource "aws_sqs_queue" "transform_lambda_dlq" {
  name                      = "${var.environment_prefix_variable}-${aws_lambda_function.firehose_lambda_transform.function_name}-dlq"
  kms_master_key_id         = aws_kms_key.firehose_key.id
}

resource "aws_sqs_queue_policy" "lambda_dlq_policy" {
  queue_url = aws_sqs_queue.lambda_dlq.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AllowLambdaSendMessage"
        Effect    = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${var.account_ids[var.account]}:role/${var.kinesis_firehose_lambda_role_name}"
        }
        Action    = "sqs:SendMessage"
        Resource  = aws_sqs_queue.transform_lambda_dlq.arn
      }
    ]
  })
}



# SQS for retry lambda
resource "aws_sqs_queue" "retry_notification_queue" {
  name                = "${var.environment_prefix_variable}-retry-sqs-queue"
  kms_master_key_id   = aws_kms_key.firehose_key.id
}

# Bucket notification to populate the SQS each time an object is added to the retries/ prefix of the s3 bucket.
resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = var.firehose_failures_bucket_id

  queue {
    queue_arn     = aws_sqs_queue.retry_notification_queue.arn
    events        = ["s3:ObjectCreated:*"]
    filter_prefix = "/retries"
  }
}


# SQS for retry lambda deadletter queue.
resource "aws_sqs_queue" "retry_lambda_dql" {
    name                = "${var.environment_prefix_variable}-${aws_lambda_function.firehose_lambda_retry.function_name}-dlq"
    kms_master_key_id   = aws_kms_key.firehose_key.id
}