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
  # checkov:skip=CKV_AWS_108:for testing
  # checkov:skip=CKV_AWS_109:for testing
  # checkov:skip=CKV_AWS_110:for testing
  # checkov:skip=CKV_AWS_111:for testing
  # checkov:skip=CKV_AWS_356:for testing
  statement {
    actions = [
      "s3:AbortMultipartUpload",
      "s3:GetBucketLocation",
      "s3:GetObject",
      "s3:ListBucket",
      "s3:ListBucketMultipartUploads",
      "s3:PutObject",
    ]
    resources = ["*"]
    effect    = "Allow"
  }

  statement {
    actions   = ["kms:*"]
    resources = ["*"]
    effect    = "Allow"
  }

  statement {
    actions   = ["logs:*"]
    resources = ["*"]
    effect    = "Allow"
  }

  statement {
    actions = [
      "lambda:InvokeFunction",
      "lambda:GetFunctionConfiguration",
    ]
    resources = [aws_lambda_function.firehose_lambda_transform.arn]
    effect    = "Allow"
  }
}
