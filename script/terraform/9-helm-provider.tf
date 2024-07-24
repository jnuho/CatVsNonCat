

# FOR MINIKUBE - LOCAL
# provider "helm" {
#   kubernetes {
#     config_path = "~/.kube/config"
#   }
# }

# FOR EKS; dynamically obtain a token to athenticate with cluster
data "aws_eks_cluster" "eks" {
  name = aws_eks_cluster.my-cluster.name
}

data "aws_eks_cluster_auth" "eks" {
  name = aws_eks_cluster.my-cluster.name
}

provider "helm" {
  kubernetes {
    host                   = data.aws_eks_cluster.eks.endpoint
    cluster_ca_certificate = base64decode(data.aws_eks_cluster.eks.certificate_authority[0].data)
    token                  = data.aws_eks_cluster_auth.eks.token
  }
}