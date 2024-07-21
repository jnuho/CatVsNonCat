#!/bin/bash

# Get the name of the fe-nginx pod
POD_NAME=$(kubectl get pods --no-headers -o custom-columns=":metadata.name" | grep be-py)

# Log the output of the fe-nginx pod with the --tail option
kubectl exec -it $POD_NAME -- /bin/sh