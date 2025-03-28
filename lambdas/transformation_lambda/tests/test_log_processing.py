import base64
import gzip
import json
from src.mbtp_splunk_cloudwatch_transformation.handler import (
    get_record_size,
    get_record_type,
    process_cloudwatch_log_record,
    process_eventbridge_event,
    process_records,
    split_cwl_record,
)

config = {
    "log_groups": {
        "test_config": {
            "log_group": "TEST_LOG_GROUP",
            "accounts": [123456789012],
            "index": "TEST_INDEX",
            "log_streams": [
                {"regex": "^TEST_LOG_STREAM$", "sourcetype": "TEST_SOURCETYPE"}
            ],
        }
    },
    "sourcetypes": {"TEST_SOURCETYPE": {"denylist_regexes": ["DROPME"]}},
    "events": {
        "test_config": {
            "event_source": "aws.tag",
            "accounts": [123456789012],
            "index": "TEST_INDEX",
            "detail_types": [
                {"regex": "Tag Change on .*", "sourcetype": "TEST_SOURCETYPE"}
            ],
        }
    },
}
data = {
    "messageType": "DATA_MESSAGE",
    "owner": "123456789012",
    "logGroup": "TEST_LOG_GROUP",
    "logStream": "TEST_LOG_STREAM",
    "subscriptionFilters": ["subscription_filter_name"],
    "logEvents": [
        {
            "id": "01234567890123456789012345678901234567890123456789012345",
            "timestamp": 1510109208016,
            "message": "log message 1",
        },
        {
            "id": "01234567890123456789012345678901234567890123456789012345",
            "timestamp": 1510109208017,
            "message": "log message 2",
        },
    ],
}
transformed_logs = [
    {
        "index": "TEST_INDEX",
        "sourcetype": "TEST_SOURCETYPE",
        "time": "1510109208016",
        "host": "ARN",
        "source": "TEST_LOG_GROUP",
        "fields": {
            "aws_account_id": "123456789012",
            "cw_log_stream": "TEST_LOG_STREAM",
        },
        "event": "log message 1",
    },
    {
        "index": "TEST_INDEX",
        "sourcetype": "TEST_SOURCETYPE",
        "time": "1510109208017",
        "host": "ARN",
        "source": "TEST_LOG_GROUP",
        "fields": {
            "aws_account_id": "123456789012",
            "cw_log_stream": "TEST_LOG_STREAM",
        },
        "event": "log message 2",
    },
]


def test_process_cloudwatch_log_record_good():
    expected_result = {
        "data": base64.b64encode(
            "\n".join([json.dumps(x) for x in transformed_logs]).encode()
        ).decode(),
        "result": "Ok",
        "recordId": "123",
    }
    assert process_cloudwatch_log_record(data, "123", "ARN", config) == expected_result


def test_process_cloudwatch_log_record_unknown_log_group():
    test_data = {
        "messageType": "DATA_MESSAGE",
        "owner": "123456789012",
        "logGroup": "BAD_LOG_GROUP",
        "logStream": "TEST_LOG_STREAM",
        "logEvents": [],
    }
    assert process_cloudwatch_log_record(test_data, "123", "ARN", config) == {
        "result": "Dropped",
        "recordId": "123",
    }


def test_process_cloudwatch_log_record_unknown_log_stream():
    test_data = {
        "messageType": "DATA_MESSAGE",
        "owner": "123456789012",
        "logGroup": "TEST_LOG_GROUP",
        "logStream": "BAD_LOG_STREAM",
        "logEvents": [],
    }
    assert process_cloudwatch_log_record(test_data, "123", "ARN", config) == {
        "result": "Dropped",
        "recordId": "123",
    }


def test_process_cloudwatch_log_record_unknown_account():
    test_data = {
        "messageType": "DATA_MESSAGE",
        "owner": "123",
        "logGroup": "TEST_LOG_GROUP",
        "logStream": "TEST_LOG_STREAM",
        "logEvents": [],
    }
    assert process_cloudwatch_log_record(test_data, "123", "ARN", config) == {
        "result": "Dropped",
        "recordId": "123",
    }


def test_process_cloudwatch_log_record_control_message():
    test_data = {"messageType": "CONTROL_MESSAGE"}
    assert process_cloudwatch_log_record(test_data, "123", "ARN", config) == {
        "result": "Dropped",
        "recordId": "123",
    }


def test_process_cloudwatch_log_record_unknown_message():
    test_data = {"messageType": "FOO"}
    assert process_cloudwatch_log_record(test_data, "123", "ARN", config) == {
        "result": "ProcessingFailed",
        "recordId": "123",
    }


def test_get_record_size():
    assert get_record_size({"foo": "bar"}) == 14


def test_process_records_cloudwatch():
    compressed_data = base64.b64encode(gzip.compress(json.dumps(data).encode()))
    test_records = [{"data": compressed_data, "recordId": "1"}]
    reingest_data = {
        "index": "TEST_INDEX",
        "sourcetype": "TEST_SOURCETYPE",
        "time": "1510109208016",
        "host": "ARN",
        "source": "TEST_LOG_GROUP",
        "fields": {
            "aws_account_id": "123456789012",
            "cw_log_stream": "TEST_LOG_STREAM",
        },
        "event": "log message 1",
    }
    reingest_record_compressed = base64.b64encode(
        gzip.compress(json.dumps(reingest_data).encode())
    )
    test_records.append({"data": reingest_record_compressed, "recordId": "2"})

    unknown_record_compressed = base64.b64encode(
        gzip.compress(json.dumps({"foo": "bar"}).encode())
    )
    test_records.append({"data": unknown_record_compressed, "recordId": "3"})

    assert process_records(test_records, "ARN", config) == [
        {
            "result": "Ok",
            "recordId": "1",
            "data": base64.b64encode(
                "\n".join([json.dumps(x) for x in transformed_logs]).encode()
            ).decode(),
        },
        {
            "result": "Ok",
            "recordId": "2",
            "data": base64.b64encode(json.dumps(reingest_data).encode()).decode(),
        },
        {"result": "ProcessingFailed", "recordId": "3"},
    ]


def test_split_cwl_record():
    result = [
        {
            "messageType": "DATA_MESSAGE",
            "owner": "123456789012",
            "logGroup": "TEST_LOG_GROUP",
            "logStream": "TEST_LOG_STREAM",
            "subscriptionFilters": ["subscription_filter_name"],
            "logEvents": [
                {
                    "id": "01234567890123456789012345678901234567890123456789012345",
                    "timestamp": 1510109208016,
                    "message": "log message 1",
                }
            ],
        },
        {
            "messageType": "DATA_MESSAGE",
            "owner": "123456789012",
            "logGroup": "TEST_LOG_GROUP",
            "logStream": "TEST_LOG_STREAM",
            "subscriptionFilters": ["subscription_filter_name"],
            "logEvents": [
                {
                    "id": "01234567890123456789012345678901234567890123456789012345",
                    "timestamp": 1510109208017,
                    "message": "log message 2",
                }
            ],
        },
    ]

    assert split_cwl_record(data) == [
        gzip.compress(json.dumps(r).encode()) for r in result
    ]


def test_get_record_type():
    assert (
        get_record_type(
            {
                "messageType": "foo",
                "logGroup": "foo",
                "owner": "bar",
                "logEvents": "bar",
                "one": "more",
            }
        )
    ) == "cloudwatch"

    assert (
        get_record_type(
            {
                "source": "foo",
                "detail-type": "bar",
                "one": "more",
            }
        )
    ) == "eventbridge"

    assert (
        get_record_type(
            {
                "index": "foo",
                "sourcetype": "bar",
                "event": "bar",
                "one": "more",
            }
        )
    ) == "splunk"

    assert (get_record_type({"one": "more"})) == None


def test_process_eventbridge_event_good():
    test_data = {
        "version": "0",
        "id": "0",
        "detail-type": "Tag Change on Resource",
        "source": "aws.tag",
        "account": "123456789012",
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
            "tags": {"example": "foo"},
        },
    }
    expected_result = {
        "data": base64.b64encode(
            json.dumps(
                {
                    "index": "TEST_INDEX",
                    "sourcetype": "TEST_SOURCETYPE",
                    "time": "1741172723.0",
                    "host": "ARN",
                    "source": "aws.tag",
                    "fields": {"aws_account_id": "123456789012"},
                    "event": test_data,
                }
            ).encode()
        ).decode(),
        "result": "Ok",
        "recordId": "123",
    }
    assert process_eventbridge_event(test_data, "123", "ARN", config) == expected_result


def test_process_eventbridge_event_unknown_source():
    test_data = {
        "version": "0",
        "id": "0",
        "detail-type": "Tag Change on Resource",
        "source": "aws.cheese",
        "account": "123456789012",
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
            "tags": {"example": "foo"},
        },
    }
    assert process_eventbridge_event(test_data, "123", "ARN", config) == {
        "result": "Dropped",
        "recordId": "123",
    }


def test_process_eventbridge_event_unknown_detail():
    test_data = {
        "version": "0",
        "id": "0",
        "detail-type": "blah",
        "source": "aws.tag",
        "account": "123456789012",
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
            "tags": {"example": "foo"},
        },
    }
    assert process_eventbridge_event(test_data, "123", "ARN", config) == {
        "result": "Dropped",
        "recordId": "123",
    }


def test_process_eventbridge_event_unknown_account():
    test_data = {
        "version": "0",
        "id": "0",
        "detail-type": "Tag Change on Resource",
        "source": "aws.tag",
        "account": "123456000000",
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
            "tags": {"example": "foo"},
        },
    }
    assert process_eventbridge_event(test_data, "123", "ARN", config) == {
        "result": "Dropped",
        "recordId": "123",
    }


def test_process_eventbridge_event_dropped_regex():
    test_data = {
        "version": "0",
        "id": "0",
        "detail-type": "Tag Change on Resource",
        "source": "aws.tag",
        "account": "123456789012",
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
            "tags": {"example": "DROPME"},
        },
    }
    assert process_eventbridge_event(test_data, "123", "ARN", config) == {
        "result": "Dropped",
        "recordId": "123",
    }


def test_process_records_eventbridge():
    test_data = {
        "version": "0",
        "id": "0",
        "detail-type": "Tag Change on Resource",
        "source": "aws.tag",
        "account": "123456789012",
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
            "tags": {"example": "foo"},
        },
    }
    input_data = base64.b64encode(json.dumps(test_data).encode())
    test_records = [{"data": input_data, "recordId": "1"}]

    assert process_records(test_records, "ARN", config) == [
        {
            "result": "Ok",
            "recordId": "1",
            "data": base64.b64encode(
                json.dumps(
                    {
                        "index": "TEST_INDEX",
                        "sourcetype": "TEST_SOURCETYPE",
                        "time": "1741172723.0",
                        "host": "ARN",
                        "source": "aws.tag",
                        "fields": {"aws_account_id": "123456789012"},
                        "event": test_data,
                    }
                ).encode()
            ).decode(),
        }
    ]
