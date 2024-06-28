#!/bin/bash

minikube kubectl -- delete -f ingress.yaml

minikube kubectl -- delete -f service.yaml
minikube kubectl -- delete -f be/go/service.yaml
minikube kubectl -- delete -f be/py/service.yaml

minikube kubectl -- delete -f deployment.yaml
minikube kubectl -- delete -f be/go/deployment.yaml
minikube kubectl -- delete -f be/py/deployment.yaml

# mongodb, mongo-express
#minikube kubectl -- delete -f mongo/mongo-configmap.yaml
#minikube kubectl -- delete -f mongo/mongo-secret.yaml
#minikube kubectl -- delete -f mongo/mongodb.yaml
#minikube kubectl -- delete -f mongo/mongo-express.yaml

#minikube kubectl -- delete secret regcred

minikube kubectl -- get pod
minikube kubectl -- get service
minikube kubectl -- get ingress

