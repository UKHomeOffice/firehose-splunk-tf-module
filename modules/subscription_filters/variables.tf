variable "firehose_arn" {
  description = "The ARN of the Firehose delivery stream."
  type        = string
}

variable "account_id" {
  description = "The aws account where the firehose is hosted."
  type        = number
}

variable "config_disk_path" {
  description = "The path to config file on disk."
  type        = string
}

variable "environment_prefix_variable" {
  description = "Environment prefix provided by the importing module in order to ensure resources have unique names."
  type        = string
}

variable "tags" {
  description = "A map of additional tags to associate with the resource"
  type        = map(string)
  default     = {}
}
