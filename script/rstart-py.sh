#!/bin/bash

kubectl rollout restart deployment be-py

sleep 1

kubectl get pod --watch
