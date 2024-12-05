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

  actions_enabled = true
  alarm_actions = [aws_sns_topic.sns_topic_alerts.arn]
  ok_actions = [aws_sns_topic.sns_topic_alerts.arn]
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

  actions_enabled = true
  alarm_actions = [aws_sns_topic.sns_topic_alerts.arn]
  ok_actions = [aws_sns_topic.sns_topic_alerts.arn]
}

# CloudWatch alarm for SQS Queue Messages
resource "aws_cloudwatch_metric_alarm" "sqs_message_backlog" {
  for_each = toset([
    "${var.environment_prefix_variable}-${var.retry_sqs_name}",
    "${var.environment_prefix_variable}-${var.retry_dlq_name}"
  ])
  alarm_name                = "${each.value}-sqs_message_backlog_alarm"
  alarm_description         = "Triggers when there are more than 3 messages in the SQS queue."
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
    QueueName = each.value
  }

  actions_enabled = true
  alarm_actions = [aws_sns_topic.sns_topic_alerts.arn]
  ok_actions = [aws_sns_topic.sns_topic_alerts.arn]
}


# CloudWatch Alarm for Firehose Splunk Processing
resource "aws_cloudwatch_metric_alarm" "cloudwatch_alarm_firehose_splunk_processing" {
  alarm_name                = "${var.environment_prefix_variable}-firehose_splunk"
  alarm_description         = "Alarm if the Kinesis Firehose to Splunk stops sending data to Splunk"
  metric_name               = "DeliveryToSplunk.Success"
  namespace                 = "AWS/Firehose"
  statistic                 = "Average"
  comparison_operator       = "LessThanThreshold"
  evaluation_periods        = 1
  period                    = 300
  threshold                 = 1
  insufficient_data_actions = []
  tags                      = var.tags

  actions_enabled = true
  alarm_actions = [aws_sns_topic.sns_topic_alerts.arn]
  ok_actions = [aws_sns_topic.sns_topic_alerts.arn]
  dimensions = {
    DeliveryStreamName = local.firehose_stream_name
  }
}
