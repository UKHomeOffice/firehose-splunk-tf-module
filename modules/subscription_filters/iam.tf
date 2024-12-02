resource "aws_iam_role" "cloudwatch_to_firehose" {
  name = "${var.environment_prefix_variable}-cloudwatch-to-firehose-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "logs.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
}


resource "aws_iam_policy" "cloudwatch_to_firehose_policy" {
  name        = "${var.environment_prefix_variable}-cloudwatch-to-firehose-policy"
  description = "Policy for CloudWatch Logs to send data to Firehose"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "firehose:PutRecord",
          "firehose:PutRecordBatch"
        ],
        Resource = var.firehose_arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "attach_policy" {
  role       = aws_iam_role.cloudwatch_to_firehose.name
  policy_arn = aws_iam_policy.cloudwatch_to_firehose_policy.arn
}