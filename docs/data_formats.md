# Data Formats

## Cloudwatch

### Successful Path

Logs from Cloudwatch are submitted to the transformation lambda in the below format.

```json
{
  "invocationId": "7d996c21-3c33-4dc2-9d3d-4f212157b032",
  "deliveryStreamArn": "arn:aws:firehose:eu-west-2:104046402197:deliverystream/ho-it-sec-test-fh-cw2splunk",
  "region": "eu-west-2",
  "records": [
    {
      "recordId": "shardId-00000000000000000000000000000000000000000000000000000000000000000000000000000000000049661071185880666403463533812464436510279596978340888578000000000000",
      "approximateArrivalTimestamp": 1741018141414,
      "data": "H4sIAAAAAAAA/4WQMWvDMBSE/8vNNrwnKZaszVA3Uydnq0NwXNUVjS1jyQ0l5L+XJBS6dbzjvju4C0YXYze43ffsYPFU7arDS9001bZGhnCe3AILJkWqUCS41MhwCsN2CesMi4+Q+5RH1+fJxZT3ZxHn0zp93qWfhke6SYvrRljc3EN8qAxxPcZ+8XPyYXr2p+SWCPv6b2f+l8P+vlB/uSnd6Av8GyykMaIg4nKjNKlCE5XMipUUUm9EKaU0Qm9kSdJoNpJIS+JCCmRIfnQxdeMMy1oxsWHFwlD2+xUsLi3eQ2hhWxy7pcUV1/31BzrzJUFNAQAA"
    }
  ]
}
```

The `data` field in each record is a Base64 encoded string which has also been compressed with gzip. If we convert it back to a readable blob, we get:

```json
{
  "messageType": "DATA_MESSAGE",
  "owner": "104046402197",
  "logGroup": "ho-it-sec-test-cw2splunk-testing",
  "logStream": "test_stream",
  "subscriptionFilters": ["ho-it-sec-test-cw2splunk-testing-subscription"],
  "logEvents": [
    {
      "id": "38826001954704670091141432375293338275390387183007301632",
      "timestamp": 1741018141280,
      "message": "{\"foo\":\"bar\"}"
    }
  ]
}
```
