#!/bin/bash

kubectl rollout restart deployment fe-nginx-deployment

sleep 1

kubectl get pod --watch
