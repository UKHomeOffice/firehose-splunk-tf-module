
resource "aws_s3_bucket" "failed_bucket" {
  bucket = var.bucket_name


}

resource "aws_s3_bucket_versioning" "failed_bucket" {
  bucket = aws_s3_bucket.failed_bucket.bucket
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "failed_bucket" {
  bucket = aws_s3_bucket.failed_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.s3_kms_key.arn
      sse_algorithm     = "aws:kms"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "failed_bucket" {
  bucket                  = aws_s3_bucket.failed_bucket.bucket
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

output "bucket_name" {
  value = aws_s3_bucket.failed_bucket.bucket
}