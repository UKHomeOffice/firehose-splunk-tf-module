# Processing enabled kinesis firehose
resource "aws_kinesis_firehose_delivery_stream" "kinesis_firehose" {
  # checkov:skip=CKV_AWS_240:A CMK is being used for failed events sent to s3. It cannot be used for the primary destination, which is Splunk.
  # checkov:skip=CKV_AWS_241:A CMK is being used for failed events sent to s3. It cannot be used for the primary destination, which is Splunk.
  name        = local.firehose_stream_name
  destination = "splunk"

  splunk_configuration {
    hec_endpoint               = var.hec_url
    hec_token                  = var.hec_token
    hec_acknowledgment_timeout = var.hec_acknowledgment_timeout
    hec_endpoint_type          = var.hec_endpoint_type
    s3_backup_mode             = "FailedEventsOnly"
    retry_duration             = var.firehose_retry_duration

    s3_configuration {
      role_arn           = aws_iam_role.kinesis_firehose_role.arn
      prefix             = var.s3_retries_prefix
      bucket_arn         = var.s3_bucket_arn
      buffering_size     = var.firehose_buffer
      buffering_interval = var.firehose_buffer_interval
      kms_key_arn        = aws_kms_key.firehose_key.arn
      compression_format = "UNCOMPRESSED"
    }

    processing_configuration {
      enabled = "true"

      processors {
        type = "Lambda"

        parameters {
          parameter_name  = "LambdaArn"
          parameter_value = "${aws_lambda_function.firehose_lambda_transformation.arn}:$LATEST"
        }
        parameters {
          parameter_name  = "RoleArn"
          parameter_value = aws_iam_role.kinesis_firehose_role.arn
        }
        parameters {
          parameter_name  = "BufferSizeInMBs"
          parameter_value = var.firehose_transform_buffer
        }
        parameters {
          parameter_name  = "BufferIntervalInSeconds"
          parameter_value = var.firehose_transform_buffer_interval
        }
      }
    }

    cloudwatch_logging_options {
      enabled         = true
      log_group_name  = aws_cloudwatch_log_group.firehose_log_group.name
      log_stream_name = aws_cloudwatch_log_stream.firehose_log_stream.name
    }
  }

  tags = var.tags
}

resource "aws_cloudwatch_log_group" "firehose_log_group" {
  # checkov:skip=CKV_AWS_158: Not enabling encryption for now
  # checkov:skip=CKV_AWS_338: Ignore retention below 1 year
  name              = "/aws/kinesisfirehose/${var.environment_prefix_variable}-${var.firehose_log_group_name}"
  retention_in_days = var.firehose_log_retention
  tags              = var.tags
}

resource "aws_cloudwatch_log_stream" "firehose_log_stream" {
  name           = var.firehose_log_stream_name
  log_group_name = aws_cloudwatch_log_group.firehose_log_group.name
}
