variable "bucket_name" {
  description = "The name of the S3 bucket"
  type        = string
}

variable "approved_s3_resources" {
  description = "List of resource ARNs which can PUT into S3"
  default     = []
  type        = list(string)
}

variable "account_id" {
  description = "IAM account ID"
  type        = string
}

variable "tags" {
  description = "A map of additional tags to associate with the resource"
  type        = map(string)
  default     = {}
}

variable "environment_prefix_variable" {
  description = "Environment prefix provided by the importing module in order to ensure resources have unique names."
  type        = string
}
