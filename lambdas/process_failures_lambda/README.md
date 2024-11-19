# MBTP Splunk Cloudwatch Process Failures

This lambda function is expected to be run manually to re-process any files that end up in the `failed/` prefix in S3.

It should only be run, once any issues with the Splunk HEC/firehose have been resolved.

Upon triggering in the AWS console, it will:

- Redrive any SQS messages which may be on the re-ingestion SQS queue.
- Move any files from `failed/` to `retries/` in the S3 bucket.

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
