# REPLACE OIDC!!
# Run agent on every single node on cluster
# resource "aws_eks_addon" "pod_identity" {
#   cluster_name  = aws_eks_cluster.my-cluster.name
#   addon_name    = "eks-pod-identity-agent"
#   addon_version = "v1.3.0-eksbuild.1"
#   depends_on    = [aws_eks_node_group.private_nodes]
# }

# data "aws_iam_policy_document" "aws_lbc" {
#   statement {
#     effect = "Allow"

#     principals {
#       type        = "Service"
#       identifiers = ["pods.eks.amazonaws.com"]
#     }

#     actions = [
#       "sts:AssumeRole",
#       "sts:TagSession"
#     ]
#   }
# }

data "aws_iam_policy_document" "aws_lbc" {
  statement {
    effect = "Allow"

    actions = [
      "sts:AssumeRole",
      "sts:TagSession"
    ]

    principals {
      type        = "Service"
      identifiers = ["pods.eks.amazonaws.com"]
    }
  }
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRoleWithWebIdentity"]

    # condition {
    #   test     = "StringEquals"
    #   variable = "${replace(aws_iam_openid_connect_provider.oidc_provider.url, "https://", "")}:aud"
    #   values   = ["sts.amazonaws.com"]
    # }

    condition {
      test     = "StringEquals"
      variable = "${replace(aws_iam_openid_connect_provider.oidc_provider.url, "https://", "")}:sub"
      values   = ["system:serviceaccount:kube-system:aws-load-balancer-controller"]
    }

    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.oidc_provider.arn]
    }
  }
}

resource "aws_iam_role" "aws_lbc" {
  name               = "aws-lbc"
  assume_role_policy = data.aws_iam_policy_document.aws_lbc.json
}

resource "aws_iam_policy" "aws_lbc" {
  policy = file("./iam/AWSLoadBalancerController.json")
  name   = "AWSLoadBalancerController"
}

resource "aws_iam_role_policy_attachment" "aws_lbc" {
  policy_arn = aws_iam_policy.aws_lbc.arn
  role       = aws_iam_role.aws_lbc.name
}

# REPLACE OIDC!
# Associate `AWS IAM Role` with `Kubernetes Service account`!!
# resource "aws_eks_pod_identity_association" "aws_lbc" {
#   cluster_name    = aws_eks_cluster.my-cluster.name
#   namespace       = "kube-system"
#   service_account = "aws-load-balancer-controller"
#   role_arn        = aws_iam_role.aws_lbc.arn
# }

# Required to access Kuberentes API from IAM role?
# data "aws_eks_cluster_auth" "my-cluster" {
#   name = aws_eks_cluster.my-cluster.name
# }

# # The Kubernetes (K8S) provider is used to interact with the resources supported by Kubernetes.
# provider "kubernetes" {
#   host                   = data.aws_eks_cluster.my-cluster.endpoint
#   cluster_ca_certificate = base64decode(data.aws_eks_cluster.my-cluster.certificate_authority[0].data)
#   token                  = data.aws_eks_cluster_auth.my-cluster.token
# }

# resource "kubernetes_service_account" "aws-load-balancer-controller" {
#   metadata {
#     name      = "aws-load-balancer-controller"
#     namespace = "kube-system"
#     annotations = {
#       "eks.amazonaws.com/role-arn"     = aws_iam_role.aws_lbc.arn
#       "meta.helm.sh/release-name"      = "aws-load-balancer-controller"
#       "meta.helm.sh/release-namespace" = "kube-system"
#     }
#     labels = {
#       "app.kubernetes.io/managed-by" = "Helm",
#       "app.kubernetes.io/component" = "controller",
#       "app.kubernetes.io/name" = "aws-load-balancer-controller"
#     }
#   }
# }


resource "helm_release" "aws_lbc" {
  name = "aws-load-balancer-controller"

  repository = "https://aws.github.io/eks-charts"
  chart      = "aws-load-balancer-controller"
  namespace  = "kube-system"
  version    = "1.7.2"

  set {
    name  = "clusterName"
    value = aws_eks_cluster.my-cluster.name
  }

  set {
    name  = "serviceAccount.name"
    # value = kubernetes_service_account.aws-load-balancer-controller.metadata[0].name
    value = "aws-load-balancer-controller"
  }
  set {
    name  = "serviceAccount.annotations.eks\\.amazonaws\\.com/role-arn"
    value = aws_iam_role.aws_lbc.arn
  }

  # lbc needs to know region and vpcid (but clustername is provided..?)
  set {
    name  = "region"
    value = var.region
  }

  set {
    name  = "vpcId"
    value = aws_vpc.main.id
  }

  # depends_on = [helm_release.cluster_autoscaler]
  # depends_on = [ aws_eks_node_group.private_nodes ]
  depends_on = [helm_release.metric_server]
}


# Use module
# https://registry.terraform.io/modules/akw-devsecops/eks/aws/latest/submodules/aws-load-balancer-controller
# module "eks_aws-load-balancer-controller" {
#   source  = "akw-devsecops/eks/aws//modules/aws-load-balancer-controller"
#   version = "3.0.0"

#   # insert the 1 required variable here
#   # The ARN of the OIDC Provider
#   oidc_provider_arn = aws_iam_openid_connect_provider.oidc_provider.arn
# }
