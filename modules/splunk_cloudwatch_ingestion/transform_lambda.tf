resource "null_resource" "lambda_exporter" {
  provisioner "local-exec" {
    working_dir = "${path.module}/../../lambdas/transformation_lambda"
    command     = "bash package.sh"
  }
  triggers = {
    # code         = "${base64sha256(file("${path.module}/../../lambdas/transformation_lambda/src/mbtp_splunk_cloudwatch_transformation/handler.py"))}"
    # requirements = "${base64sha256(file("${path.module}/../../lambdas/transformation_lambda/requirements.txt")S)}"
    trigger = timestamp()
  }
}

data "archive_file" "lambda_compressor" {
  depends_on = [null_resource.lambda_exporter]
  excludes   = ["__pycache__"]

  source_dir  = "${path.module}/../../lambdas/transformation_lambda/package/"
  output_path = "${path.module}/../../lambdas/transformation_lambda/package/handler.zip"
  type        = "zip"
}

resource "aws_lambda_function" "firehose_lambda_transform" {
  # checkov:skip=CKV_AWS_116:DLQ is on the reingestion SQS.
  # checkov:skip=CKV_AWS_117:Doesn't need to be configured in a VPC as networking is not handled at this level. 
  # checkov:skip=CKV_AWS_50:X-Ray tracing not required for this function
  # checkov:skip=CKV_AWS_272:Code-signing not required for this function
  # checkov:skip=CKV_AWS_115: Don't need a concurrency limit currently 
  # checkov:skip=CKV_AWS_173:Nothing sensitive in the env vars
  function_name    = "${var.environment_prefix_variable}-splunk-fh-transform"
  description      = "Transform data from CloudWatch format to Splunk compatible format"
  filename         = data.archive_file.lambda_compressor.output_path
  source_code_hash = data.archive_file.lambda_compressor.output_base64sha256
  role             = aws_iam_role.kinesis_firehose_lambda.arn
  handler          = "handler.lambda_handler"
  runtime          = var.python_runtime
  timeout          = var.transform_lambda_function_timeout
  memory_size      = var.transform_lambda_transform_memory_size
  tags             = var.tags
  environment {
    variables = {
      CONFIG_S3_BUCKET = var.firehose_failures_bucket_name
      CONFIG_S3_KEY    = var.s3_config_file_key
    }
  }
  depends_on = [null_resource.lambda_exporter]
}

resource "aws_iam_role" "kinesis_firehose_lambda" {
  name        = "${var.environment_prefix_variable}-splunk-fh-transform"
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
  policy_arn = aws_iam_policy.lambda_transform_policy.arn
}

resource "aws_iam_policy" "lambda_transform_policy" {
  name   = "${var.environment_prefix_variable}-splunk-fh-transform"
  policy = data.aws_iam_policy_document.lambda_policy_doc.json
}

data "aws_iam_policy_document" "lambda_policy_doc" {
  statement {
    actions = ["firehose:*"]
    resources = [
      "arn:aws:firehose:${var.region}:${var.account_id}:deliverystream/${local.firehose_stream_name}"
    ]
  }
  statement {
    actions   = ["s3:*"]
    resources = [
      "${var.firehose_failures_bucket_arn}",
      "${var.firehose_failures_bucket_arn}/*"
    ]
  }
  statement {
    actions   = ["kms:Decrypt"]
    resources = [var.s3_kms_key_arn]
  }
}
