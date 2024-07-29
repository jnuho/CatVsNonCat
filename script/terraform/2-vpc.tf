// vpc
resource "aws_vpc" "main" {
  # CIDR block for the VPC
  cidr_block = var.cidr_block

  # Enables DNS hostnames for instances in the VPC
  # instances will receive DNS hostnames that can be resolved to their private IP addresses.

  # Required for EKS. Enables DNS support for the VPC
  enable_dns_support = var.enable_dns_support

  # Required for EKS. Enables DNS hostnames for instances in the VPC
  enable_dns_hostnames = var.enable_dns_hostnames

  tags = {
    "Name" = "${var.env}-main"
  }
}

# output "vpc_id" {
#   value = aws_vpc.main.id
#   description = "VPC id."
#   # Setting an output value as sensitive will mask it in the console output
#   sensitive = false
# }
