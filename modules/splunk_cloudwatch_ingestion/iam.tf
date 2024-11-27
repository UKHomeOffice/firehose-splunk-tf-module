# Lambda Processing Policy
resource "aws_iam_role" "kinesis_firehose_lambda" {
  name        = "${var.environment_prefix_variable}-${var.kinesis_firehose_lambda_role_name}"
  description = "Role for Lambda function to transformation CloudWatch logs into Splunk compatible format"

  assume_role_policy = <<POLICY
{
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      }
    }
  ],
  "Version": "2012-10-17"
}
POLICY


  tags = var.tags
  lifecycle {
    ignore_changes = [
      tags
    ]
  }
}

data "aws_iam_policy_document" "lambda_policy_doc" {
  statement {
    actions = [
      "logs:GetLogEvents",
    ]

    resources = [
      for log_group in var.cloudwatch_log_group_subscription_to_firehose : "arn:aws:logs:${var.region}:${var.account_ids[var.account]}:log-group:${log_group}:*"
    ]

    effect = "Allow"
  }

  statement {
    actions = [
      "firehose:PutRecordBatch",
    ]

    resources = [
      "arn:aws:firehose:${var.region}:${var.account_ids[var.account]}:deliverystream/*"
    ]
  }

  statement {
    actions = [
      "logs:PutLogEvents",
    ]

    resources = [
      for log_group in var.cloudwatch_log_group_subscription_to_firehose : "arn:aws:logs:${var.region}:${var.account_ids[var.account]}:log-group:${log_group}:log-stream:*"
    ]

    effect = "Allow"
  }

  statement {
    actions = [
      "logs:CreateLogGroup",
    ]

    resources = [
      "arn:aws:logs:${var.region}:${var.account_ids[var.account]}:log-group:*"
    ]

    effect = "Allow"
  }

  statement {
    actions = [
      "logs:CreateLogStream",
    ]

    resources = [
      for log_group in var.cloudwatch_log_group_subscription_to_firehose : "arn:aws:logs:${var.region}:${var.account_ids[var.account]}:log-group:${log_group}"
    ]

    effect = "Allow"
  }

  statement {
    actions = [
      "sqs:SendMessage"
    ]
    resources = [
      aws_sqs_queue.transform_lambda_dlq.arn,
      aws_sqs_queue.retry_sqs_dql.arn
    ]
    effect = "Allow"
  }
}

resource "aws_iam_policy" "lambda_transform_policy" {
  name   = "${var.environment_prefix_variable}_${var.lambda_iam_policy_name}_${local.region_short}"
  policy = data.aws_iam_policy_document.lambda_policy_doc.json
}

resource "aws_iam_role_policy_attachment" "lambda_policy_role_attachment" {
  role       = aws_iam_role.kinesis_firehose_lambda.name
  policy_arn = aws_iam_policy.lambda_transform_policy.arn
}


# Kinesis Firehose Policy

resource "aws_iam_role" "kinesis_firehose_role" {
  name        = "${var.environment_prefix_variable}-${var.kinesis_firehose_role_name}"
  description = "Role for kinesis firehose"

  assume_role_policy = <<POLICY
{
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      }
    }
  ],
  "Version": "2012-10-17"
}
POLICY


  tags = var.tags
  lifecycle {
    ignore_changes = [
      tags
    ]
  }
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
      "arn:aws:s3:::${var.firehose_failures_bucket_name}",
      "arn:aws:s3:::${var.firehose_failures_bucket_name}/*",
    ]

    effect = "Allow"
  }

  statement {
    actions = [
      "lambda:InvokeFunction",
      "lambda:GetFunctionConfiguration",
    ]

    resources = [
      "arn:aws:lambda:eu-west-1:${var.account_ids[var.account]}:function:kinesis-firehose-transform:$LATEST",
      "arn:aws:lambda:eu-west-2:${var.account_ids[var.account]}:function:kinesis-firehose-transform:$LATEST",
    ]
  }

  statement {
    actions = [
      "logs:PutLogEvents",
    ]

    resources = [
      "arn:aws:logs:${var.region}:${lookup(var.account_ids, var.account)}:log-group:/aws/kinesisfirehose/*"
    ]

    effect = "Allow"
  }
}

resource "aws_iam_policy" "kinesis_firehose_iam_policy" {
  name   = "${var.environment_prefix_variable}_${var.kinesis_firehose_iam_policy_name}_${local.region_short}"
  policy = data.aws_iam_policy_document.kinesis_firehose_policy_document.json
}

resource "aws_iam_role_policy_attachment" "kinesis_fh_role_attachment" {
  role       = aws_iam_role.kinesis_firehose_role.name
  policy_arn = aws_iam_policy.kinesis_firehose_iam_policy.arn
}

# Log Group Subscription Policy
resource "aws_iam_role" "cloudwatch_to_firehose_trust" {
  name        = "${var.environment_prefix_variable}-${var.cloudwatch_to_firehose_trust_iam_role_name}"
  description = "Role for CloudWatch Log Group subscription"

  assume_role_policy = <<ROLE
{
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": [
          "logs.eu-west-1.amazonaws.com",
          "logs.eu-west-2.amazonaws.com"
        ]
      }
    }
  ],
  "Version": "2012-10-17"
}
ROLE


  tags = var.tags
    lifecycle {
    ignore_changes = [
      tags
    ]
  }
}

# Cloudwatch Logs to Firehose Policy
data "aws_iam_policy_document" "cloudwatch_to_fh_access_policy" {
  statement {
    actions = [
      "firehose:*",
    ]

    effect = "Allow"

    resources = [
      "arn:aws:firehose:eu-west-1:${var.account_ids[var.account]}:deliverystream/*",
      "arn:aws:firehose:eu-west-2:${var.account_ids[var.account]}:deliverystream/*",
    ]
  }

  statement {
    actions = [
      "iam:PassRole",
    ]

    effect = "Allow"

    resources = [
      aws_iam_role.cloudwatch_to_firehose_trust.arn,
    ]
  }
}

resource "aws_iam_policy" "cloudwatch_to_fh_access_policy" {
  name        = "${var.environment_prefix_variable}_${var.cloudwatch_to_fh_access_policy_name}_${local.region_short}"
  description = "Cloudwatch to Firehose Subscription Policy"
  policy      = data.aws_iam_policy_document.cloudwatch_to_fh_access_policy.json
}

resource "aws_iam_role_policy_attachment" "cloudwatch_to_fh" {
  role       = aws_iam_role.cloudwatch_to_firehose_trust.name
  policy_arn = aws_iam_policy.cloudwatch_to_fh_access_policy.arn
}
