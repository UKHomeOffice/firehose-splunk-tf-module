resource "null_resource" "transformation_lambda_exporter" {
  provisioner "local-exec" {
    working_dir = "${path.module}/../../lambdas/transformation_lambda"
    command     = "bash package.sh"
  }
  triggers = {
    trigger = timestamp()
  }
}

data "archive_file" "transformation_lambda_compressor" {
  depends_on = [null_resource.transformation_lambda_exporter]
  excludes   = ["__pycache__"]

  source_dir  = "${path.module}/../../lambdas/transformation_lambda/package/"
  output_path = "${path.module}/../../lambdas/transformation_lambda/package/handler.zip"
  type        = "zip"
}

#trivy:ignore:AVD-AWS-0066 - X-Ray tracing not required for this function
resource "aws_lambda_function" "firehose_lambda_transformation" {
  # checkov:skip=CKV_AWS_116:DLQ is on the reingestion SQS.
  # checkov:skip=CKV_AWS_117:Doesn't need to be configured in a VPC as networking is not handled at this level. 
  # checkov:skip=CKV_AWS_50:X-Ray tracing not required for this function
  # checkov:skip=CKV_AWS_272:Code-signing not required for this function
  # checkov:skip=CKV_AWS_115: Don't need a concurrency limit currently 
  # checkov:skip=CKV_AWS_173:Nothing sensitive in the env vars
  function_name    = "${var.environment_prefix_variable}-${var.transformation_lambda_name}"
  description      = "Transform data from CloudWatch format to Splunk compatible format"
  filename         = data.archive_file.transformation_lambda_compressor.output_path
  source_code_hash = data.archive_file.transformation_lambda_compressor.output_base64sha256
  role             = aws_iam_role.kinesis_firehose_lambda.arn
  handler          = "handler.lambda_handler"
  runtime          = var.python_runtime
  timeout          = var.transformation_lambda_timeout
  memory_size      = var.transformation_lambda_memory_size
  tags             = var.tags
  logging_config {
    log_format            = "JSON"
    log_group             = aws_cloudwatch_log_group.transformation_lambda_logs.name
    application_log_level = var.transformation_lambda_log_level
  }
  environment {
    variables = {
      CONFIG_S3_BUCKET = var.s3_bucket_name
      CONFIG_S3_KEY    = var.s3_config_file_key
    }
  }
  depends_on = [null_resource.transformation_lambda_exporter]
}

#trivy:ignore:AVD-AWS-0017 - Not enabling KMS encryption for now
resource "aws_cloudwatch_log_group" "transformation_lambda_logs" {
  # checkov:skip=CKV_AWS_158: Not enabling KMS encryption for now
  # checkov:skip=CKV_AWS_338: Ignore retention below 1 year
  name              = "/aws/lambda/${var.environment_prefix_variable}-${var.transformation_lambda_name}"
  retention_in_days = var.lambda_log_retention
  tags              = var.tags
}

resource "aws_iam_role" "kinesis_firehose_lambda" {
  name        = "${var.environment_prefix_variable}-${var.transformation_lambda_name}"
  description = "Role for Lambda function to transformation CloudWatch logs into Splunk compatible format"

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

resource "aws_iam_role_policy_attachment" "kinesis_firehose_lambda_default" {
  role       = aws_iam_role.kinesis_firehose_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

resource "aws_iam_role_policy_attachment" "lambda_policy_role_attachment" {
  role       = aws_iam_role.kinesis_firehose_lambda.name
  policy_arn = aws_iam_policy.lambda_transformation_policy.arn
}

resource "aws_iam_policy" "lambda_transformation_policy" {
  name   = "${var.environment_prefix_variable}-${var.transformation_lambda_name}"
  policy = data.aws_iam_policy_document.lambda_policy_doc.json
  tags   = var.tags
}

data "aws_iam_policy_document" "lambda_policy_doc" {
  statement {
    actions = ["firehose:PutRecordBatch"]
    resources = [
      "arn:aws:firehose:${var.region}:${var.account_id}:deliverystream/${local.firehose_stream_name}"
    ]
  }
  statement {
    actions   = ["s3:GetObject*"]
    resources = ["${var.s3_bucket_arn}/*"]
  }
  statement {
    actions   = ["kms:Decrypt"]
    resources = [var.s3_kms_key_arn]
  }
}
