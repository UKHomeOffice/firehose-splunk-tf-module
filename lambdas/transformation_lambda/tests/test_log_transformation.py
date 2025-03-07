import pytest
from src.mbtp_splunk_cloudwatch_transformation.handler import (
    is_json,
    load_firehose_record_data,
    transform_event_to_splunk,
)


def test_is_json():
    assert is_json("foo") is False
    assert is_json('{"foo":"bar"}') is True


def test_load_firehose_record_data():
    assert load_firehose_record_data(
        "H4sIABSPQGcC/6tWSsvPV7JSSkosUqoFAO/1K/4NAAAA"
    ) == {"foo": "bar"}


def test_load_json_base64():
    assert load_firehose_record_data("eyJmb28iOiJiYXIifQo=") == {"foo": "bar"}


test_cwlog_transformations = [
    (
        {"message": "HI", "timestamp": "1234"},
        {},
        '"HI"',
    ),
    (
        {"message": '{"foo": "bar"}', "timestamp": "1234"},
        {},
        '{"foo": "bar"}',
    ),
    (
        {"message": "TEST PII TEST", "timestamp": "1234"},
        {"redact_regexes": ["blah", ".*(PII).*"]},
        '"TEST ***REDACTED BY SOURCETYPE.redact_regexes.1*** TEST"',
    ),
    (
        {"message": '{"foo": "TEST PII TEST"}', "timestamp": "1234"},
        {"redact_regexes": [".*(PII).*"]},
        '{"foo": "TEST ***REDACTED BY SOURCETYPE.redact_regexes.0*** TEST"}',
    ),
    (
        {"message": "TEST LOG IS ALLOWED WHEN IN ALLOWLIST", "timestamp": "1234"},
        {"allowlist_regexes": [".*ALLOWED.*"], "redact_regexes": []},
        '"TEST LOG IS ALLOWED WHEN IN ALLOWLIST"',
    ),
    (
        {"message": "TEST LOG IS DENIED WHEN NOT IN ALLOWLIST", "timestamp": "1234"},
        {"allowlist_regexes": [".*ALLOWED.*"], "redact_regexes": []},
        None,
    ),
    (
        {"message": "TEST LOG IS ALLOWED WHEN NOT IN DENYLIST", "timestamp": "1234"},
        {"denylist_regexes": [".*DENIED.*"], "redact_regexes": []},
        '"TEST LOG IS ALLOWED WHEN NOT IN DENYLIST"',
    ),
    (
        {"message": "TEST LOG IS DENIED WHEN IN DENYLIST TEST", "timestamp": "1234"},
        {"denylist_regexes": [".*DENIED.*"], "redact_regexes": []},
        None,
    ),
    (
        {
            "message": "TEST LOS IS DENIED WHEN IN DENYLIST BUT ALLOWED BY ALLOWLIST",
            "timestamp": "1234",
        },
        {
            "allowlist_regexes": [".*DENIED.*"],
            "denylist_regexes": [".*DENIED.*"],
            "redact_regexes": [],
        },
        None,
    ),
]


@pytest.mark.parametrize("event,sourcetype,expected_event", test_cwlog_transformations)
def test_transform_cw_to_splunk(event, sourcetype, expected_event):
    default_params = {
        "timestamp": event["timestamp"],
        "event": event["message"],
        "index": "INDEX",
        "sourcetype": sourcetype,
        "sourcetype_name": "SOURCETYPE",
        "firehose_arn": "ARN",
        "account_id": "ACCOUNT_ID",
        "source": "LOG_GROUP",
        "log_stream": "LOG_STREAM",
    }
    expected_result = None
    if expected_event is not None:
        expected_result = (
            '{"index": "INDEX", "sourcetype": "SOURCETYPE", "time": "'
            + event["timestamp"]
            + '", "host": "ARN", "source": "LOG_GROUP", "fields": {"aws_account_id": "ACCOUNT_ID", "cw_log_stream": "LOG_STREAM"}, "event": '
            + expected_event
            + "}"
        )

    assert transform_event_to_splunk(**default_params) == expected_result


test_event_transformations = [
    (
        {"time": "1234", "source": "aws.tag"},
        {},
        '{"time": "1234", "source": "aws.tag"}',
    ),
    (
        {
            "time": "1234",
            "source": "aws.tag",
            "detail": {"changed-tag-keys": ["TEST PII TEST"]},
        },
        {"redact_regexes": ["blah", ".*(PII).*"]},
        '{"time": "1234", "source": "aws.tag", "detail": {"changed-tag-keys": ["TEST ***REDACTED BY SOURCETYPE.redact_regexes.1*** TEST"]}}',
    ),
    (
        {
            "time": "1234",
            "source": "aws.tag",
            "detail": {"changed-tag-keys": ["TEST ALLOWED TEST"]},
        },
        {"allowlist_regexes": [".*ALLOWED.*"], "redact_regexes": []},
        '{"time": "1234", "source": "aws.tag", "detail": {"changed-tag-keys": ["TEST ALLOWED TEST"]}}',
    ),
    (
        {
            "time": "1234",
            "source": "aws.tag",
            "detail": {
                "changed-tag-keys": ["TEST LOG IS DENIED WHEN NOT IN ALLOWLIST"]
            },
        },
        {"allowlist_regexes": [".*ALLOWED.*"], "redact_regexes": []},
        None,
    ),
    (
        {
            "time": "1234",
            "source": "aws.tag",
            "detail": {
                "changed-tag-keys": ["TEST LOG IS ALLOWED WHEN NOT IN DENYLIST"]
            },
        },
        {"denylist_regexes": [".*DENIED.*"], "redact_regexes": []},
        '{"time": "1234", "source": "aws.tag", "detail": {"changed-tag-keys": ["TEST LOG IS ALLOWED WHEN NOT IN DENYLIST"]}}',
    ),
    (
        {
            "time": "1234",
            "source": "aws.tag",
            "detail": {
                "changed-tag-keys": ["TEST LOG IS DENIED WHEN IN DENYLIST TEST"]
            },
        },
        {"denylist_regexes": [".*DENIED.*"], "redact_regexes": []},
        None,
    ),
    (
        {
            "time": "1234",
            "source": "aws.tag",
            "detail": {
                "changed-tag-keys": [
                    "TEST LOS IS DENIED WHEN IN DENYLIST BUT ALLOWED BY ALLOWLIST"
                ]
            },
        },
        {
            "allowlist_regexes": [".*DENIED.*"],
            "denylist_regexes": [".*DENIED.*"],
            "redact_regexes": [],
        },
        None,
    ),
]


@pytest.mark.parametrize("data,sourcetype,expected_event", test_event_transformations)
def test_transform_event_to_splunk(data, sourcetype, expected_event):
    default_params = {
        "timestamp": data["time"],
        "event": data,
        "index": "INDEX",
        "sourcetype": sourcetype,
        "sourcetype_name": "SOURCETYPE",
        "firehose_arn": "ARN",
        "account_id": "ACCOUNT_ID",
        "source": data["source"],
        "log_stream": "LOG_STREAM",
    }
    expected_result = None
    if expected_event is not None:
        expected_result = (
            '{"index": "INDEX", "sourcetype": "SOURCETYPE", "time": "'
            + data["time"]
            + '", "host": "ARN", "source": "'
            + data["source"]
            + '", "fields": {"aws_account_id": "ACCOUNT_ID", "cw_log_stream": "LOG_STREAM"}, "event": '
            + expected_event
            + "}"
        )

    assert transform_event_to_splunk(**default_params) == expected_result
