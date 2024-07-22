#!/bin/bash

docker context use default

if ! minikube status | grep "Running" &> /dev/null; then
    minikube start
else
    echo "Minikube cluster is already running."
fi

eval $(minikube -p minikube docker-env)

