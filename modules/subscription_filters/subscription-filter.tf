resource "aws_cloudwatch_log_subscription_filter" "cloudwatch_log_filter" {
  for_each = tomap({
    for log_group_name, details in local.config["log_groups"] :
    log_group_name => details
    if contains(details["accounts"], tonumber(var.account))
  })

  name            = "${each.key}-subscription"
  log_group_name  = each.key
  destination_arn = var.firehose_arn
  filter_pattern  = lookup(each.value, "subscription_filter", " ")
  role_arn        = aws_iam_role.cloudwatch_to_firehose.arn
}
