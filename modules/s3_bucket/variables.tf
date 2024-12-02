variable "bucket_name" {
  description = "The name of the S3 bucket"
  type        = string
}

variable "approved_s3_resources" {
  description = "List of resource ARNs which can PUT into S3"
  default     = []
  type        = list(string)
}
