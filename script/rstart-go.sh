#!/bin/bash

kubectl rollout restart deployment be-go-deployment

sleep 1

kubectl get pod --watch
