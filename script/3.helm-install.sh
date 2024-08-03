#!/bin/bash

current_context=$(kubectl config current-context)

if [ "$current_context" = "minikube" ]; then
    helm install tst-release ./tst-chart -f ./tst-chart/values.local.yaml
elif [ "$current_context" = "pi" ]; then
    helm install tst-release ./tst-chart -f ./tst-chart/values.pi.yaml
elif [[ "$current_context" == *"aws:eks"* ]]; then
    aws eks update-kubeconfig --region ap-northeast-2 --name my-cluster --profile terraform
    helm install tst-release ./tst-chart -f ./tst-chart/values.prd.AWS.L4.ingress.controller.yaml
else
    echo "NO KUBERNETES CONTEXT FOUND!"
fi
