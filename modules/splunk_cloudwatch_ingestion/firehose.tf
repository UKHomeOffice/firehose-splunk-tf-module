# Processing enabled kinesis firehose
resource "aws_kinesis_firehose_delivery_stream" "kinesis_firehose" {
  # checkov:skip=CKV_AWS_240:A CMK is being used for failed events sent to s3. It cannot be used for the primary destination, which is Splunk.
  # checkov:skip=CKV_AWS_241:A CMK is being used for failed events sent to s3. It cannot be used for the primary destination, which is Splunk.
  name        = "${var.environment_prefix_variable}-firehose-cloudwatch-to-splunk"
  destination = "splunk"

  splunk_configuration {
    hec_endpoint               = var.hec_url
    hec_token                  = var.splunk_hec_token
    hec_acknowledgment_timeout = var.hec_acknowledgment_timeout
    hec_endpoint_type          = var.hec_endpoint_type
    s3_backup_mode             = var.s3_backup_mode
    retry_duration             = var.retry_duration

    s3_configuration {
      role_arn           = "arn:aws:iam::${var.account_id}:role/${var.environment_prefix_variable}-${var.kinesis_firehose_role_name}"
      prefix             = "/retries/"
      bucket_arn         = var.firehose_failures_bucket_arn
      buffering_size     = var.kinesis_firehose_buffer
      buffering_interval = var.kinesis_firehose_buffer_interval
      kms_key_arn = aws_kms_key.firehose_key.arn
    }

    processing_configuration {
      enabled = "true"

      processors {
        type = "Lambda"

        parameters {
          parameter_name  = "LambdaArn"
          parameter_value = "${aws_lambda_function.firehose_lambda_transform.arn}:$LATEST"
        }
        parameters {
          parameter_name  = "RoleArn"
          parameter_value = "arn:aws:iam::${var.account_id}:role/${var.environment_prefix_variable}-${var.kinesis_firehose_role_name}"
        }
        parameters {
          parameter_name  = "BufferSizeInMBs"
          parameter_value = var.kinesis_firehose_transform_buffer
        }
        parameters {
          parameter_name  = "BufferIntervalInSeconds"
          parameter_value = var.kinesis_firehose_transform_buffer_interval
        }
      }
    }

    cloudwatch_logging_options {
      enabled         = var.enable_fh_cloudwatch_logging
      log_group_name  = "/aws/kinesisfirehose/${var.environment_prefix_variable}-firehose-cloudwatch-to-splunk"
      log_stream_name = var.log_stream_name
    }
  }

  tags = var.tags

  lifecycle {
    ignore_changes = [
      tags,
      splunk_configuration[0].processing_configuration[0].processors[0].parameters
    ]
  }
}
