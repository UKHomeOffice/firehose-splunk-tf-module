# CloudWatch Alarm for Lambda Errors
resource "aws_cloudwatch_metric_alarm" "lambda_error_alarm" {
  for_each = toset([
    "${var.environment_prefix_variable}-${var.transformation_lambda_name}",
    "${var.environment_prefix_variable}-${var.reingestion_lambda_name}",
    "${var.environment_prefix_variable}-${var.process_failures_lambda_name}"
  ])
  alarm_name                = "${each.value}-lambda_errors_alarm"
  alarm_description         = "Triggers when the Lambda function errors exceed 0 in a minute."
  comparison_operator       = "GreaterThanThreshold"
  evaluation_periods        = 5
  metric_name               = "Errors"
  namespace                 = "AWS/Lambda"
  period                    = 60 # Check every minute
  statistic                 = "Sum"
  threshold                 = 0 # Triggers if errors > 0
  insufficient_data_actions = []
  tags                      = var.tags
  dimensions = {
    FunctionName = each.value
  }
  treat_missing_data = "ignore"
  actions_enabled    = true
  alarm_actions      = [aws_sns_topic.sns_topic_alerts.arn]
  ok_actions         = [aws_sns_topic.sns_topic_alerts.arn]
}

# CloudWatch alarm for Lambda Throttling
resource "aws_cloudwatch_metric_alarm" "lambda_throttles_alarm" {
  for_each = toset([
    "${var.environment_prefix_variable}-${var.transformation_lambda_name}",
    "${var.environment_prefix_variable}-${var.reingestion_lambda_name}",
    "${var.environment_prefix_variable}-${var.process_failures_lambda_name}"
  ])
  alarm_name                = "${each.value}-lambda_throttle_alarm"
  alarm_description         = "Triggers when the Lambda function is throttled."
  comparison_operator       = "GreaterThanThreshold"
  evaluation_periods        = 5
  metric_name               = "Throttles"
  namespace                 = "AWS/Lambda"
  period                    = 60
  statistic                 = "Sum"
  threshold                 = 1 # Trigger if throttling occurs
  insufficient_data_actions = []
  tags                      = var.tags
  dimensions = {
    FunctionName = each.value
  }
  treat_missing_data = "ignore"
  actions_enabled    = true
  alarm_actions      = [aws_sns_topic.sns_topic_alerts.arn]
  ok_actions         = [aws_sns_topic.sns_topic_alerts.arn]
}

# CloudWatch alarm for SQS Queue Messages
resource "aws_cloudwatch_metric_alarm" "sqs_message_backlog" {
  alarm_name                = "${var.environment_prefix_variable}-${var.retry_sqs_name}-sqs_message_backlog_alarm"
  alarm_description         = "Triggers when there are more than 3 messages in the ${var.environment_prefix_variable}-${var.retry_sqs_name} SQS queue."
  comparison_operator       = "GreaterThanThreshold"
  evaluation_periods        = 3
  metric_name               = "ApproximateNumberOfMessagesVisible"
  namespace                 = "AWS/SQS"
  period                    = 60
  statistic                 = "Sum"
  threshold                 = 3
  insufficient_data_actions = []
  tags                      = var.tags
  dimensions = {
    QueueName = "${var.environment_prefix_variable}-${var.retry_sqs_name}"
  }
  treat_missing_data = "ignore"
  actions_enabled    = true
  alarm_actions      = [aws_sns_topic.sns_topic_alerts.arn]
  ok_actions         = [aws_sns_topic.sns_topic_alerts.arn]
}

resource "aws_cloudwatch_metric_alarm" "sqs_dlq_message_backlog" {
  alarm_name                = "${var.environment_prefix_variable}-${var.retry_dlq_name}-dlq_message_backlog_alarm"
  alarm_description         = "Triggers when there are messages in the ${var.environment_prefix_variable}-${var.retry_dlq_name} DLQ SQS queue. Navigate to https://${var.region}.console.aws.amazon.com/lambda/home?region=${var.region}#/functions/${var.environment_prefix_variable}-${var.process_failures_lambda_name}?tab=testing, Click Test"
  comparison_operator       = "GreaterThanThreshold"
  evaluation_periods        = 1
  metric_name               = "ApproximateNumberOfMessagesVisible"
  namespace                 = "AWS/SQS"
  period                    = 60
  statistic                 = "Sum"
  threshold                 = 0
  insufficient_data_actions = []
  tags                      = var.tags
  dimensions = {
    QueueName = "${var.environment_prefix_variable}-${var.retry_dlq_name}"
  }
  treat_missing_data = "ignore"
  actions_enabled    = true
  alarm_actions      = [aws_sns_topic.sns_topic_alerts.arn]
  ok_actions         = [aws_sns_topic.sns_topic_alerts.arn]
}


# CloudWatch Alarm for Firehose Splunk Processing
resource "aws_cloudwatch_metric_alarm" "cloudwatch_alarm_firehose_splunk_processing" {
  alarm_name                = "${var.environment_prefix_variable}-firehose_splunk"
  alarm_description         = "Alarm if the ${local.firehose_stream_name} Firehose to Splunk stops sending data to Splunk"
  metric_name               = "DeliveryToSplunk.Success"
  namespace                 = "AWS/Firehose"
  statistic                 = "Average"
  comparison_operator       = "LessThanThreshold"
  evaluation_periods        = 1
  period                    = 300
  threshold                 = 1
  insufficient_data_actions = []
  tags                      = var.tags
  treat_missing_data        = "ignore"
  actions_enabled           = true
  alarm_actions             = [aws_sns_topic.sns_topic_alerts.arn]
  ok_actions                = [aws_sns_topic.sns_topic_alerts.arn]
  dimensions = {
    DeliveryStreamName = local.firehose_stream_name
  }
}

# CloudWatch Alarm for IncomingBytes 
resource "aws_cloudwatch_metric_alarm" "cloudwatch_alarm_firehose_incoming_bytes" {
  for_each = local.multiplier_rate
  alarm_name                = "${var.environment_prefix_variable}-firehose-incoming-bytes-${each.key}"
  alarm_description         = "${local.alarm_description_text} ${each.key} of the BytesPerSecondLimit"
  comparison_operator       = "GreaterThanThreshold"
  evaluation_periods        = 5
  datapoints_to_alarm       = 3
  threshold                 = each.value
  tags                      = var.tags
  treat_missing_data        = "ignore" 
  actions_enabled           = true
  insufficient_data_actions = []
  alarm_actions             = [aws_sns_topic.sns_topic_alerts.arn]
  ok_actions                = [aws_sns_topic.sns_topic_alerts.arn]

  metric_query {
    id          = "e1"
    expression  = "(m1/PERIOD(m1))/FILL(m2, REPEAT)"
    label       = "Percentage Byte Limit"
    return_data = "true"
  }

  metric_query {
    id = "m1"

    metric {
      metric_name = "IncomingBytes"
      namespace   = "AWS/Firehose"
      period      = 60
      stat        = "Sum"
      unit        = "Bytes"

      dimensions = {
        DeliveryStreamName = local.firehose_stream_name
      }
    }
  }

  metric_query {
    id = "m2"

    metric {
      metric_name = "BytesPerSecondLimit"
      namespace   = "AWS/Firehose"
      period      = 60
      stat        = "Minumum"
      unit        = "Bytes/sec"

      dimensions = {
        DeliveryStreamName = local.firehose_stream_name
      }
    }
  }
}

# CloudWatch Alarm for IncomingPutRequests 
resource "aws_cloudwatch_metric_alarm" "cloudwatch_alarm_firehose_incoming_put_requests" {
  for_each = local.multiplier_rate
  alarm_name                = "${var.environment_prefix_variable}-firehose-incoming-put-requests-${each.key}"
  alarm_description         = "${local.alarm_description_text} ${each.key} of the PutRequestsPerSecondLimit"
  comparison_operator       = "GreaterThanThreshold"
  evaluation_periods        = 5
  datapoints_to_alarm       = 3
  threshold                 = each.value
  tags                      = var.tags
  treat_missing_data        = "ignore" 
  actions_enabled           = true
  insufficient_data_actions = []
  alarm_actions             = [aws_sns_topic.sns_topic_alerts.arn]
  ok_actions                = [aws_sns_topic.sns_topic_alerts.arn]

  metric_query {
    id          = "e1"
    expression  = "(m1/PERIOD(m1))/FILL(m2, REPEAT)"
    label       = "Percentage Put Limit"
    return_data = "true"
  }

  metric_query {
    id = "m1"

    metric {
      metric_name = "IncomingPutRequests"
      namespace   = "AWS/Firehose"
      period      = 60
      stat        = "Sum"
      unit        = "Count"

      dimensions = {
        DeliveryStreamName = local.firehose_stream_name
      }
    }
  }

  metric_query {
    id = "m2"

    metric {
      metric_name = "PutRequestsPerSecondLimit"
      namespace   = "AWS/Firehose"
      period      = 60
      stat        = "Minimum"
      unit        = "Count"

      dimensions = {
        DeliveryStreamName = local.firehose_stream_name
      }
    }
  }
}


# CloudWatch Alarm for IncomingRecords 
resource "aws_cloudwatch_metric_alarm" "cloudwatch_alarm_firehose_incoming_records" {
  for_each = local.multiplier_rate
  alarm_name                = "${var.environment_prefix_variable}-firehose-incoming-records-${each.key}"
  alarm_description         = "${local.alarm_description_text} ${each.key} of the RecordsPerSecondLimit"
  comparison_operator       = "GreaterThanThreshold"
  evaluation_periods        = 5
  datapoints_to_alarm       = 3
  threshold                 = each.value
  tags                      = var.tags
  treat_missing_data        = "ignore" 
  actions_enabled           = true
  insufficient_data_actions = []
  alarm_actions             = [aws_sns_topic.sns_topic_alerts.arn]
  ok_actions                = [aws_sns_topic.sns_topic_alerts.arn]

  metric_query {
    id          = "e1"
    expression  = "(m1/PERIOD(m1))/FILL(m2, REPEAT)"
    label       = "Percentage Record Limit"
    return_data = "true"
  }

  metric_query {
    id = "m1"

    metric {
      metric_name = "IncomingRecords"
      namespace   = "AWS/Firehose"
      period      = 60
      stat        = "Sum"
      unit        = "Count"

      dimensions = {
        DeliveryStreamName = local.firehose_stream_name
      }
    }
  }

  metric_query {
    id = "m2"

    metric {
      metric_name = "RecordsPerSecondLimit"
      namespace   = "AWS/Firehose"
      period      = 60
      stat        = "Minimum"
      unit        = "Count"

      dimensions = {
        DeliveryStreamName = local.firehose_stream_name
      }
    }
  }
}