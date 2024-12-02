#TRANSFORM LAMBDA

resource "aws_lambda_function" "firehose_lambda_transform" {
  # checkov:skip=CKV_AWS_117:Doesn't need to be configured in a VPC as networking is not handled at this level. 
  # checkov:skip=CKV_AWS_50:X-Ray tracing not required for this function
  # checkov:skip=CKV_AWS_272:Code-signing not required for this function
  function_name                  = "${var.environment_prefix_variable}-splunk-fh-transform"
  description                    = "Transform data from CloudWatch format to Splunk compatible format"
  filename                       = "${path.module}/../../lambdas/transformation_lambda/package/handler.zip"
  role                           = aws_iam_role.kinesis_firehose_lambda.arn
  handler                        = "handler.lambda_handler"
  runtime                        = var.python_runtime
  timeout                        = var.transform_lambda_function_timeout
  memory_size                    = var.transform_lambda_transform_memory_size
  layers                         = ["arn:aws:lambda:${var.region}:580247275435:layer:LambdaInsightsExtension:53"]
  reserved_concurrent_executions = var.transform_lambda_concurrency_limit

  dead_letter_config {
    target_arn = aws_sqs_queue.transform_lambda_dlq.arn
  }

  tracing_config {
    mode = "Active"
  }

  tags = var.tags
  lifecycle {
    ignore_changes = [
      tags
    ]
  }
  depends_on = ["null_resource.lambda_exporter"]

}


resource "null_resource" "lambda_exporter" {
  provisioner "local-exec" {
    working_dir = "${path.module}/../../lambdas/transformation_lambda"
    command     = "bash package.sh"
  }
  triggers = {
    code         = "${base64sha256(file("${path.module}/../../lambdas/transformation_lambda/src/mbtp_splunk_cloudwatch_transformation/handler.py"))}"
    requirements = "${base64sha256(file("${path.module}/../../lambdas/transformation_lambda/requirements.txt"))}"
  }
}

# RETRY LAMBDA 

resource "aws_lambda_function" "firehose_lambda_retry" {
  # checkov:skip=CKV_AWS_116:DLQ is on the reingestion SQS.
  # checkov:skip=CKV_AWS_117:Doesn't need to be configured in a VPC as networking is not handled at this level. 
  # checkov:skip=CKV_AWS_50:X-Ray tracing not required for this function
  # checkov:skip=CKV_AWS_272:Code-signing not required for this function
  function_name                  = "${var.environment_prefix_variable}-splunk-fh-retry"
  description                    = "Reingest logs from the retries prefix of the s3 bucket back into firehose"
  filename                       = data.archive_file.retry_lambda_function.output_path
  role                           = aws_iam_role.kinesis_firehose_lambda.arn
  handler                        = "handler.lambda_handler"
  source_code_hash               = data.archive_file.retry_lambda_function.output_base64sha256
  runtime                        = var.python_runtime
  timeout                        = var.retry_lambda_function_timeout
  memory_size                    = var.retry_lambda_transform_memory_size
  layers                         = ["arn:aws:lambda:${var.region}:580247275435:layer:LambdaInsightsExtension:53"]
  reserved_concurrent_executions = var.retry_lambda_concurrency_limit


  tracing_config {
    mode = "Active"
  }

  tags = var.tags

  lifecycle {
    ignore_changes = [
      tags
    ]
  }
}

data "archive_file" "retry_lambda_function" {
  type        = "zip"
  source_dir  = "${path.module}/../../lambdas/reingestion_lambda/src/mbtp_splunk_cloudwatch_reingestion/"
  output_path = "${path.module}/../../lambdas/reingestion_lambda/src/mbtp_splunk_cloudwatch_reingestion/handler.zip"
}

resource "aws_lambda_event_source_mapping" "retry_lambda_trigger" {
  event_source_arn = aws_sqs_queue.retry_notification_queue.arn
  function_name    = aws_lambda_function.firehose_lambda_retry.arn
}



# REPROCESS FAILED LAMBDA

resource "aws_lambda_function" "firehose_lambda_reprocess_failed" {
  # checkov:skip=CKV_AWS_116:DLQ not required for manually triggered lambda
  # checkov:skip=CKV_AWS_117:Doesn't need to be configured in a VPC as networking is not handled at this level. 
  # checkov:skip=CKV_AWS_50:X-Ray tracing not required for this function
  # checkov:skip=CKV_AWS_272:Code-signing not required for this function
  function_name                  = "${var.environment_prefix_variable}-splunk-fh-reprocess-failed"
  description                    = "Manually triggered to move objects from /failed to /retries"
  filename                       = data.archive_file.reprocess_failed_lambda_function.output_path
  role                           = aws_iam_role.kinesis_firehose_lambda.arn
  handler                        = "handler.lambda_handler"
  source_code_hash               = data.archive_file.retry_lambda_function.output_base64sha256
  runtime                        = var.python_runtime
  timeout                        = var.failed_lambda_function_timeout
  memory_size                    = var.failed_lambda_transform_memory_size
  layers                         = ["arn:aws:lambda:${var.region}:580247275435:layer:LambdaInsightsExtension:53"]
  reserved_concurrent_executions = var.failed_lambda_concurrency_limit

  tracing_config {
    mode = "Active"
  }

  tags = var.tags

  lifecycle {
    ignore_changes = [
      tags
    ]
  }
}

data "archive_file" "reprocess_failed_lambda_function" {
  type        = "zip"
  source_dir  = "${path.module}/../../lambdas/process_failures_lambda/src/mbtp_splunk_cloudwatch_process_failures/"
  output_path = "${path.module}/../../lambdas/process_failures_lambda/src/mbtp_splunk_cloudwatch_process_failures/handler.zip"
}
