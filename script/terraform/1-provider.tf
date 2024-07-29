
# Configure the AWS Provider
# The AWS Provider can source credentials and other settings
# $HOME/.aws/config and $HOME/.aws/credentials
provider "aws" {
  profile = var.profile
  region  = var.region
}

# terraform version constraints
terraform {
  backend "s3" {
    bucket = "tfstate-s3-stage"
    key = "eks/terraform.tfstate"
    region="ap-northeast-2"
  }

  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "2.13.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
  }
}
