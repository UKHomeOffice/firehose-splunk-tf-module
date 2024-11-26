# Validate the AWS availability zones' names
# [TODO] Remove these when Terrafrom 0.9.x is released.
# The same functionality will be available through:
#  "data.aws_availability_zones.all.names"
# See https://github.com/hashicorp/terraform/pull/11482
#
data "aws_availability_zone" "a" {
  name = data.aws_availability_zones.all.names[0]
}

data "aws_availability_zone" "b" {
  name = data.aws_availability_zones.all.names[1]
}

data "aws_availability_zone" "c" {
  name = data.aws_availability_zones.all.names[2]
}