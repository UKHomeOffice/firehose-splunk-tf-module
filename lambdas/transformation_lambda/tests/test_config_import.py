from os import environ
import io

import boto3
from botocore.response import StreamingBody

from botocore.stub import Stubber
import pytest
import yaml
from src.mbtp_splunk_cloudwatch_transformation.handler import (
    InvalidConfigException,
    get_validated_config,
)


test_configs = [
    (
        """hello: {}""",
        True,
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
    LOG_GROUP_NAME:
        accounts:
            - 123456
            - 456789
        index: TEST_INDEX
        log_streams: 
            - regex: .*
              sourcetype: TEST_SOURCETYPE
sourcetypes: {}
""",
        True,
    ),
    (
        """
log_groups:
    LOG_GROUP_NAME:
        accounts:
            - 123456
            - 456789
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
    LOG_GROUP_NAME:
        accounts:
            - "123456"
            - 456789
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
""",
        False,
    ),
    (
        """
log_groups:
    LOG_GROUP_NAME:
        accounts:
            - 123456
            - 456789
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
        assert get_validated_config() == yaml.safe_load(test_config)
    else:
        with pytest.raises(InvalidConfigException):
            get_validated_config()
