resource "aws_kms_key" "s3_kms_key" {
  description             = "KMS Key to protect S3 content"
  enable_key_rotation     = true
  rotation_period_in_days = 90
}

resource "aws_kms_alias" "s3_kms_alias" {
  name          = "alias/${var.bucket_name}-s3-key"
  target_key_id = aws_kms_key.s3_kms_key.key_id
}

resource "aws_kms_key_policy" "s3_kms_policy" {
  key_id = aws_kms_key.s3_kms_key.id
  policy = data.aws_iam_policy_document.s3_kms_policy.json
}

data "aws_iam_policy_document" "s3_kms_policy" {
  statement {
    sid    = "Enable IAM User Permissions"
    effect = "Allow"
    actions = [
      "kms:*",
    ]
    resources = [aws_kms_key.s3_kms_key.arn]
    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${var.account_id}:root"]
    }
  }
  statement {
    effect = "Deny"
    actions = [
      "kms:GenerateDataKey",
      "kms:Decrypt",
      "kms:Encrypt",
    ]
    resources = [aws_kms_key.s3_kms_key.arn]
    principals {
      type        = "AWS"
      identifiers = ["*"]
    }
    condition {
      test     = "StringNotEquals"
      variable = "aws:PrincipalArn"
      values = var.approved_s3_resources
    }
  }
}