import pytest
from src.mbtp_splunk_cloudwatch_transformation.handler import (
    is_json,
    load_json_gzip_base64,
    transform_cloudwatch_log_event,
)


def test_is_json():
    assert is_json("foo") is False
    assert is_json('{"foo":"bar"}') is True


def test_load_json_gzip_base64():
    assert load_json_gzip_base64("H4sIABSPQGcC/6tWSsvPV7JSSkosUqoFAO/1K/4NAAAA") == {
        "foo": "bar"
    }


test_log_transformations = [
    (
        {"message": "HI", "timestamp": 1234},
        {},
        '"event": "HI"',
    ),
    (
        {"message": '{"foo": "bar"}', "timestamp": 1234},
        {},
        '"event": {"foo": "bar"}',
    ),
    (
        {"message": "TEST PII TEST", "timestamp": 1234},
        {"redact_regexes": ["blah", ".*(PII).*"]},
        '"event": "TEST ***REDACTED BY SOURCETYPE.redact_regexes.1*** TEST"',
    ),
    (
        {"message": '{"foo": "TEST PII TEST"}', "timestamp": 1234},
        {"redact_regexes": [".*(PII).*"]},
        '"event": {"foo": "TEST ***REDACTED BY SOURCETYPE.redact_regexes.0*** TEST"}',
    ),
    (
        {"message": "TEST LOG IS ALLOWED WHEN IN ALLOWLIST", "timestamp": 1234},
        {"allowlist_regexes": [".*ALLOWED.*"], "redact_regexes": []},
        '"event": "TEST LOG IS ALLOWED WHEN IN ALLOWLIST"',
    ),
    (
        {"message": "TEST LOG IS DENIED WHEN NOT IN ALLOWLIST", "timestamp": 1234},
        {"allowlist_regexes": [".*ALLOWED.*"], "redact_regexes": []},
        None,
    ),
    (
        {"message": "TEST LOG IS ALLOWED WHEN NOT IN DENYLIST", "timestamp": 1234},
        {"denylist_regexes": [".*DENIED.*"], "redact_regexes": []},
        '"event": "TEST LOG IS ALLOWED WHEN NOT IN DENYLIST"',
    ),
    (
        {"message": "TEST LOG IS DENIED WHEN IN DENYLIST TEST", "timestamp": 1234},
        {"denylist_regexes": [".*DENIED.*"], "redact_regexes": []},
        None,
    ),
    (
        {
            "message": "TEST LOS IS DENIED WHEN IN DENYLIST BUT ALLOWED BY ALLOWLIST",
            "timestamp": 1234,
        },
        {
            "allowlist_regexes": [".*DENIED.*"],
            "denylist_regexes": [".*DENIED.*"],
            "redact_regexes": [],
        },
        None,
    ),
]


@pytest.mark.parametrize("event,sourcetype,expected_event", test_log_transformations)
def test_transform_cloudwatch_log_event(event, sourcetype, expected_event):
    default_params = {
        "index": "INDEX",
        "sourcetype_name": "SOURCETYPE",
        "firehose_arn": "ARN",
        "account_id": "ACCOUNT_ID",
        "log_group": "LOG_GROUP",
        "log_stream": "LOG_STREAM",
        "event": event,
        "sourcetype": sourcetype,
    }
    expected_result = None
    if expected_event is not None:
        expected_result = (
            '{"index": "INDEX", "sourcetype": "SOURCETYPE", "time": "1234", "host": "ARN", "source": "LOG_GROUP", "fields": {"aws_account_id": "ACCOUNT_ID", "cw_log_stream": "LOG_STREAM"}, '
            + expected_event
            + "}"
        )
    assert transform_cloudwatch_log_event(**default_params) == expected_result
