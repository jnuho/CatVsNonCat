variable "env" {
  description = "Environment name"
  type        = string
}

variable "profile" {
  description = "AWS profile name"
  type        = string
}

variable "region" {
  description = "AWS region"
  type        = string
}

variable "zone1" {
  description = "First availability zone"
  type        = string
}

variable "zone2" {
  description = "Second availability zone"
  type        = string
}

variable "eks_name" {
  description = "EKS cluster name"
  type        = string
}

variable "eks_version" {
  description = "EKS cluster version"
  type        = string
}

variable "addons" {
  type = list(object({
    name    = string
    version = string
  }))
}