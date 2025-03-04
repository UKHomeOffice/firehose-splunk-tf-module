# Data Formats

## Cloudwatch

### Successful Path

#### Transformation Lambda

Logs from Cloudwatch are submitted to the transformation lambda as batches of compressed logs. The triggering event in the `handler` function is in the following format:

```json
{
  "invocationId": "7aadc5cf-37dd-41e3-b554-18037ca12014",
  "deliveryStreamArn": "arn:aws:firehose:eu-west-2:104046402197:deliverystream/ho-it-sec-test-fh-cw2splunk",
  "region": "eu-west-2",
  "records": [
    {
      "recordId": "shardId-00000000000000000000000000000000000000000000000000000000000000000000000000000000000049661076801743525278240094264031636452583540156006400002000000000000",
      "approximateArrivalTimestamp": 1741077318783,
      "data": "H4sIAAAAAAAAA7VQPW/DIBDd+zOYbYkvG8hmqW6mTs5WoshxiYtqgwW4URXlvxdoU3Vrl0qIu+Px7r07cJFgVt73o9q9L0qCjQT3za45PLZd12xbCQoJ7NkolyEEKaQ1hRgJlqHJjltn1yWjL7bUofRqKIPyoRzO2C/Tal5zqc14Y3TBqX7OlIQc/FcdUb8e/eD0ErQ1D3oKyvn47+n33uVPpgT7T6X2TZmQO8Q59XOWJJxjRjCqKamIiPNUtGYci5hgTCGnUEAIK4EoQbgWqGLpleDsL+i4rdDPaWDEKIKMEcRjVnzvMYtcpJTgZG0Km3Qde5fCNZ7in71Uf/CCb2b2V3D3AQKdp+sFAgAA"
    },
    {
      "recordId": "shardId-00000000000000000000000000000000000000000000000000000000000000000000000000000000000049661076801743525278240094265250233678755086501549178882000000000000",
      "approximateArrivalTimestamp": 1741077320014,
      "data": "H4sIAAAAAAAA/4WQTWuDQBiE/8ucFfYr7rt7C9Tm1JO51RCM3dql6oq7NhTxv5ckFHrrcYZ5ZmBWDC7GpnPH78nB4ml/3J9fyqraH0pkCNfRzbDgTDFVKCa40cjQh+4wh2WCxUfIfcqja/PkYsrbq4hTv4yfd+nH7pGu0uyaARY39xwfKkNcLrGd/ZR8GJ99n9wcYV//7cz/cjjdF8ovN6YbvcK/wUISCS0FL3RhChKC74yRxCSjgktGO0FSkJRMESkjSDKllFZEyJD84GJqhgmWa8WZ1pKbQsvs9ytYrDXeQ6hha1yaucaG7bT9AJJuWDVNAQAA"
    }
  ]
}
```

The `data` field in each `record` is a Base64 encoded string which has also been compressed with gzip. If we convert it back to a readable JSON object, we get:

```json
{
  "messageType": "DATA_MESSAGE",
  "owner": "104046402197",
  "logGroup": "ho-it-sec-test-cw2splunk-testing",
  "logStream": "test_stream",
  "subscriptionFilters": ["ho-it-sec-test-cw2splunk-testing-subscription"],
  "logEvents": [
    {
      "id": "38827321643539404546782904522408409000591431269157240832",
      "timestamp": 1741077318174,
      "message": "{\"foo\":\"bar\"}"
    },
    {
      "id": "38827321643539404546782904522408409000591431269157240832",
      "timestamp": 1741077318175,
      "message": "{\"foo\":\"bar2\"}"
    }
  ]
}
```

Once the log has been processed, it is returned as a JSON string. If there are multiple `logEvents` in the array, they will be strings separated by a new line. If the logs are dropped by the `deny_regex` they will be excluded from the response here.

```json
"{\"index\": \"mbtp_secopsit_testenv_ops\", \"sourcetype\": \"_json\", \"time\": \"1741077318174\", \"host\": \"arn:aws:firehose:eu-west-2:104046402197:deliverystream/ho-it-sec-test-fh-cw2splunk\", \"source\": \"ho-it-sec-test-cw2splunk-testing\", \"fields\": {\"aws_account_id\": \"104046402197\", \"cw_log_stream\": \"test_stream\"}, \"event\": {\"foo\": \"bar\"}}
{\"index\": \"mbtp_secopsit_testenv_ops\", \"sourcetype\": \"_json\", \"time\": \"1741077318175\", \"host\": \"arn:aws:firehose:eu-west-2:104046402197:deliverystream/ho-it-sec-test-fh-cw2splunk\", \"source\": \"ho-it-sec-test-cw2splunk-testing\", \"fields\": {\"aws_account_id\": \"104046402197\", \"cw_log_stream\": \"test_stream\"}, \"event\": {\"foo\": \"bar2\"}}"
```

The result is then Base64 encoded and put into a firehose record:

```json
{
  "data": "eyJpbmRleCI6ICJtYnRwX3NlY29wc2l0X3Rlc3RlbnZfb3BzIiwgInNvdXJjZXR5cGUiOiAiX2pzb24iLCAidGltZSI6ICIxNzQxMDc3MzE4MTc0IiwgImhvc3QiOiAiYXJuOmF3czpmaXJlaG9zZTpldS13ZXN0LTI6MTA0MDQ2NDAyMTk3OmRlbGl2ZXJ5c3RyZWFtL2hvLWl0LXNlYy10ZXN0LWZoLWN3MnNwbHVuayIsICJzb3VyY2UiOiAiaG8taXQtc2VjLXRlc3QtY3cyc3BsdW5rLXRlc3RpbmciLCAiZmllbGRzIjogeyJhd3NfYWNjb3VudF9pZCI6ICIxMDQwNDY0MDIxOTciLCAiY3dfbG9nX3N0cmVhbSI6ICJ0ZXN0X3N0cmVhbSJ9LCAiZXZlbnQiOiB7ImZvbyI6ICJiYXIifX0KeyJpbmRleCI6ICJtYnRwX3NlY29wc2l0X3Rlc3RlbnZfb3BzIiwgInNvdXJjZXR5cGUiOiAiX2pzb24iLCAidGltZSI6ICIxNzQxMDc3MzE4MTc1IiwgImhvc3QiOiAiYXJuOmF3czpmaXJlaG9zZTpldS13ZXN0LTI6MTA0MDQ2NDAyMTk3OmRlbGl2ZXJ5c3RyZWFtL2hvLWl0LXNlYy10ZXN0LWZoLWN3MnNwbHVuayIsICJzb3VyY2UiOiAiaG8taXQtc2VjLXRlc3QtY3cyc3BsdW5rLXRlc3RpbmciLCAiZmllbGRzIjogeyJhd3NfYWNjb3VudF9pZCI6ICIxMDQwNDY0MDIxOTciLCAiY3dfbG9nX3N0cmVhbSI6ICJ0ZXN0X3N0cmVhbSJ9LCAiZXZlbnQiOiB7ImZvbyI6ICJiYXIyIn19Cg==",
  "result": "Ok",
  "recordId": "shardId-00000000000000000000000000000000000000000000000000000000000000000000000000000000000049661076801743525278240094264031636452583540156006400002000000000000"
}
```

This then gets returned from the lambda in a list of other records:

```json
{
  "records": [
    {
      "data": "eyJpbmRleCI6ICJtYnRwX3NlY29wc2l0X3Rlc3RlbnZfb3BzIiwgInNvdXJjZXR5cGUiOiAiX2pzb24iLCAidGltZSI6ICIxNzQxMDc3MzE4MTc0IiwgImhvc3QiOiAiYXJuOmF3czpmaXJlaG9zZTpldS13ZXN0LTI6MTA0MDQ2NDAyMTk3OmRlbGl2ZXJ5c3RyZWFtL2hvLWl0LXNlYy10ZXN0LWZoLWN3MnNwbHVuayIsICJzb3VyY2UiOiAiaG8taXQtc2VjLXRlc3QtY3cyc3BsdW5rLXRlc3RpbmciLCAiZmllbGRzIjogeyJhd3NfYWNjb3VudF9pZCI6ICIxMDQwNDY0MDIxOTciLCAiY3dfbG9nX3N0cmVhbSI6ICJ0ZXN0X3N0cmVhbSJ9LCAiZXZlbnQiOiB7ImZvbyI6ICJiYXIifX0KeyJpbmRleCI6ICJtYnRwX3NlY29wc2l0X3Rlc3RlbnZfb3BzIiwgInNvdXJjZXR5cGUiOiAiX2pzb24iLCAidGltZSI6ICIxNzQxMDc3MzE4MTc1IiwgImhvc3QiOiAiYXJuOmF3czpmaXJlaG9zZTpldS13ZXN0LTI6MTA0MDQ2NDAyMTk3OmRlbGl2ZXJ5c3RyZWFtL2hvLWl0LXNlYy10ZXN0LWZoLWN3MnNwbHVuayIsICJzb3VyY2UiOiAiaG8taXQtc2VjLXRlc3QtY3cyc3BsdW5rLXRlc3RpbmciLCAiZmllbGRzIjogeyJhd3NfYWNjb3VudF9pZCI6ICIxMDQwNDY0MDIxOTciLCAiY3dfbG9nX3N0cmVhbSI6ICJ0ZXN0X3N0cmVhbSJ9LCAiZXZlbnQiOiB7ImZvbyI6ICJiYXIyIn19Cg==",
      "result": "Ok",
      "recordId": "shardId-00000000000000000000000000000000000000000000000000000000000000000000000000000000000049661076801743525278240094264031636452583540156006400002000000000000"
    },
    {
      "data": "eyJpbmRleCI6ICJtYnRwX3NlY29wc2l0X3Rlc3RlbnZfb3BzIiwgInNvdXJjZXR5cGUiOiAiX2pzb24iLCAidGltZSI6ICIxNzQxMDc3MzE5NjczIiwgImhvc3QiOiAiYXJuOmF3czpmaXJlaG9zZTpldS13ZXN0LTI6MTA0MDQ2NDAyMTk3OmRlbGl2ZXJ5c3RyZWFtL2hvLWl0LXNlYy10ZXN0LWZoLWN3MnNwbHVuayIsICJzb3VyY2UiOiAiaG8taXQtc2VjLXRlc3QtY3cyc3BsdW5rLXRlc3RpbmciLCAiZmllbGRzIjogeyJhd3NfYWNjb3VudF9pZCI6ICIxMDQwNDY0MDIxOTciLCAiY3dfbG9nX3N0cmVhbSI6ICJ0ZXN0X3N0cmVhbSJ9LCAiZXZlbnQiOiB7ImZvbyI6ICJiYXIifX0=",
      "result": "Ok",
      "recordId": "shardId-00000000000000000000000000000000000000000000000000000000000000000000000000000000000049661076801743525278240094265250233678755086501549178882000000000000"
    }
  ]
}
```

#### Transformation Lambda - Large Records

Once the records are decompressed and converted into Splunk formatted events, they are checked for size limitations.

Logs that are too large cannot be returned by the transformation lambda.

For large Cloudwatch records, the original Firehose record will be makkred as **Dropped** and the `logEvents` field will be split in half and reingested using the Firehose API.
