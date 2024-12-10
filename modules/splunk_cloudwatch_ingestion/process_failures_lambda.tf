data "archive_file" "process_failures_lambda_function" {
  type        = "zip"
  source_dir  = "${path.module}/../../lambdas/process_failures_lambda/src/mbtp_splunk_cloudwatch_process_failures/"
  output_path = "${path.module}/../../lambdas/process_failures_lambda/src/mbtp_splunk_cloudwatch_process_failures/handler.zip"
}

resource "aws_lambda_function" "firehose_lambda_process_failures" {
  # checkov:skip=CKV_AWS_116:DLQ not required for manually triggered lambda
  # checkov:skip=CKV_AWS_117:Doesn't need to be configured in a VPC as networking is not handled at this level. 
  # checkov:skip=CKV_AWS_50:X-Ray tracing not required for this function
  # checkov:skip=CKV_AWS_272:Code-signing not required for this function
  # checkov:skip=CKV_AWS_115: Don't need a concurrency limit currently 
  # checkov:skip=CKV_AWS_173:Nothing sensitive in the env vars
  function_name    = "${var.environment_prefix_variable}-${var.process_failures_lambda_name}"
  description      = "Manually triggered to move objects from /failed to /retries"
  filename         = data.archive_file.process_failures_lambda_function.output_path
  role             = aws_iam_role.process_failures_lambda.arn
  handler          = "handler.lambda_handler"
  source_code_hash = data.archive_file.process_failures_lambda_function.output_base64sha256
  runtime          = var.python_runtime
  timeout          = var.process_failures_lambda_timeout
  memory_size      = var.process_failures_lambda_memory_size
  tags             = var.tags
  logging_config {
    log_format = "JSON"
    log_group  = aws_cloudwatch_log_group.process_failures_lambda_logs.name
  }
  environment {
    variables = {
      S3_BUCKET_NAME = var.s3_bucket_name
      SQS_QUEUE_ARN  = aws_sqs_queue.retry_notification_queue.arn
      DLQ_QUEUE_ARN  = aws_sqs_queue.retry_sqs_dql.arn
      RETRIES_PREFIX = var.s3_retries_prefix
      FAILED_PREFIX  = var.s3_failed_prefix
    }
  }
}

resource "aws_cloudwatch_log_group" "process_failures_lambda_logs" {
  # checkov:skip=CKV_AWS_158: Not enabling encryption for now
  # checkov:skip=CKV_AWS_338: Ignore retention below 1 year
  name              = "/aws/lambda/${var.environment_prefix_variable}-${var.process_failures_lambda_name}"
  retention_in_days = var.lambda_log_retention
}

resource "aws_iam_role" "process_failures_lambda" {
  name        = "${var.environment_prefix_variable}-${var.process_failures_lambda_name}"
  description = "Role for Lambda function to try reingest logs into Firehose when they fail."

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "process_failures_lambda_default" {
  role       = aws_iam_role.process_failures_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

resource "aws_iam_role_policy_attachment" "process_failures_lambda" {
  role       = aws_iam_role.process_failures_lambda.name
  policy_arn = aws_iam_policy.process_failures_lambda_policy.arn
}

resource "aws_iam_policy" "process_failures_lambda_policy" {
  name   = "${var.environment_prefix_variable}-${var.process_failures_lambda_name}"
  policy = data.aws_iam_policy_document.process_failures_lambda_policy.json
}

data "aws_iam_policy_document" "process_failures_lambda_policy" {
  statement {
    actions   = ["s3:ListBucket", "s3:ListObject*", "s3:GetObject*", "s3:PutObject*", "s3:DeleteObject*"]
    resources = [var.s3_bucket_arn, "${var.s3_bucket_arn}/*"]
  }
  statement {
    actions   = ["sqs:StartMessageMoveTask", "sqs:ReceiveMessage", "sqs:DeleteMessage", "sqs:GetQueueAttributes"]
    resources = [aws_sqs_queue.retry_sqs_dql.arn]
  }
  statement {
    actions   = ["sqs:SendMessage"]
    resources = [aws_sqs_queue.retry_notification_queue.arn]
  }
  statement {
    actions   = ["kms:GenerateDataKey", "kms:Decrypt", "kms:Encrypt"]
    resources = [aws_kms_key.firehose_key.arn, var.s3_kms_key_arn]
  }
}
