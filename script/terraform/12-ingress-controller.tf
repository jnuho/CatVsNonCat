
resource "helm_release" "external_nginx" {
  name = "external"

  repository       = "https://kubernetes.github.io/ingress-nginx"
  chart            = "ingress-nginx"
  namespace        = "ingress"
  create_namespace = true
  version          = "4.7.0"

  set {
    #default value: nginx-ingress
    name  = "controller.ingressClassResource.name"
    value = "external-nginx"
  }

  # Set this only if you have already installed the AWS Load Balancer Controller and want VPC native routing.
  set {
    name  = "controller.service.annotations.service\\.beta\\.kubernetes\\.io/aws-load-balancer-type"
    value = "external"
  }

  set {
    name  = "controller.service.annotations.service\\.beta\\.kubernetes\\.io/aws-load-balancer-nlb-target-type"
    value = "ip"
  }

  set {
    name  = "controller.service.annotations.service\\.beta\\.kubernetes\\.io/aws-load-balancer-scheme"
    value = "internet-facing"
  }

  # depends_on = [helm_release.aws_lbc]
  depends_on = [helm_release.metric_server]
}