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

### Failed Path - Transformation Lambda Failure

If the Transformation Lambda has an error (bad configuration or buggy code) then firehose will place the failed logs in the S3 bucket.

When a file is placed in the bucket, it triggers the Reingestion lambda function.

The Reingestion lambda is triggered with a SQS event with a S3 event inside.

```json
{
  "Records": [
    {
      "messageId": "c1f6586e-124e-4215-ad4a-62fad29fa267",
      "receiptHandle": "AQEBWzs1fCIZvV2d2w3WYeURPdcv76SDIP0ou7UH22DZy2Lp+s2udTpyHX85244EmSbA/9Vez7YRzpT7svF74uxkhQrr40UnbPxnqb/xjJ/TbZnIeNfVJjF7z59ycxw0KrfBHkBC48YrOn36M75Icg4g6nCHxC3vDQYGycGFU9By40wdrSE9bwwondjXB++6CbUR0aH1GATqWRez9b1EjANdH2VREiLiDn9zH4kYqJte4pcfpLqU3QAS2IAQnDt3Cb8UZVBBUzL43G2OjfSSJc3/Ls8q+bmabBGwr4IgBnKi3s0hO3HHZy+bAQ2ngGfusqmJ5pveGsK/zV73r4+2egHE2xYJUMnlde7J4LLjsXCiwC0nX3KqiIpvdcYM6KyuliavVIYB+9Jv22Y8o/F+7Ssn+oEUPb2Ev/wBcNm66aARorU=",
      "body": "{\"Records\":[{\"eventVersion\":\"2.1\",\"eventSource\":\"aws:s3\",\"awsRegion\":\"eu-west-2\",\"eventTime\":\"2025-03-04T11:51:08.487Z\",\"eventName\":\"ObjectCreated:Put\",\"userIdentity\":{\"principalId\":\"AWS:AROARQONGDKK7VF25MK3Y:AWSFirehoseToS3\"},\"requestParameters\":{\"sourceIPAddress\":\"10.63.13.234\"},\"responseElements\":{\"x-amz-request-id\":\"P9QT6CFMQCMKPW0S\",\"x-amz-id-2\":\"f2eHarD4SXSGYZyh35nY4ijYhl5ge6aVuyedtjJ+Y1ZrZIZ7ReqUu1+8E/osMHDbxGRxNtlb/I8wWb7+QBySe4PP9rLRGJh6\"},\"s3\":{\"s3SchemaVersion\":\"1.0\",\"configurationId\":\"tf-s3-queue-20250303142857274500000006\",\"bucket\":{\"name\":\"ew2.ho.it.np.sec.splunk-firehose\",\"ownerIdentity\":{\"principalId\":\"AIRAEMCN28RPY\"},\"arn\":\"arn:aws:s3:::ew2.ho.it.np.sec.splunk-firehose\"},\"object\":{\"key\":\"ho-it-sec-test/retries/processing-failed/2025/03/04/11/ho-it-sec-test-fh-cw2splunk-9-2025-03-04-11-48-32-c7cc019b-af51-412d-b641-b3b44ceb3d87\",\"size\":677,\"eTag\":\"d51acdfdb2f835debf14d4ee9a271ecc\",\"versionId\":\"9PkggzWYCsWgaiuTj6g8yqel5BJQO_SL\",\"sequencer\":\"0067C6E92C64732325\"}}}]}",
      "attributes": {
        "ApproximateReceiveCount": "1",
        "SentTimestamp": "1741089069412",
        "SenderId": "AROA5LVVW55647YN4KVPZ:S3-PROD-END",
        "ApproximateFirstReceiveTimestamp": "1741089129412"
      },
      "messageAttributes": {},
      "md5OfBody": "474daf6cbf272edf12bc7932ab08c8fd",
      "eventSource": "aws:sqs",
      "eventSourceARN": "arn:aws:sqs:eu-west-2:104046402197:ho-it-sec-test-cw2splunk-retry-sqs",
      "awsRegion": "eu-west-2"
    }
  ]
}
```

The file is downloaded from S3 using the object details in the `body` of the SQS message.

The file's content which was populated by firehose contains a JSON string. Multiple events can be within the same file on different lines.

The `rawData` field is a Base64 and Gzip compressed JSON string of the oringinal firehose record.

```json
"{\"rawData\":\"H4sIAAAAAAAA/4WQS2uDQACE/8ucFfblvm5CbU49mVsNwditXaquuGtDEf97SUKhtx5nmG8GZsPoYmx7d/yeHSyeymN5fqnqujxUyBCuk1tgQYkgQgrCqFHIMIT+sIR1hsVHyH3Ko+vy5GLKuyuL87BOn3fpp/6RrtPi2hEWN/ccHypDXC+xW/ycfJie/ZDcEmFf/+3M/3I43ReqLzelG73Bv8GCa81UoQkjVGsiCs6JNEYaZjiXwhTcEGIkU5JoapiiQilhuJLIkPzoYmrHGZYqQYnWhjLOafb7FSy2Bu8hNLANLu3SYMd+2n8AV7S7kU0BAAA=\",\"errorCode\":\"Lambda.FunctionError\",\"errorMessage\":\"The Lambda function was successfully invoked but it returned an error result.\",\"attemptsMade\":4,\"arrivalTimestamp\":1741088912364,\"attemptEndingTimestamp\":1741089007666,\"lambdaARN\":\"arn:aws:lambda:eu-west-2:104046402197:function:ho-it-sec-test-cw2splunk-transformation-lambda:$LATEST\"}"
```

After processing the `rawData` field, we get:

```json
{
  "messageType": "DATA_MESSAGE",
  "owner": "104046402197",
  "logGroup": "ho-it-sec-test-cw2splunk-testing",
  "logStream": "test_stream",
  "subscriptionFilters": ["ho-it-sec-test-cw2splunk-testing-subscription"],
  "logEvents": [
    {
      "id": "38827580201880453306996929336495390096276081927147749376",
      "timestamp": 1741088912331,
      "message": "{\"foo\":\"bar\"}"
    }
  ]
}
```

This record is sent back into Firehose, but has a `firehose_errors` field applied:

```json
{
  "messageType": "DATA_MESSAGE",
  "owner": "104046402197",
  "logGroup": "ho-it-sec-test-cw2splunk-testing",
  "logStream": "test_stream",
  "subscriptionFilters": ["ho-it-sec-test-cw2splunk-testing-subscription"],
  "logEvents": [
    {
      "id": "38827580201880453306996929336495390096276081927147749376",
      "timestamp": 1741088912331,
      "message": "{\"foo\":\"bar\"}"
    }
  ],
  "fields": {
    "firehose_errors": 1
  }
}
```

Once the `firehose_errors` goes over the threshold (3 by default), the event will be placed in the S3 bucket.

The message in the bucket is in the same format as it was when Firehose sent it in originally, but it has the `firehose_errors` field removed so that when it's next processed it does not automatically go back to failures.
