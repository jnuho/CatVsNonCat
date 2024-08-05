#!/bin/bash

if [ -z "$1" ]; then
    docker rmi jnuho/fe-nginx:latest
    docker rmi jnuho/be-go:latest
    docker rmi jnuho/be-py:latest
    docker build -f ../dockerfiles/Dockerfile-nginx -t jnuho/fe-nginx ..
    docker build -f ../dockerfiles/Dockerfile-go -t jnuho/be-go ..
    docker build -f ../dockerfiles/Dockerfile-py -t jnuho/be-py ..
    exit
fi

PLATFORM="linux/$1"

docker rmi jnuho/fe-nginx-$1:latest
docker rmi jnuho/be-go-$1:latest
docker rmi jnuho/be-py-$1:latest
docker build --platform "$PLATFORM" -f ../dockerfiles/Dockerfile-nginx -t jnuho/fe-nginx-$1 ..
docker build --platform "$PLATFORM" -f ../dockerfiles/Dockerfile-go -t jnuho/be-go-$1 ..
docker build --platform "$PLATFORM" -f ../dockerfiles/Dockerfile-py -t jnuho/be-py-$1 ..

sleep 2

docker image prune -f
