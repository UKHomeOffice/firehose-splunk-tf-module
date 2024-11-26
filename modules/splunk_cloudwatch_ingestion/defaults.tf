variable "region_shortnames" {
  type = map(string)

  default = {
    eu-west-1 = "ew1"
    eu-west-2 = "ew2"
    us-east-1 = "ue1"
  }
}