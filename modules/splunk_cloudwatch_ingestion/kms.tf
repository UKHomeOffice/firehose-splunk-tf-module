resource "aws_kms_key" "firehose_key" {
  # checkov:skip=CKV2_AWS_64:Key policy to be introduced later
  description             = "KMS key for Kinesis Firehose S3 backup encryption"
  deletion_window_in_days = 10
  enable_key_rotation     = true
}
