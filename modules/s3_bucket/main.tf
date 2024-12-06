
resource "aws_s3_bucket" "failed_bucket" {
  bucket = var.bucket_name
  tags   = var.tags
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

resource "aws_s3_bucket_policy" "failed_bucket_policy" {
  bucket = aws_s3_bucket.failed_bucket.bucket
  policy = data.aws_iam_policy_document.failed_bucket_policy.json
}

data "aws_iam_policy_document" "failed_bucket_policy" {
  statement {
    actions = ["*"]
    effect  = "Deny"
    resources = [
      "arn:aws:s3:::${var.bucket_name}/*"
    ]
    condition {
      test     = "StringNotEquals"
      variable = "aws:PrincipalArn"
      values   = var.approved_s3_resources
    }
  }
}
