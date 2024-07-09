#!/bin/bash

kubectl rollout restart deployment be-py-deployment

sleep 1

kubectl get pod --watch
