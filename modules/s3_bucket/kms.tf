resource "aws_kms_key" "s3_kms_key" {
  description             = "KMS Key to protect S3 content"
  enable_key_rotation     = true
  rotation_period_in_days = 90
}

resource "aws_kms_alias" "s3_kms_alias" {
  name          = "alias/${var.bucket_name}-s3-key"
  target_key_id = aws_kms_key.s3_kms_key.key_id
}