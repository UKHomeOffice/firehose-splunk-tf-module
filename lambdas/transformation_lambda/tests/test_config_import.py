from os import environ
import io

import boto3
from botocore.response import StreamingBody

from botocore.stub import Stubber
import pytest
from ruamel.yaml import YAML
from src.mbtp_splunk_cloudwatch_transformation.handler import (
    InvalidConfigException,
    get_validated_config,
)


test_configs = [
    (
        "",
        True,
    ),
    (
        """hello: {}""",
        False,
    ),
    (
        """
log_groups: {}
sourcetypes: {}
""",
        False,
    ),
    (
        """
log_groups:
    test_config:
        log_group: LOG_GROUP_NAME
        accounts:
            - 123456
            - "456789"
        index: TEST_INDEX
        log_streams: 
            - regex: .*
              sourcetype: TEST_SOURCETYPE
sourcetypes: {}
""",
        False,
    ),
    (
        """
log_groups:
    test_config: {}
sourcetypes: {}
""",
        True,
    ),
    (
        """
log_groups:
    test_config:
        log_group: LOG_GROUP_NAME
        accounts:
            - 123456
            - "456789"
        index: TEST_INDEX
        log_streams: 
            - regex: .*
              sourcetype: TEST_SOURCETYPE
sourcetypes: 
    TEST_SOURCETYPE: {}
""",
        False,
    ),
    (
        """
log_groups:
    test_config:
        log_group: LOG_GROUP_NAME
        accounts:
            - 123456
            - "456789"
        index: TEST_INDEX
        log_streams: 
            - regex: .*
              sourcetype: TEST_SOURCETYPE
sourcetypes: 
    TEST_SOURCETYPE:
        allowlist_regexes:
            - .*
        denylist_regexes:
            - .*
        redact_regexes:
            - .*
events:
    test_config:
        event_source: EVENT_SOURCE
        accounts:
            - 00123456
            - "00456789"
        index: TEST_INDEX
        detail_types: 
            - regex: .*
              sourcetype: TEST_SOURCETYPE
""",
        False,
    ),
]


@pytest.mark.parametrize("test_config,error", test_configs)
def test_get_validated_config(test_config, error, mocker):
    mocked_s3_client = boto3.client("s3", region_name=environ["AWS_REGION"])
    s3_stubber = Stubber(mocked_s3_client)
    test_config = test_config.encode()

    s3_stubber.add_response(
        "get_object",
        {"Body": StreamingBody(io.BytesIO(test_config), len(test_config))},
        {"Bucket": "CONFIG_S3_BUCKET", "Key": "CONFIG_S3_KEY"},
    )
    s3_stubber.activate()
    mocker.patch(
        "src.mbtp_splunk_cloudwatch_transformation.handler.s3_client",
        new=mocked_s3_client,
    )

    if not error:
        yaml = YAML(typ="safe")
        test_config = yaml.load(test_config)
        for config_section in [
            test_config.get("log_groups", {}),
            test_config.get("events", {}),
        ]:
            for details in config_section.values():
                if "accounts" in details:
                    details["accounts"] = [
                        str(x).zfill(12) for x in details["accounts"]
                    ]

        assert get_validated_config() == test_config
    else:
        with pytest.raises(InvalidConfigException):
            get_validated_config()
