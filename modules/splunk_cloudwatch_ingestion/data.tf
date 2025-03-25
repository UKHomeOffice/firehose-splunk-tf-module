locals {
  firehose_stream_name = "${var.environment_prefix_variable}-fh-cw2splunk"

  multiplier_rate = {
      "100%" : 1
      "80%" : 0.8
  }
  alarm_description_text = "Alarm when ${local.firehose_stream_name} Firehose reaches"
}
