
# The policy that grants an entity permission to assume the role.
# Used to access AWS resources that you might not normally have access to.
# The role that Amazon EKS will use to create AWS reousrces for Kubernetes clusters


data "aws_iam_policy_document" "cluster-role-assume-policy" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type = "Service"
      # for IAM role to be used only by EKS services
      identifiers = ["eks.amazonaws.com"]
    }
    effect = "Allow"
  }
}

# This role is assumed by the EKS control plane to manage the cluster.
resource "aws_iam_role" "eks_cluster_role" {
  name               = "eks-cluster-role"
  assume_role_policy = data.aws_iam_policy_document.cluster-role-assume-policy.json
}

# attach AmazonEKSClusterPolicy to this role
resource "aws_iam_role_policy_attachment" "eks_cluster_role_policy" {
  role       = aws_iam_role.eks_cluster_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
}

# TODO Security Group


resource "aws_eks_cluster" "my-cluster" {
  name     = var.eks_name
  version  = var.eks_version
  role_arn = aws_iam_role.eks_cluster_role.arn

  vpc_config {
    # cluster's Kubernetes private API server endpoint is disabled
    endpoint_private_access = false

    # cluster's Kubernetes public API server endpoint is enabled
    endpoint_public_access = true

    # EKS requires at least two private subnets in different Availability Zones
    subnet_ids = [
      aws_subnet.private_zone1.id,
      aws_subnet.private_zone2.id,
    ]
    # list of security group ids to associate with the cluster
    # security_group_ids = [aws_security_group.eks_cluster_sg.id]
  }

  access_config {
    authentication_mode = "API"
    # to deploy helm chart and plain yaml
    bootstrap_cluster_creator_admin_permissions = true
  }

  depends_on = [aws_iam_role_policy_attachment.eks_cluster_role_policy]
}

# To use some Amazon EKS add-ons(vpc-cni), or to enable individual Kubernetes workloads
# to have specific AWS Identity and Access Management (IAM) permissions,
# create an IAM OpenID Connect (OIDC) provider for your cluster.
# You only need to create an IAM OIDC provider for your cluster once.

# If an add-on(vpc-cni) requires IAM permissions,
# then you must have an IAM OpenID Connect (OIDC) provider for your cluster.


# Ensure the EKS cluster is created before reading its data

data "aws_eks_cluster" "my-cluster" {
  name       = aws_eks_cluster.my-cluster.name
  depends_on = [aws_eks_cluster.my-cluster]
}

# manage permissions to applications attach policies to node directly pod will also have same permissions
# >>> OR create OIDC provider which will allow granting IAM permissions based on the serviceaccount used by the pod.

# Create an OIDC provider for the EKS cluster

data "tls_certificate" "eks_cluster_ca" {
  url = aws_eks_cluster.my-cluster.identity[0].oidc[0].issuer
}

resource "aws_iam_openid_connect_provider" "oidc_provider" {
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = [data.tls_certificate.eks_cluster_ca.certificates[0].sha1_fingerprint]
  url             = aws_eks_cluster.my-cluster.identity[0].oidc[0].issuer
}


# The vpc-cni plugin requires you to attach the following IAM policies to an IAM role:
# AmazonEKS_CNI_Policy

data "aws_iam_policy_document" "vpc_cni_assume_role_policy" {
  # statement {
  #   actions = ["sts:AssumeRole"]

  #   principals {
  #     identifiers = ["eks.amazonaws.com"]
  #     type        = "Service"
  #   }
  # }
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    effect  = "Allow"

    # condition {
    #   test     = "StringEquals"
    #   variable = "${replace(aws_iam_openid_connect_provider.oidc_provider.url, "https://", "")}:aud"
    #   values   = ["sts.amazonaws.com"]
    # }

    condition {
      test     = "StringEquals"
      variable = "${replace(aws_iam_openid_connect_provider.oidc_provider.url, "https://", "")}:sub"
      values   = ["system:serviceaccount:kube-system:aws-node"]
    }

    principals {
      identifiers = [aws_iam_openid_connect_provider.oidc_provider.arn]
      type        = "Federated"
    }
  }
}

# This role is specifically for the VPC CNI add-on, which handles networking for the EKS cluster.
# : attach AmazonEKS_CNI_Policy to this role

resource "aws_iam_role" "eks_cni_role" {
  name               = "eks-cni-role"
  assume_role_policy = data.aws_iam_policy_document.vpc_cni_assume_role_policy.json
}

resource "aws_iam_role_policy_attachment" "eks_cni_role_policy" {
  role       = aws_iam_role.eks_cni_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
}

# Output to be used in 11-aws-lbc.sh
output "vpc_cni_role_arn" {
  value = aws_iam_role.eks_cni_role.arn
}

resource "aws_eks_addon" "addons" {
  for_each                    = { for addon in var.addons : addon.name => addon }
  cluster_name                = aws_eks_cluster.my-cluster.name
  addon_name                  = each.value.name
  addon_version               = each.value.version
  resolve_conflicts_on_update = "OVERWRITE"

  depends_on = [aws_eks_node_group.private_nodes]

  service_account_role_arn = each.value.name == "vpc-cni" ? aws_iam_role.eks_cni_role.arn : null
}
