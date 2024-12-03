# MBTP Splunk Cloudwatch Ingestion - Splunk Cloudwatch Ingestion Module

<!-- BEGIN_TF_DOCS -->
## Requirements

No requirements.

## Providers

| Name | Version |
|------|---------|
| <a name="provider_archive"></a> [archive](#provider\_archive) | n/a |
| <a name="provider_aws"></a> [aws](#provider\_aws) | n/a |
| <a name="provider_null"></a> [null](#provider\_null) | n/a |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [aws_cloudwatch_log_group.firehose_log_group](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_log_group) | resource |
| [aws_cloudwatch_log_stream.firehose_log_stream](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_log_stream) | resource |
| [aws_iam_policy.kinesis_firehose_iam_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_policy) | resource |
| [aws_iam_policy.lambda_transform_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_policy) | resource |
| [aws_iam_policy.reingestion_lambda_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_policy) | resource |
| [aws_iam_policy.reprocess_failed_lambda_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_policy) | resource |
| [aws_iam_role.kinesis_firehose_lambda](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_iam_role.kinesis_firehose_role](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_iam_role.reingestion_lambda](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_iam_role.reprocess_failed_lambda](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_iam_role_policy_attachment.kinesis_fh_role_attachment](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.kinesis_firehose_lambda_default](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.lambda_policy_role_attachment](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.reingestion_lambda](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.reingestion_lambda_default](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.reprocess_failed_lambda](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.reprocess_failed_lambda_default](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_kinesis_firehose_delivery_stream.kinesis_firehose](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kinesis_firehose_delivery_stream) | resource |
| [aws_kms_key.firehose_key](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_key) | resource |
| [aws_kms_key_policy.firehose_key_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_key_policy) | resource |
| [aws_lambda_event_source_mapping.retry_lambda_trigger](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_event_source_mapping) | resource |
| [aws_lambda_function.firehose_lambda_reprocess_failed](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_function) | resource |
| [aws_lambda_function.firehose_lambda_retry](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_function) | resource |
| [aws_lambda_function.firehose_lambda_transform](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_function) | resource |
| [aws_s3_bucket_notification.bucket_notification](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_notification) | resource |
| [aws_sns_topic.sns_topic_failed_splunk_events](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sns_topic) | resource |
| [aws_sns_topic_policy.s3_to_sns_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sns_topic_policy) | resource |
| [aws_sns_topic_subscription.subscription_to_failed_splunk_sns_topic](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sns_topic_subscription) | resource |
| [aws_sqs_queue.retry_notification_queue](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sqs_queue) | resource |
| [aws_sqs_queue.retry_sqs_dql](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sqs_queue) | resource |
| [aws_sqs_queue_policy.s3_sqs](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sqs_queue_policy) | resource |
| [null_resource.lambda_exporter](https://registry.terraform.io/providers/hashicorp/null/latest/docs/resources/resource) | resource |
| [archive_file.lambda_compressor](https://registry.terraform.io/providers/hashicorp/archive/latest/docs/data-sources/file) | data source |
| [archive_file.reprocess_failed_lambda_function](https://registry.terraform.io/providers/hashicorp/archive/latest/docs/data-sources/file) | data source |
| [archive_file.retry_lambda_function](https://registry.terraform.io/providers/hashicorp/archive/latest/docs/data-sources/file) | data source |
| [aws_iam_policy_document.kinesis_firehose_policy_document](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_iam_policy_document.lambda_policy_doc](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_iam_policy_document.reingestion_lambda_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_iam_policy_document.reprocess_failed_lambda_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_account_id"></a> [account\_id](#input\_account\_id) | The aws account id where the firehose is hosted. | `any` | n/a | yes |
| <a name="input_cloudwatch_log_retention"></a> [cloudwatch\_log\_retention](#input\_cloudwatch\_log\_retention) | Log retention for the firehose cloudwatch logs | `number` | `30` | no |
| <a name="input_enable_fh_cloudwatch_logging"></a> [enable\_fh\_cloudwatch\_logging](#input\_enable\_fh\_cloudwatch\_logging) | Enable kinesis firehose CloudWatch logging. (It only logs errors) | `bool` | `true` | no |
| <a name="input_environment_prefix_variable"></a> [environment\_prefix\_variable](#input\_environment\_prefix\_variable) | Envirment prefix provided by the importing module in order to ensure resources have unique names. | `any` | n/a | yes |
| <a name="input_failed_lambda_function_timeout"></a> [failed\_lambda\_function\_timeout](#input\_failed\_lambda\_function\_timeout) | The function execution time at which Lambda should terminate the function. | `number` | `900` | no |
| <a name="input_failed_lambda_transform_memory_size"></a> [failed\_lambda\_transform\_memory\_size](#input\_failed\_lambda\_transform\_memory\_size) | The function execution memory limit at which Lambda should terminate the function. | `number` | `1536` | no |
| <a name="input_firehose_failures_bucket_arn"></a> [firehose\_failures\_bucket\_arn](#input\_firehose\_failures\_bucket\_arn) | The arn of the bucket in which logs are stored when they fail being sent to splunk. | `string` | `""` | no |
| <a name="input_firehose_failures_bucket_name"></a> [firehose\_failures\_bucket\_name](#input\_firehose\_failures\_bucket\_name) | The name of the bucket in which logs are stored when they fail being sent to splunk. | `string` | `""` | no |
| <a name="input_hec_acknowledgment_timeout"></a> [hec\_acknowledgment\_timeout](#input\_hec\_acknowledgment\_timeout) | The amount of time, in seconds between 180 and 600, that Kinesis Firehose waits to receive an acknowledgment from Splunk after it sends it data. | `number` | `300` | no |
| <a name="input_hec_endpoint_type"></a> [hec\_endpoint\_type](#input\_hec\_endpoint\_type) | Splunk HEC endpoint type; `Raw` or `Event` | `string` | `"Event"` | no |
| <a name="input_hec_url"></a> [hec\_url](#input\_hec\_url) | Splunk Kinesis URL for submitting CloudWatch logs to splunk | `any` | n/a | yes |
| <a name="input_kinesis_firehose_buffer"></a> [kinesis\_firehose\_buffer](#input\_kinesis\_firehose\_buffer) | https://www.terraform.io/docs/providers/aws/r/kinesis_firehose_delivery_stream.html#buffer_size | `number` | `1` | no |
| <a name="input_kinesis_firehose_buffer_interval"></a> [kinesis\_firehose\_buffer\_interval](#input\_kinesis\_firehose\_buffer\_interval) | Buffer incoming data for the specified period of time, in seconds, before delivering it to the destination | `number` | `60` | no |
| <a name="input_kinesis_firehose_iam_policy_name"></a> [kinesis\_firehose\_iam\_policy\_name](#input\_kinesis\_firehose\_iam\_policy\_name) | Name of the IAM Policy attached to IAM Role for the Kinesis Firehose | `string` | `"KinesisFH-Policy"` | no |
| <a name="input_kinesis_firehose_role_name"></a> [kinesis\_firehose\_role\_name](#input\_kinesis\_firehose\_role\_name) | Name of IAM Role for the Kinesis Firehose | `string` | `"SplunkKinesisFHRole"` | no |
| <a name="input_kinesis_firehose_transform_buffer"></a> [kinesis\_firehose\_transform\_buffer](#input\_kinesis\_firehose\_transform\_buffer) | https://www.terraform.io/docs/providers/aws/r/kinesis_firehose_delivery_stream.html#buffer_size | `number` | `0.25` | no |
| <a name="input_kinesis_firehose_transform_buffer_interval"></a> [kinesis\_firehose\_transform\_buffer\_interval](#input\_kinesis\_firehose\_transform\_buffer\_interval) | Buffer incoming data for the specified period of time, in seconds, before delivering it to the destination | `number` | `60` | no |
| <a name="input_log_stream_name"></a> [log\_stream\_name](#input\_log\_stream\_name) | Name of the CloudWatch log stream for Kinesis Firehose CloudWatch log group | `string` | `"SplunkDelivery"` | no |
| <a name="input_python_runtime"></a> [python\_runtime](#input\_python\_runtime) | Runtime version of python for Lambda function | `string` | `"python3.12"` | no |
| <a name="input_region"></a> [region](#input\_region) | the AWS region where the firehose is running | `any` | n/a | yes |
| <a name="input_retry_duration"></a> [retry\_duration](#input\_retry\_duration) | How long Kinesis Data Firehose retries sending data to Splunk | `string` | `"60"` | no |
| <a name="input_retry_lambda_function_timeout"></a> [retry\_lambda\_function\_timeout](#input\_retry\_lambda\_function\_timeout) | The function execution time at which Lambda should terminate the function. | `number` | `900` | no |
| <a name="input_retry_lambda_transform_memory_size"></a> [retry\_lambda\_transform\_memory\_size](#input\_retry\_lambda\_transform\_memory\_size) | The function execution memory limit at which Lambda should terminate the function. | `number` | `1536` | no |
| <a name="input_s3_backup_mode"></a> [s3\_backup\_mode](#input\_s3\_backup\_mode) | Defines how documents should be delivered to Amazon S3. Valid values are FailedEventsOnly and AllEvents. | `string` | `"FailedEventsOnly"` | no |
| <a name="input_s3_config_file_key"></a> [s3\_config\_file\_key](#input\_s3\_config\_file\_key) | Location of the key to find the config file in S3. | `any` | n/a | yes |
| <a name="input_s3_failed_prefix"></a> [s3\_failed\_prefix](#input\_s3\_failed\_prefix) | Prefix to store failed Firehose logs that failed to be reingested. | `string` | `"failed/"` | no |
| <a name="input_s3_kms_key_arn"></a> [s3\_kms\_key\_arn](#input\_s3\_kms\_key\_arn) | KMS Key ARN used to protect the S3 bucket. | `any` | n/a | yes |
| <a name="input_s3_retries_prefix"></a> [s3\_retries\_prefix](#input\_s3\_retries\_prefix) | Prefix to store failed Firehose logs that need reingesting. | `string` | `"retries/"` | no |
| <a name="input_sns_failed_splunk_subscription_emails"></a> [sns\_failed\_splunk\_subscription\_emails](#input\_sns\_failed\_splunk\_subscription\_emails) | List of emails for people who need to be aware when a log event is moved ot the /failed prefix of the s3 bucket. | `list(string)` | `[]` | no |
| <a name="input_splunk_hec_token"></a> [splunk\_hec\_token](#input\_splunk\_hec\_token) | splunk hec token for the index which logs should be forwarded to. | `any` | n/a | yes |
| <a name="input_tags"></a> [tags](#input\_tags) | A map of additional tags to associate with the resource | `map(string)` | `{}` | no |
| <a name="input_transform_lambda_function_timeout"></a> [transform\_lambda\_function\_timeout](#input\_transform\_lambda\_function\_timeout) | The function execution time at which Lambda should terminate the function. | `number` | `900` | no |
| <a name="input_transform_lambda_transform_memory_size"></a> [transform\_lambda\_transform\_memory\_size](#input\_transform\_lambda\_transform\_memory\_size) | The function execution memory limit at which Lambda should terminate the function. | `number` | `1536` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_destination_firehose_arn"></a> [destination\_firehose\_arn](#output\_destination\_firehose\_arn) | cloudwatch log subscription filter - Firehose destination arn |
<!-- END_TF_DOCS -->
