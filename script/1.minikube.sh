#!/bin/bash

docker context use default

if ! minikube status | grep "Running" &> /dev/null; then
    minikube start --kubernetes-version=v1.30.3 --driver=docker --cpus 4 --memory 4g
else
    echo "Minikube cluster is already running."
fi

eval $(minikube -p minikube docker-env)

