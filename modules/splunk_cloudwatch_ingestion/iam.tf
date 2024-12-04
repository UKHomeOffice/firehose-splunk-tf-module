# Kinesis Firehose Policy

resource "aws_iam_role" "kinesis_firehose_role" {
  name        = "${var.environment_prefix_variable}-${var.firehose_role_name}"
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
  policy_arn = aws_iam_policy.kinesis_firehose_policy.arn
}

resource "aws_iam_policy" "kinesis_firehose_policy" {
  name   = "${var.environment_prefix_variable}-${var.firehose_role_name}"
  policy = data.aws_iam_policy_document.kinesis_firehose_policy_document.json
}

data "aws_iam_policy_document" "kinesis_firehose_policy_document" {
  # checkov:skip=CKV_AWS_111
  # checkov:skip=CKV_AWS_356
  statement {
    actions = [
      "s3:AbortMultipartUpload",
      "s3:GetBucketLocation",
      "s3:GetObject",
      "s3:ListBucket",
      "s3:ListBucketMultipartUploads",
      "s3:PutObject",
    ]
    resources = [var.s3_bucket_arn, "${var.s3_bucket_arn}/*"]
    effect    = "Allow"
  }

  statement {
    actions   = ["kms:*"]
    resources = [var.s3_kms_key_arn]
    effect    = "Allow"
  }

  statement {
    actions   = ["logs:PutLogEvents"]
    resources = ["${aws_cloudwatch_log_group.firehose_log_group.arn}:*"]
    effect    = "Allow"
  }

  statement {
    actions = [
      "lambda:InvokeFunction",
      "lambda:GetFunctionConfiguration",
    ]
    resources = ["${aws_lambda_function.firehose_lambda_transformation.arn}:$LATEST"]
    effect    = "Allow"
  }
}
