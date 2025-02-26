data "archive_file" "reingestion_lambda_function" {
  type        = "zip"
  source_dir  = "${path.module}/../../lambdas/reingestion_lambda/src/mbtp_splunk_cloudwatch_reingestion/"
  output_path = "${path.module}/../../lambdas/reingestion_lambda/src/mbtp_splunk_cloudwatch_reingestion/handler_${timestamp()}.zip"
}

resource "aws_lambda_function" "firehose_lambda_reingestion" {
  # checkov:skip=CKV_AWS_116:DLQ is on the reingestion SQS.
  # checkov:skip=CKV_AWS_117:Doesn't need to be configured in a VPC as networking is not handled at this level. 
  # checkov:skip=CKV_AWS_50:X-Ray tracing not required for this function
  # checkov:skip=CKV_AWS_272:Code-signing not required for this function
  # checkov:skip=CKV_AWS_115: Don't need a concurrency limit currently 
  # checkov:skip=CKV_AWS_173:Nothing sensitive in the env vars
  function_name    = "${var.environment_prefix_variable}-${var.reingestion_lambda_name}"
  description      = "Reingest logs from the retries prefix of the s3 bucket back into firehose"
  filename         = data.archive_file.reingestion_lambda_function.output_path
  role             = aws_iam_role.reingestion_lambda.arn
  handler          = "handler.lambda_handler"
  source_code_hash = data.archive_file.reingestion_lambda_function.output_base64sha256
  runtime          = var.python_runtime
  timeout          = var.reingestion_lambda_timeout
  memory_size      = var.reingestion_lambda_memory_size
  tags             = var.tags
  logging_config {
    log_format = "JSON"
    log_group  = aws_cloudwatch_log_group.reingestion_lambda_logs.name
  }
  environment {
    variables = {
      MAX_RETRIES    = 3
      STREAM_NAME    = local.firehose_stream_name
      RETRIES_PREFIX = var.s3_retries_prefix
      FAILED_PREFIX  = var.s3_failed_prefix
    }
  }
}

resource "aws_cloudwatch_log_group" "reingestion_lambda_logs" {
  # checkov:skip=CKV_AWS_158: Not enabling encryption for now
  # checkov:skip=CKV_AWS_338: Ignore retention below 1 year
  name              = "/aws/lambda/${var.environment_prefix_variable}-${var.reingestion_lambda_name}"
  retention_in_days = var.lambda_log_retention
  tags              = var.tags
}

resource "aws_lambda_event_source_mapping" "reingestion_lambda_trigger" {
  event_source_arn = aws_sqs_queue.retry_notification_queue.arn
  function_name    = aws_lambda_function.firehose_lambda_reingestion.arn
}

resource "aws_iam_role" "reingestion_lambda" {
  name        = "${var.environment_prefix_variable}-${var.reingestion_lambda_name}"
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

resource "aws_iam_role_policy_attachment" "reingestion_lambda_default" {
  role       = aws_iam_role.reingestion_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

resource "aws_iam_role_policy_attachment" "reingestion_lambda" {
  role       = aws_iam_role.reingestion_lambda.name
  policy_arn = aws_iam_policy.reingestion_lambda_policy.arn
}

resource "aws_iam_policy" "reingestion_lambda_policy" {
  name   = "${var.environment_prefix_variable}-${var.reingestion_lambda_name}"
  policy = data.aws_iam_policy_document.reingestion_lambda_policy.json
  tags   = var.tags
}

data "aws_iam_policy_document" "reingestion_lambda_policy" {
  statement {
    actions = ["firehose:PutRecordBatch"]
    resources = [
      "arn:aws:firehose:${var.region}:${var.account_id}:deliverystream/${local.firehose_stream_name}"
    ]
  }
  statement {
    actions   = ["s3:HeadObject*", "s3:ListObject*", "s3:GetObject*", "s3:PutObject*", "s3:DeleteObject*"]
    resources = ["${var.s3_bucket_arn}/*"]
  }
  statement {
    actions   = ["kms:GenerateDataKey", "kms:Decrypt", "kms:Encrypt"]
    resources = [var.s3_kms_key_arn, aws_kms_key.firehose_key.arn]
  }
  statement {
    actions   = ["sqs:DeleteMessage", "sqs:GetQueueAttributes", "sqs:ReceiveMessage", "sqs:ChangeMessageVisibility"]
    resources = [aws_sqs_queue.retry_notification_queue.arn]
  }
}
