#!/bin/bash

kubectl rollout restart deployment be-go

sleep 1

kubectl get pod --watch
