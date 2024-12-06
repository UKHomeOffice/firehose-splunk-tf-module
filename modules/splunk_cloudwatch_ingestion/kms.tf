resource "aws_kms_key" "firehose_key" {
  description             = "KMS key for Kinesis Firehose S3 backup encryption"
  deletion_window_in_days = 10
  enable_key_rotation     = true
}

resource "aws_kms_alias" "firehose_key_alias" {
  name          = "alias/${var.environment_prefix_variable}-${var.kms_key_name}"
  target_key_id = aws_kms_key.firehose_key.key_id
}

resource "aws_kms_key_policy" "firehose_key_policy" {
  key_id = aws_kms_key.firehose_key.id
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid    = "EnableRootAccess",
        Effect = "Allow",
        Principal = {
          AWS = "arn:aws:iam::${var.account_id}:root"
        },
        Action   = "kms:*",
        Resource = aws_kms_key.firehose_key.arn
      },
      {
        Sid    = "AllowS3ToUseKey",
        Effect = "Allow",
        Principal = {
          Service = "s3.amazonaws.com"
        },
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:GenerateDataKey"
        ],
        Resource = aws_kms_key.firehose_key.arn,
        Condition = {
          StringEquals = {
            "aws:SourceArn" = var.s3_bucket_arn
          }
        }
      },
      {
        Sid    = "AllowSQSToUseKey",
        Effect = "Allow",
        Principal = {
          Service = "sqs.amazonaws.com"
        },
        Action = [
          "kms:Decrypt",
          "kms:GenerateDataKey"
        ],
        Resource = aws_kms_key.firehose_key.arn,
        Condition = {
          "ForAnyValue:StringEquals" = {
            "aws:SourceArn" = [
              aws_sqs_queue.retry_notification_queue.arn,
              aws_sqs_queue.retry_sqs_dql.arn
            ]
          }
        }
      },
      {
        Sid    = "AllowCloudwatch",
        Effect = "Allow",
        Principal = {
          Service = "cloudwatch.amazonaws.com"
        },
        Action = [
          "kms:Decrypt",
          "kms:GenerateDataKey"
        ],
        Resource = aws_kms_key.firehose_key.arn,
      }
    ]
  })
}
