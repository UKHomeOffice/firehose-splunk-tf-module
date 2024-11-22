# MBTP Splunk Cloudwatch Reingestion

This lambda function will be triggered by any files landing in the `retries/` prefix in the S3 bucket.

Upon triggering, it will:

- Download the file from S3
- Extract the failed logs
- Check how many time the have failed and either
  - Send them back to Firehose, or
  - Put them in S3 under the `failed` prefix

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
