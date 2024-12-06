output "bucket_name" {
  description = "The name of the S3 bucket"
  value       = aws_s3_bucket.failed_bucket.bucket
}

output "bucket_arn" {
  description = "The ARN of the S3 bucket"
  value       = aws_s3_bucket.failed_bucket.arn
}

output "kms_arn" {
  description = "The ARN of the KMS key protecting the S3 bucket"
  value       = aws_kms_key.s3_kms_key.arn
}
