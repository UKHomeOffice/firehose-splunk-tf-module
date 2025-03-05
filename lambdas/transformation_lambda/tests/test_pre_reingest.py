import base64
import gzip
import json
from unittest import mock
from src.mbtp_splunk_cloudwatch_transformation.handler import (
    work_out_records_to_reingest,
)


def b64compress(data):
    return base64.b64encode(gzip.compress(json.dumps(data).encode()))


def test_work_out_records_to_reingest():
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

    event = {
        "records": [
            {"data": b64compress(data)},
            {"data": b64compress(data)},
            {"data": b64compress(data)},
            {"data": b64compress(data)},
        ]
    }
    records = [
        {"result": "Ok", "recordId": "1", "data": ""},
        {"result": "Ok", "recordId": "2", "data": ""},
        {"result": "Ok", "recordId": "3", "data": ""},
        {"result": "Dropped", "recordId": "4", "data": ""},
    ]
    # Each record is 45 bytes so 100 bytes max should cause one to be reingested
    assert work_out_records_to_reingest(event, records, 100) == [[{"Data": mock.ANY}]]
    assert records[2]["result"] == "Dropped"
    assert "data" not in records[2]


def test_work_out_records_to_reingest_single_too_big():
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
            }
        ],
    }

    event = {
        "records": [
            {"data": b64compress(data)},
        ]
    }
    records = [
        {"result": "Ok", "recordId": "1", "data": ""},
    ]
    assert work_out_records_to_reingest(event, records, 1) == []
    assert records[0]["result"] == "ProcessingFailed"
    assert "data" not in records[0]


def test_work_out_records_to_reingest_multiple_too_big():
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

    event = {
        "records": [
            {"data": b64compress(data)},
        ]
    }
    records = [
        {"result": "Ok", "recordId": "1", "data": ""},
    ]
    assert work_out_records_to_reingest(event, records, 1) == [
        [{"Data": mock.ANY}, {"Data": mock.ANY}]
    ]
    assert records[0]["result"] == "Dropped"
    assert "data" not in records[0]


def test_work_out_records_to_reingest_too_big_not_cloudwatch():
    data = {"index": "foo", "sourcetype": "bar", "event": {}}

    event = {
        "records": [
            {"data": base64.b64encode(json.dumps(data).encode()).decode()},
        ]
    }
    records = [
        {"result": "Ok", "recordId": "1", "data": ""},
    ]
    assert work_out_records_to_reingest(event, records, 1) == []
    assert records[0]["result"] == "ProcessingFailed"
    assert "data" not in records[0]
