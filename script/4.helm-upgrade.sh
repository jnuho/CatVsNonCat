#!/bin/bash

if [ "$(kubectl config current-context)" = "minikube" ]; then
    helm upgrade tst-release ./tst-chart -f ./tst-chart/values.dev.yaml
else
    helm upgrade tst-release ./tst-chart -f ./tst-chart/values.prd.yaml
fi
