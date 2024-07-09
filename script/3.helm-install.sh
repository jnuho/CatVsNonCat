#!/bin/bash

# helm install

if [ "$(kubectl config current-context)" = "minikube" ]; then
    helm install tst-release ./tst-chart -f ./tst-chart/values.dev.yaml
else
    helm install tst-release ./tst-chart -f ./tst-chart/values.prd.yaml
fi
