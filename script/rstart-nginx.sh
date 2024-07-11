#!/bin/bash

kubectl rollout restart deployment fe-nginx

sleep 1

kubectl get pod --watch
