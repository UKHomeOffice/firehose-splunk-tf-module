# MBTP Splunk Cloudwatch Transformation

This lambda transforms incoming Cloudwatch Firehose events into Splunk HEC format.

It requires a config file which it can download from S3. The config file must use the following format:

```
log_groups:
  <FRIENDLY_NAME>:
    log_group: <LOG_GROUP_NAME>
    accounts:
      - <ACCOUNT_ID> # To allow cross account subscription filters
    index: <INDEX>
    log_streams:
      - regex: <LOG_STREAM_NAME_REGEX>
        sourcetype: <SOURCETYPE>
    subscription_filter: <SUBSCRIPTION_FILTER> # Optional. Default to allow all.
sourcetypes:
  <SOURCETYPE>:
    allowlist_regexes:
      - <REGEX_PATTERN_TO_ALLOW> # Optional. Defaults to allow all
    denylist_regexes:
      - <REGEX_PATTERN_TO_DENY> # Optional. Defaults to []
    redact_regexes:
      - <REGEX_PATTERN_TO_REDACT> # Optional. Defaults to []
events:
  <FRIENDLY_NAME>:
    event_source: <EVENT_SOURCE>
    accounts:
      - <ACCOUNT_ID> # To allow cross account subscription filters
    index: <INDEX>
    detail_types:
      - regex: <EVENT_DETAIL_REGEX>
        sourcetype: <SOURCETYPE>
    subscription_filter: <SUBSCRIPTION_FILTER> # Optional. Default to allow all.
```

## Development

### Set up

Make sure you have pdm installed (python3.12 -m pip install pdm), then to install dependencies:
`pdm install`

### Formatting the code

`pdm format`

### Linting the code

`pdm lint`

### Testing the code

`pdm test`

### Run all the checks

`pdm check`

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.
