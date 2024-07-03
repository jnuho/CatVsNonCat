#!/bin/bash

# Get the IAM role ARN from Terraform output
# VPC_CNI_ROLE_ARN=$(terraform output -raw vpc_cni_role_arn)

# echo "---VPC_CNI_ROLE---"
# echo $VPC_CNI_ROLE_ARN
# echo "------------------"
# eksctl create iamserviceaccount \
#     --cluster=my-cluster \
#     --namespace=kube-system \
#     --name=aws-node \
#     --attach-role-arn=$VPC_CNI_ROLE_ARN \
#     --profile terraform \
#     --override-existing-serviceaccounts \
#     --approve

# Get the IAM role ARN from Terraform output
LBC_ROLE_ARN=$(terraform output -raw aws_lbc_role_arn)

echo "---LBC_ROLE-------"
echo $LBC_ROLE_ARN
echo "------------------"

eksctl create iamserviceaccount \
    --cluster=my-cluster \
    --namespace=kube-system \
    --name=aws-load-balancer-controller \
    --attach-role-arn=$LBC_ROLE_ARN \
    --profile terraform \
    --approve


# Helm
helm repo add eks https://aws.github.io/eks-charts
helm repo update eks

helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=my-cluster \
  --set serviceAccount.create=false \
  --set serviceAccount.name=aws-load-balancer-controller 

kubectl get deployment -n kube-system aws-load-balancer-controller
# NAME                           READY   UP-TO-DATE   AVAILABLE   AGE
# aws-load-balancer-controller   2/2     2            2           84s

