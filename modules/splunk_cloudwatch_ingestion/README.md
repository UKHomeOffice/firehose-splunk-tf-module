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
| [aws_cloudwatch_log_group.process_failures_lambda_logs](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_log_group) | resource |
| [aws_cloudwatch_log_group.reingestion_lambda_logs](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_log_group) | resource |
| [aws_cloudwatch_log_group.transformation_lambda_logs](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_log_group) | resource |
| [aws_cloudwatch_log_stream.firehose_log_stream](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_log_stream) | resource |
| [aws_iam_policy.lambda_transformation_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_policy) | resource |
| [aws_iam_policy.process_failures_lambda_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_policy) | resource |
| [aws_iam_policy.reingestion_lambda_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_policy) | resource |
| [aws_iam_role.kinesis_firehose_lambda](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_iam_role.kinesis_firehose_role](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_iam_role.process_failures_lambda](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_iam_role.reingestion_lambda](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_iam_role_policy_attachment.kinesis_fh_role_attachment](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.kinesis_firehose_lambda_default](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.lambda_policy_role_attachment](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.process_failures_lambda](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.process_failures_lambda_default](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.reingestion_lambda](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.reingestion_lambda_default](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_kinesis_firehose_delivery_stream.kinesis_firehose](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kinesis_firehose_delivery_stream) | resource |
| [aws_kms_alias.firehose_key_alias](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_alias) | resource |
| [aws_kms_key.firehose_key](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_key) | resource |
| [aws_kms_key_policy.firehose_key_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_key_policy) | resource |
| [aws_lambda_event_source_mapping.reingestion_lambda_trigger](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_event_source_mapping) | resource |
| [aws_lambda_function.firehose_lambda_process_failures](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_function) | resource |
| [aws_lambda_function.firehose_lambda_reingestion](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_function) | resource |
| [aws_lambda_function.firehose_lambda_transformation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_function) | resource |
| [aws_policy.kinesis_firehose_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/policy) | resource |
| [aws_s3_bucket_notification.bucket_notification](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_notification) | resource |
| [aws_sns_topic.sns_topic_alerts](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sns_topic) | resource |
| [aws_sns_topic_policy.s3_to_sns_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sns_topic_policy) | resource |
| [aws_sns_topic_subscription.subscription_to_failed_splunk_sns_topic](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sns_topic_subscription) | resource |
| [aws_sqs_queue.retry_notification_queue](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sqs_queue) | resource |
| [aws_sqs_queue.retry_sqs_dql](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sqs_queue) | resource |
| [aws_sqs_queue_policy.s3_sqs](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sqs_queue_policy) | resource |
| [null_resource.transformation_lambda_exporter](https://registry.terraform.io/providers/hashicorp/null/latest/docs/resources/resource) | resource |
| [archive_file.process_failures_lambda_function](https://registry.terraform.io/providers/hashicorp/archive/latest/docs/data-sources/file) | data source |
| [archive_file.reingestion_lambda_function](https://registry.terraform.io/providers/hashicorp/archive/latest/docs/data-sources/file) | data source |
| [archive_file.transformation_lambda_compressor](https://registry.terraform.io/providers/hashicorp/archive/latest/docs/data-sources/file) | data source |
| [aws_iam_policy_document.lambda_policy_doc](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_iam_policy_document.process_failures_lambda_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_iam_policy_document.reingestion_lambda_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_policy_document.kinesis_firehose_policy_document](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/policy_document) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_account_id"></a> [account\_id](#input\_account\_id) | The aws account id where the firehose is hosted. | `any` | n/a | yes |
| <a name="input_alerts_sns_topic_name"></a> [alerts\_sns\_topic\_name](#input\_alerts\_sns\_topic\_name) | Name of SNS topic to send alerts to | `string` | `"cw2splunk-alerts-sns"` | no |
| <a name="input_alerts_subscription_emails"></a> [alerts\_subscription\_emails](#input\_alerts\_subscription\_emails) | List of emails for people who need to be aware when a log event is moved ot the /failed prefix of the s3 bucket. | `list(string)` | `[]` | no |
| <a name="input_environment_prefix_variable"></a> [environment\_prefix\_variable](#input\_environment\_prefix\_variable) | Envirment prefix provided by the importing module in order to ensure resources have unique names. | `any` | n/a | yes |
| <a name="input_firehose_buffer"></a> [firehose\_buffer](#input\_firehose\_buffer) | https://www.terraform.io/docs/providers/aws/r/kinesis_firehose_delivery_stream.html#buffer_size | `number` | `1` | no |
| <a name="input_firehose_buffer_interval"></a> [firehose\_buffer\_interval](#input\_firehose\_buffer\_interval) | Buffer incoming data for the specified period of time, in seconds, before delivering it to the destination | `number` | `60` | no |
| <a name="input_firehose_log_group_name"></a> [firehose\_log\_group\_name](#input\_firehose\_log\_group\_name) | Name of the CloudWatch log group for Kinesis Firehose | `string` | `"cw2splunk-log-group"` | no |
| <a name="input_firehose_log_retention"></a> [firehose\_log\_retention](#input\_firehose\_log\_retention) | Log retention for the firehose cloudwatch logs | `number` | `30` | no |
| <a name="input_firehose_log_stream_name"></a> [firehose\_log\_stream\_name](#input\_firehose\_log\_stream\_name) | Name of the CloudWatch log stream for Kinesis Firehose CloudWatch log group | `string` | `"cw2splunk-logs"` | no |
| <a name="input_firehose_retry_duration"></a> [firehose\_retry\_duration](#input\_firehose\_retry\_duration) | How long Kinesis Data Firehose retries sending data to Splunk | `string` | `"60"` | no |
| <a name="input_firehose_role_name"></a> [firehose\_role\_name](#input\_firehose\_role\_name) | Name of IAM Role for the Kinesis Firehose | `string` | `"cw2splunk-fh-role"` | no |
| <a name="input_firehose_transform_buffer"></a> [firehose\_transform\_buffer](#input\_firehose\_transform\_buffer) | https://www.terraform.io/docs/providers/aws/r/kinesis_firehose_delivery_stream.html#buffer_size | `number` | `0.25` | no |
| <a name="input_firehose_transform_buffer_interval"></a> [firehose\_transform\_buffer\_interval](#input\_firehose\_transform\_buffer\_interval) | Buffer incoming data for the specified period of time, in seconds, before delivering it to the destination | `number` | `60` | no |
| <a name="input_hec_acknowledgment_timeout"></a> [hec\_acknowledgment\_timeout](#input\_hec\_acknowledgment\_timeout) | The amount of time, in seconds between 180 and 600, that Kinesis Firehose waits to receive an acknowledgment from Splunk after it sends it data. | `number` | `300` | no |
| <a name="input_hec_endpoint_type"></a> [hec\_endpoint\_type](#input\_hec\_endpoint\_type) | Splunk HEC endpoint type; `Raw` or `Event` | `string` | `"Event"` | no |
| <a name="input_hec_url"></a> [hec\_url](#input\_hec\_url) | Splunk Kinesis URL for submitting CloudWatch logs to splunk | `any` | n/a | yes |
| <a name="input_kms_key_name"></a> [kms\_key\_name](#input\_kms\_key\_name) | Name of KMS key for the Kinesis Firehose | `string` | `"cw2splunk-key"` | no |
| <a name="input_lambda_log_retention"></a> [lambda\_log\_retention](#input\_lambda\_log\_retention) | Log retention for the lambda cloudwatch logs | `number` | `30` | no |
| <a name="input_process_failures_lambda_memory_size"></a> [process\_failures\_lambda\_memory\_size](#input\_process\_failures\_lambda\_memory\_size) | The function execution memory limit at which Lambda should terminate the function. | `number` | `512` | no |
| <a name="input_process_failures_lambda_name"></a> [process\_failures\_lambda\_name](#input\_process\_failures\_lambda\_name) | Name of Lambda function to process any failures | `string` | `"cw2splunk-process-failures-lambda"` | no |
| <a name="input_process_failures_lambda_timeout"></a> [process\_failures\_lambda\_timeout](#input\_process\_failures\_lambda\_timeout) | The function execution time at which Lambda should terminate the function. | `number` | `900` | no |
| <a name="input_python_runtime"></a> [python\_runtime](#input\_python\_runtime) | Runtime version of python for Lambda functions | `string` | `"python3.12"` | no |
| <a name="input_region"></a> [region](#input\_region) | the AWS region where the firehose is running | `any` | n/a | yes |
| <a name="input_reingestion_lambda_memory_size"></a> [reingestion\_lambda\_memory\_size](#input\_reingestion\_lambda\_memory\_size) | The function execution memory limit at which Lambda should terminate the function. | `number` | `1536` | no |
| <a name="input_reingestion_lambda_name"></a> [reingestion\_lambda\_name](#input\_reingestion\_lambda\_name) | Name of Lambda function to try reingesting logs back into firehose | `string` | `"cw2splunk-reingestion-lambda"` | no |
| <a name="input_reingestion_lambda_timeout"></a> [reingestion\_lambda\_timeout](#input\_reingestion\_lambda\_timeout) | The function execution time at which Lambda should terminate the function. | `number` | `900` | no |
| <a name="input_retry_dlq_name"></a> [retry\_dlq\_name](#input\_retry\_dlq\_name) | Name of SQS DLQ queue that events get sent to if the reingestion lambda breaks | `string` | `"cw2splunk-retry-dlq"` | no |
| <a name="input_retry_sqs_name"></a> [retry\_sqs\_name](#input\_retry\_sqs\_name) | Name of SQS queue that reingestion events get sent to | `string` | `"cw2splunk-retry-sqs"` | no |
| <a name="input_s3_bucket_arn"></a> [s3\_bucket\_arn](#input\_s3\_bucket\_arn) | The arn of the bucket in which logs are stored when they fail being sent to splunk. | `any` | n/a | yes |
| <a name="input_s3_bucket_name"></a> [s3\_bucket\_name](#input\_s3\_bucket\_name) | The name of the bucket in which logs are stored when they fail being sent to splunk. | `any` | n/a | yes |
| <a name="input_s3_config_file_key"></a> [s3\_config\_file\_key](#input\_s3\_config\_file\_key) | Location of the key to find the config file in S3. | `any` | n/a | yes |
| <a name="input_s3_failed_prefix"></a> [s3\_failed\_prefix](#input\_s3\_failed\_prefix) | Prefix to store failed Firehose logs that failed to be reingested. | `string` | `"failed/"` | no |
| <a name="input_s3_kms_key_arn"></a> [s3\_kms\_key\_arn](#input\_s3\_kms\_key\_arn) | KMS Key ARN used to protect the S3 bucket. | `any` | n/a | yes |
| <a name="input_s3_retries_prefix"></a> [s3\_retries\_prefix](#input\_s3\_retries\_prefix) | Prefix to store failed Firehose logs that need reingesting. | `string` | `"retries/"` | no |
| <a name="input_splunk_hec_token"></a> [splunk\_hec\_token](#input\_splunk\_hec\_token) | splunk hec token for the index which logs should be forwarded to. | `any` | n/a | yes |
| <a name="input_tags"></a> [tags](#input\_tags) | A map of additional tags to associate with the resource | `map(string)` | `{}` | no |
| <a name="input_transformation_lambda_memory_size"></a> [transformation\_lambda\_memory\_size](#input\_transformation\_lambda\_memory\_size) | The function execution memory limit at which Lambda should terminate the function. | `number` | `1536` | no |
| <a name="input_transformation_lambda_name"></a> [transformation\_lambda\_name](#input\_transformation\_lambda\_name) | Name of Lambda function responsible for parsing messages heading to splunk | `string` | `"cw2splunk-transformation-lambda"` | no |
| <a name="input_transformation_lambda_timeout"></a> [transformation\_lambda\_timeout](#input\_transformation\_lambda\_timeout) | The function execution time at which Lambda should terminate the function. | `number` | `900` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_destination_firehose_arn"></a> [destination\_firehose\_arn](#output\_destination\_firehose\_arn) | cloudwatch log subscription filter - Firehose destination arn |
<!-- END_TF_DOCS -->
