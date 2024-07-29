variable "env" {
  description = "Environment name"
  type        = string
  default = "dev"
}

variable "profile" {
  description = "AWS profile name"
  type        = string
  default = "terraform"
}

variable "region" {
  description = "AWS region"
  type        = string
  default = "ap-northeast-2"
}

variable "cidr_block" {
  description = "CIDR block"
  type        = string
  default = "172.16.0.0/16"
}

variable "enable_dns_support" {
  description = "Enable DNS support"
  type        = bool
  default = true
}

variable "enable_dns_hostnames" {
  description = "Enable DNS hostnames"
  type        = bool
  default = true
}

variable "zone1" {
  description = "First availability zone"
  type        = string
  default       = "ap-northeast-2a"
}

variable "zone2" {
  description = "Second availability zone"
  type        = string
  default       = "ap-northeast-2b"
}

variable "eks_name" {
  description = "EKS cluster name"
  type        = string
  default       = "my-cluster"
}

variable "eks_version" {
  description = "EKS cluster version"
  type        = string
  default = "1.30"
}

variable "addons" {
  description = "List of add-ons for the EKS cluster"
  type = list(object({
    name    = string
    version = string
  }))
  default = [
    {
      name    = "vpc-cni"
      version = "v1.18.2-eksbuild.1"
    },
    {
      name    = "coredns"
      version = "v1.11.1-eksbuild.9"
    },
    {
      name    = "kube-proxy"
      version = "v1.30.0-eksbuild.3"
    }
  ]
}
