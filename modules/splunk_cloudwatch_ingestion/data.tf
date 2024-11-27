# Enforce Terraform version and define backend as S3
terraform {
  required_version = ">= 0.12.31"

  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region 
}