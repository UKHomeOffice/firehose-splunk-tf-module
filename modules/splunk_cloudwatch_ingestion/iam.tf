# Kinesis Firehose Policy

resource "aws_iam_role" "kinesis_firehose_role" {
  name        = "${var.environment_prefix_variable}-${var.kinesis_firehose_role_name}"
  description = "Role for kinesis firehose"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "firehose.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "kinesis_fh_role_attachment" {
  role       = aws_iam_role.kinesis_firehose_role.name
  policy_arn = aws_iam_policy.kinesis_firehose_iam_policy.arn
}

resource "aws_iam_policy" "kinesis_firehose_iam_policy" {
  name   = "${var.environment_prefix_variable}_${var.kinesis_firehose_iam_policy_name}"
  policy = data.aws_iam_policy_document.kinesis_firehose_policy_document.json
}

data "aws_iam_policy_document" "kinesis_firehose_policy_document" {
  statement {
    actions = [
      "s3:AbortMultipartUpload",
      "s3:GetBucketLocation",
      "s3:GetObject",
      "s3:ListBucket",
      "s3:ListBucketMultipartUploads",
      "s3:PutObject",
    ]
    resources = [
      var.firehose_failures_bucket_arn,
      "${var.firehose_failures_bucket_arn}/*",
    ]
    effect = "Allow"
  }

  statement {
    actions   = ["kms:Decrypt", "kms:GenerateDataKey"]
    resources = [var.s3_kms_key_arn]
    effect    = "Allow"
    condition {
      test     = "StringEquals"
      variable = "kms:ViaService"
      values   = ["s3.${var.region}.amazonaws.com"]
    }
    condition {
      test     = "StringLike"
      variable = "kms:EncryptionContext:aws:s3:arn"
      values   = ["${var.firehose_failures_bucket_arn}/*"]
    }
  }

  statement {
    actions = ["logs:PutLogEvents"]
    resources = [
      "arn:aws:logs:${var.region}:${var.account_id}:log-group:/aws/kinesisfirehose/${local.firehose_stream_name}"
    ]
    effect = "Allow"
  }

  statement {
    actions = [
      "lambda:InvokeFunction",
      "lambda:GetFunctionConfiguration",
    ]
    resources = ["${aws_lambda_function.firehose_lambda_transform.arn}:$LATEST"]
    effect    = "Allow"
  }
}
