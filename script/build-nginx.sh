#!/bin/bash

if [ -z "$1" ]; then
    docker rmi jnuho/fe-nginx:latest
    docker build -f ../dockerfiles/Dockerfile-nginx -t jnuho/fe-nginx ..
    exit
fi

PLATFORM="linux/$1"

docker rmi jnuho/fe-nginx-$1:latest
docker build --platform "$PLATFORM" -f ../dockerfiles/Dockerfile-nginx -t jnuho/fe-nginx-$1 ..

sleep 2

docker image prune -f
