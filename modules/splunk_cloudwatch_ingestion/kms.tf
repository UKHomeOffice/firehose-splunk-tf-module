resource "aws_kms_key" "firehose_key" {
  # checkov:skip=CKV2_AWS_64:Key policy to be introduced later
  description             = "KMS key for Kinesis Firehose S3 backup encryption"
  deletion_window_in_days = 10
  enable_key_rotation     = true
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid       = "EnableRootAccess",
        Effect    = "Allow",
        Principal = {
          AWS = "arn:aws:iam::${var.account_id}:root"
        },
        Action    = "kms:*",
        Resource  = "*"
      },
      {
        Sid       = "AllowS3ToUseKey",
        Effect    = "Allow",
        Principal = {
          Service = "s3.amazonaws.com"
        },
        Action    = [
          "kms:Encrypt",
          "kms:GenerateDataKey"
        ],
        Resource  = "*",
        Condition = {
          StringEquals = {
            "aws:SourceArn" = "arn:aws:s3:::${var.firehose_failures_bucket_name}"
          }
        }
      },
      {
        Sid       = "AllowSQSToUseKey",
        Effect    = "Allow",
        Principal = {
          Service = "sqs.amazonaws.com"
        },
        Action    = [
          "kms:Decrypt",
          "kms:GenerateDataKey"
        ],
        Resource  = "*",
        Condition = {
          "ForAnyValue:StringEquals" = {
            "aws:SourceArn" = [
              aws_sqs_queue.retry_notification_queue.arn,
              aws_sqs_queue.transform_lambda_dlq.arn, 
              aws_sqs_queue.retry_sqs_dql.arn
            ]
          }
        }
      }
    ]
  })

  depends_on = [
    aws_sqs_queue.retry_notification_queue, 
    aws_sqs_queue.retry_sqs_dql,
    aws_sqs_queue.transform_lambda_dlq
  ]
}
