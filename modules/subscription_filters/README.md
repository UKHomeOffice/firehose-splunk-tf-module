# MBTP Splunk Cloudwatch Ingestion - Subscription Filter Module

<!-- BEGIN_TF_DOCS -->
## Requirements

No requirements.

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | n/a |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [aws_cloudwatch_log_subscription_filter.cloudwatch_log_filter](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_log_subscription_filter) | resource |
| [aws_iam_policy.cloudwatch_to_firehose_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_policy) | resource |
| [aws_iam_role.cloudwatch_to_firehose](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_iam_role_policy_attachment.attach_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_policy_document.cloudwatch_to_firehose_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_account_id"></a> [account\_id](#input\_account\_id) | The aws account where the firehose is hosted. | `number` | n/a | yes |
| <a name="input_config_disk_path"></a> [config\_disk\_path](#input\_config\_disk\_path) | The path to config file on disk. | `string` | n/a | yes |
| <a name="input_environment_prefix_variable"></a> [environment\_prefix\_variable](#input\_environment\_prefix\_variable) | Environment prefix provided by the importing module in order to ensure resources have unique names. | `string` | n/a | yes |
| <a name="input_firehose_arn"></a> [firehose\_arn](#input\_firehose\_arn) | The ARN of the Firehose delivery stream. | `string` | n/a | yes |
| <a name="input_tags"></a> [tags](#input\_tags) | A map of additional tags to associate with the resource | `map(string)` | `{}` | no |

## Outputs

No outputs.
<!-- END_TF_DOCS -->
