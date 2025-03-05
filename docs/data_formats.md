# Data Formats

## Cloudwatch

### Successful Path

Logs from Cloudwatch are submitted to the Transformation lambda as batches of compressed logs. The triggering event in the `handler` function is in the following format:

```json
{
  "invocationId": "7aadc5cf-37dd-41e3-b554-18037ca12014",
  "deliveryStreamArn": "arn:aws:firehose:eu-west-2:000000000000:deliverystream/fh-cw2splunk",
  "region": "eu-west-2",
  "records": [
    {
      "recordId": "shardId-00000000000000000000000000000000000000000000000000000000000000000000000000000000000049661076801743525278240094264031636452583540156006400002000000000000",
      "approximateArrivalTimestamp": 1741077318783,
      "data": "H4sIAAAAAAAAA7VQy2rDMBC89zP27ID1siTfDHVyysm51SE4qWJEbctIckMx/veuEwqB0mP3tDuzzMzuDL0JoWnN4Ws0kMNrcShO+7Kqil0JCbjbYDzC6VMh3Ll25900InO50TB20/CxiSZEO7QPuoreND3yK3oKjymBMJ3DxdsxWjdsbReND5C//RbZPC/C8S5Zfpohrusz2HdUZkpRySjJOBNM85QLnklFNTaU8lTxVGNaoQlnhGaaCLmijGKMaPHq2PR4AJGcpFIyorBLfr6B8nMNV+dqyGs4N76GBZbk35zF3870bn1cXr4BHspOgqsBAAA="
    },
    {
      "recordId": "shardId-00000000000000000000000000000000000000000000000000000000000000000000000000000000000049661076801743525278240094265250233678755086501549178882000000000000",
      "approximateArrivalTimestamp": 1741077320014,
      "data": "H4sIAAAAAAAAA2VQTWvDMAy972fonIK/6o/cAst66im9LaWknRfMEjvYTssI+e9TVwaFCSGk9x4PSQuMNqWut4fvyUIJr9WhOu3rpql2NRQQbt5GhMlTIDyEfhfDPCFzubE0DbP/2mSbsvP9g25ytN2I/B09pcdUQJrP6RLdlF3wb27INiYo3/+bbJ6FcPy1rK/W57t8AfeBzlxrpjijUkkjNWN0awzXhBMtKZYt0xyTE6G1MNgRIYTCAdfIDq/O3YgHUCUoUYpTIxUv/r6B9ksLnyG0ULZw7mILK6zH9eUHq2NlHTABAAA="
    }
  ]
}
```

The `data` field in each `record` is a Base64 encoded string which has also been compressed with gzip. If we convert it back to a readable JSON object, we get:

```json
{
  "messageType": "DATA_MESSAGE",
  "owner": "000000000000",
  "logGroup": "cw2splunk-testing",
  "logStream": "test_stream",
  "subscriptionFilters": ["cw2splunk-testing-subscription"],
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
"{\"index\": \"mbtp_secopsit_testenv_ops\", \"sourcetype\": \"_json\", \"time\": \"1741077318174\", \"host\": \"arn:aws:firehose:eu-west-2:000000000000:deliverystream/fh-cw2splunk\", \"source\": \"cw2splunk-testing\", \"fields\": {\"aws_account_id\": \"000000000000\", \"cw_log_stream\": \"test_stream\"}, \"event\": {\"foo\": \"bar\"}}
{\"index\": \"mbtp_secopsit_testenv_ops\", \"sourcetype\": \"_json\", \"time\": \"1741077318175\", \"host\": \"arn:aws:firehose:eu-west-2:000000000000:deliverystream/fh-cw2splunk\", \"source\": \"cw2splunk-testing\", \"fields\": {\"aws_account_id\": \"000000000000\", \"cw_log_stream\": \"test_stream\"}, \"event\": {\"foo\": \"bar2\"}}"
```

The result is then Base64 encoded and put into a firehose record:

```json
{
  "data": "eyJpbmRleCI6ICJtYnRwX3NlY29wc2l0X3Rlc3RlbnZfb3BzIiwgInNvdXJjZXR5cGUiOiAiX2pzb24iLCAidGltZSI6ICIxNzQxMDc3MzE4MTc0IiwgImhvc3QiOiAiYXJuOmF3czpmaXJlaG9zZTpldS13ZXN0LTI6MDAwMDAwMDAwMDAwOmRlbGl2ZXJ5c3RyZWFtL2ZoLWN3MnNwbHVuayIsICJzb3VyY2UiOiAiY3cyc3BsdW5rLXRlc3RpbmciLCAiZmllbGRzIjogeyJhd3NfYWNjb3VudF9pZCI6ICIwMDAwMDAwMDAwMDAiLCAiY3dfbG9nX3N0cmVhbSI6ICJ0ZXN0X3N0cmVhbSJ9LCAiZXZlbnQiOiB7ImZvbyI6ICJiYXIifX0KeyJpbmRleCI6ICJtYnRwX3NlY29wc2l0X3Rlc3RlbnZfb3BzIiwgInNvdXJjZXR5cGUiOiAiX2pzb24iLCAidGltZSI6ICIxNzQxMDc3MzE4MTc1IiwgImhvc3QiOiAiYXJuOmF3czpmaXJlaG9zZTpldS13ZXN0LTI6MDAwMDAwMDAwMDAwOmRlbGl2ZXJ5c3RyZWFtL2ZoLWN3MnNwbHVuayIsICJzb3VyY2UiOiAiY3cyc3BsdW5rLXRlc3RpbmciLCAiZmllbGRzIjogeyJhd3NfYWNjb3VudF9pZCI6ICIwMDAwMDAwMDAwMDAiLCAiY3dfbG9nX3N0cmVhbSI6ICJ0ZXN0X3N0cmVhbSJ9LCAiZXZlbnQiOiB7ImZvbyI6ICJiYXIyIn19Cg==",
  "result": "Ok",
  "recordId": "shardId-00000000000000000000000000000000000000000000000000000000000000000000000000000000000049661076801743525278240094264031636452583540156006400002000000000000"
}
```

This then gets returned from the lambda in a list of other records:

```json
{
  "records": [
    {
      "data": "eyJpbmRleCI6ICJtYnRwX3NlY29wc2l0X3Rlc3RlbnZfb3BzIiwgInNvdXJjZXR5cGUiOiAiX2pzb24iLCAidGltZSI6ICIxNzQxMDc3MzE4MTc0IiwgImhvc3QiOiAiYXJuOmF3czpmaXJlaG9zZTpldS13ZXN0LTI6MDAwMDAwMDAwMDAwOmRlbGl2ZXJ5c3RyZWFtL2ZoLWN3MnNwbHVuayIsICJzb3VyY2UiOiAiY3cyc3BsdW5rLXRlc3RpbmciLCAiZmllbGRzIjogeyJhd3NfYWNjb3VudF9pZCI6ICIwMDAwMDAwMDAwMDAiLCAiY3dfbG9nX3N0cmVhbSI6ICJ0ZXN0X3N0cmVhbSJ9LCAiZXZlbnQiOiB7ImZvbyI6ICJiYXIifX0KeyJpbmRleCI6ICJtYnRwX3NlY29wc2l0X3Rlc3RlbnZfb3BzIiwgInNvdXJjZXR5cGUiOiAiX2pzb24iLCAidGltZSI6ICIxNzQxMDc3MzE4MTc1IiwgImhvc3QiOiAiYXJuOmF3czpmaXJlaG9zZTpldS13ZXN0LTI6MDAwMDAwMDAwMDAwOmRlbGl2ZXJ5c3RyZWFtL2ZoLWN3MnNwbHVuayIsICJzb3VyY2UiOiAiY3cyc3BsdW5rLXRlc3RpbmciLCAiZmllbGRzIjogeyJhd3NfYWNjb3VudF9pZCI6ICIwMDAwMDAwMDAwMDAiLCAiY3dfbG9nX3N0cmVhbSI6ICJ0ZXN0X3N0cmVhbSJ9LCAiZXZlbnQiOiB7ImZvbyI6ICJiYXIyIn19Cg==",
      "result": "Ok",
      "recordId": "shardId-00000000000000000000000000000000000000000000000000000000000000000000000000000000000049661076801743525278240094264031636452583540156006400002000000000000"
    },
    {
      "data": "e2luZGV4OiBtYnRwX3NlY29wc2l0X3Rlc3RlbnZfb3BzLCBzb3VyY2V0eXBlOiBfanNvbiwgdGltZTogMTc0MTA3NzMxOTY3MywgaG9zdDogYXJuOmF3czpmaXJlaG9zZTpldS13ZXN0LTI6MDAwMDAwMDAwMDAwOmRlbGl2ZXJ5c3RyZWFtL2ZoLWN3MnNwbHVuaywgc291cmNlOiBjdzJzcGx1bmstdGVzdGluZywgZmllbGRzOiB7YXdzX2FjY291bnRfaWQ6IDAwMDAwMDAwMDAwMCwgY3dfbG9nX3N0cmVhbTogdGVzdF9zdHJlYW19LCBldmVudDoge2ZvbzogYmFyfX0K",
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
      "receiptHandle": "",
      "body": "{\"Records\":[{\"eventVersion\":\"2.1\",\"eventSource\":\"aws:s3\",\"awsRegion\":\"eu-west-2\",\"eventTime\":\"2025-03-04T11:51:08.487Z\",\"eventName\":\"ObjectCreated:Put\",\"userIdentity\":{\"principalId\":\"AWS:AROARQONGDKK7VF25MK3Y:AWSFirehoseToS3\"},\"requestParameters\":{\"sourceIPAddress\":\"10.x.x.x\"},\"responseElements\":{\"x-amz-request-id\":\"P9QT6CFMQCMKPW0S\",\"x-amz-id-2\":\"f2eHarD4SXSGYZyh35nY4ijYhl5ge6aVuyedtjJ+Y1ZrZIZ7ReqUu1+8E/osMHDbxGRxNtlb/I8wWb7+QBySe4PP9rLRGJh6\"},\"s3\":{\"s3SchemaVersion\":\"1.0\",\"configurationId\":\"tf-s3-queue-20250303142857274500000006\",\"bucket\":{\"name\":\"splunk-firehose\",\"ownerIdentity\":{\"principalId\":\"AIRAEMCN28RPY\"},\"arn\":\"arn:aws:s3:::splunk-firehose\"},\"object\":{\"key\":\"retries/processing-failed/2025/03/04/11/fh-cw2splunk-9-2025-03-04-11-48-32-c7cc019b-af51-412d-b641-b3b44ceb3d87\",\"size\":677,\"eTag\":\"d51acdfdb2f835debf14d4ee9a271ecc\",\"versionId\":\"9PkggzWYCsWgaiuTj6g8yqel5BJQO_SL\",\"sequencer\":\"0067C6E92C64732325\"}}}]}",
      "attributes": {
        "ApproximateReceiveCount": "1",
        "SentTimestamp": "1741089069412",
        "SenderId": "AROA5LVVW55647YN4KVPZ:S3-PROD-END",
        "ApproximateFirstReceiveTimestamp": "1741089129412"
      },
      "messageAttributes": {},
      "md5OfBody": "474daf6cbf272edf12bc7932ab08c8fd",
      "eventSource": "aws:sqs",
      "eventSourceARN": "arn:aws:sqs:eu-west-2:000000000000:cw2splunk-retry-sqs",
      "awsRegion": "eu-west-2"
    }
  ]
}
```

The file is downloaded from S3 using the object details in the `body` of the SQS message.

The file's content which was populated by firehose contains a JSON string. Multiple events can be within the same file on different lines.

The `rawData` field is a Base64 and Gzip compressed JSON string of the oringinal firehose record.

```json
"{\"rawData\":\"H4sIAAAAAAAAA2WQy2rDMBBF9/0K431g9LCk0c4QN6uunF0JwUkVI2I9kOSEUPrvjZNNQ3fDzLln4DqT8zCa7S0avW637f6j6/t201Xh6k3SBDhwwYESlNUUxk0Kc9THK81xmv15VUwu1o/LqS/JDE4vm31+zFWeD/mYbCw2+Hc7FZOy/vwXXv3Fdouquxhf7qj90kwpKhsFFIhSwBvGQCAKpMiY4NgwBEBBpQBFkErCpeTIpHjxFOvurwYXNZGcgFJIKGPkhXHPIvR3fQqh1vVhSPXP7u0Xc0i6DiABAAA=\",\"errorCode\":\"Lambda.FunctionError\",\"errorMessage\":\"The Lambda function was successfully invoked but it returned an error result.\",\"attemptsMade\":4,\"arrivalTimestamp\":1741088912364,\"attemptEndingTimestamp\":1741089007666,\"lambdaARN\":\"arn:aws:lambda:eu-west-2:000000000000:function:cw2splunk-transformation-lambda:$LATEST\"}"
```

After processing the `rawData` field, we get:

```json
{
  "messageType": "DATA_MESSAGE",
  "owner": "000000000000",
  "logGroup": "cw2splunk-testing",
  "logStream": "test_stream",
  "subscriptionFilters": ["cw2splunk-testing-subscription"],
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
  "owner": "000000000000",
  "logGroup": "cw2splunk-testing",
  "logStream": "test_stream",
  "subscriptionFilters": ["cw2splunk-testing-subscription"],
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

### Failed Path - Splunk Failure

If Splunk has an error (outage or bad HEC token) then firehose will place the failed logs in the S3 bucket.

The process is the same as the one above, however this time, the `rawData` field is not gzip compressed anymore and each log represents
The `rawData` field is a Base64 and Gzip compressed JSON string of the oringinal firehose record.

```json
"{\"attemptsMade\":5,\"arrivalTimestamp\":1741163012000,\"errorCode\":\"Splunk.InvalidToken\",\"errorMessage\":\"The HEC token is invalid. Update Kinesis Firehose with a valid HEC token.\",\"attemptEndingTimestamp\":1741163168935,\"rawData\":\"e2luZGV4OiBtYnRwX3NlY29wc2l0X3Rlc3RlbnZfb3BzLCBzb3VyY2V0eXBlOiBfanNvbiwgdGltZTogMTc0MTE2MzAxMTkwOCwgaG9zdDogYXJuOmF3czpmaXJlaG9zZTpldS13ZXN0LTI6MDAwMDAwMDAwMDAwOmRlbGl2ZXJ5c3RyZWFtLzAwMDAwMDAwMDAwMGZoLWN3MnNwbHVuaywgc291cmNlOiAwMDAwMDAwMDAwMDBjdzJzcGx1bmstdGVzdGluZywgZmllbGRzOiB7YXdzX2FjY291bnRfaWQ6IDAwMDAwMDAwMDAwMCwgY3dfbG9nX3N0cmVhbTogdGVzdF9zdHJlYW19LCBldmVudDoge2ZvbzogYmFyfX0K\",\"EventId\":\"000000000000000065:shardId-00000000000000000000000000000000000000000000000000000000000000000000000000000000000049661076801743525278240143492676967389331374327438770178000000000000\"}"
```

After processing the `rawData` field, we get the post processed log:

```json
{
  "index": "mbtp_secopsit_testenv_ops",
  "sourcetype": "_json",
  "time": "1741163011908",
  "host": "arn:aws:firehose:eu-west-2:000000000000:deliverystream/fh-cw2splunk",
  "source": "cw2splunk-testing",
  "fields": {
    "aws_account_id": "000000000000",
    "cw_log_stream": "test_stream"
  },
  "event": { "foo": "bar" }
}
```

This record is sent back into Firehose, but has a `firehose_errors` field applied:

```json
{
  "index": "mbtp_secopsit_testenv_ops",
  "sourcetype": "_json",
  "time": "1741163011908",
  "host": "arn:aws:firehose:eu-west-2:000000000000:deliverystream/fh-cw2splunk",
  "source": "cw2splunk-testing",
  "fields": {
    "aws_account_id": "000000000000",
    "cw_log_stream": "test_stream"
  },
  "event": { "foo": "bar" },
  "fields": {
    "firehose_errors": 1
  }
}
```

## Event Bridge

Event Bridge messages are the same as Cloudwatch logs, however they have no gzip compression in place.

The `data` field in each `record` is a Base64 encoded string. If we convert it back to a readable JSON object, we get:

```json
{
  "version": "0",
  "id": "f7a99dda-3125-a9cb-11a1-b766af09ab0b",
  "detail-type": "Tag Change on Resource",
  "source": "aws.tag",
  "account": "000000000000",
  "time": "2025-03-05T11:05:23Z",
  "region": "eu-west-2",
  "resources": ["example:arn"],
  "detail": {
    "changed-tag-keys": ["example"],
    "service": "eks",
    "tag-policy-compliant": "true",
    "resource-type": "pod",
    "version-timestamp": "1741172723640",
    "version": 1,
    "tags": {
      "example": "foo"
    }
  }
}
```

Once the log has been processed, it is returned as a JSON string. If the logs are dropped by the `deny_regex` they will be excluded from the response here.

```json
"{\"index\": \"mbtp_secopsit_testenv_ops\", \"sourcetype\": \"aws:firehose:json\", \"time\": \"1741172723.0\", \"host\": \"arn:aws:firehose:eu-west-2:000000000000:deliverystream/fh-cw2splunk\", \"source\": \"aws.tag\", \"fields\": {\"aws_account_id\": \"000000000000\"}, \"event\": {\"version\": \"0\", \"id\": \"f7a99dda-3125-a9cb-11a1-b766af09ab0b\", \"detail-type\": \"Tag Change on Resource\", \"source\": \"aws.tag\", \"account\": \"000000000000\", \"time\": \"2025-03-05T11:05:23Z\", \"region\": \"eu-west-2\", \"resources\": [\"example:arn\"], \"detail\": {\"changed-tag-keys\": [\"example\"], \"service\": \"eks\", \"tag-policy-compliant\": \"true\", \"resource-type\": \"pod\", \"version-timestamp\": \"1741172723640\", \"version\": 1.0, \"tags\": {\"example\": \"foo\"}}}}"
```
