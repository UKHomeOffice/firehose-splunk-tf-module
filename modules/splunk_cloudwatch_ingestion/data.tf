locals {
  firehose_stream_name = "${var.environment_prefix_variable}-fh-cw2splunk"
  firehose_bytes_limit = 5242880
  firehose_put_requests_limit = 2000
  firehose_incoming_records_limit = 500000

  multiplier_rate = {
      "100%" : 1
      "80%" : 0.8
  }
  alarm_description_text = "Alarm when ${local.firehose_stream_name} Firehose reaches"
}
