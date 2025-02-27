import base64
import gzip
import json
from src.mbtp_splunk_cloudwatch_transformation.handler import (
    get_record_size,
    process_cloudwatch_log_record,
    process_records,
    split_cwl_record,
)

config = {
    "log_groups": {
        "TEST_LOG_GROUP": {
            "accounts": [123456789012],
            "index": "TEST_INDEX",
            "log_streams": [
                {"regex": "^TEST_LOG_STREAM$", "sourcetype": "TEST_SOURCETYPE"}
            ],
        }
    },
    "sourcetypes": {"TEST_SOURCETYPE": {}},
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
        "time": 1510109208016,
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
        "time": 1510109208017,
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


def test_process_records():
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
