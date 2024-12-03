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
      "s3:*",
    ]
    resources = [
      var.firehose_failures_bucket_arn,
      "${var.firehose_failures_bucket_arn}/*",
    ]
    effect = "Allow"
  }

  statement {
    actions   = ["kms:*"]
    resources = [var.s3_kms_key_arn]
    effect    = "Allow"
  }

  statement {
    actions = ["logs:*"]
    resources = [
      "*"
    ]
    effect = "Allow"
  }

  statement {
    actions = [
      "lambda:*",
    ]
    resources = ["*"]
    effect    = "Allow"
  }
}
