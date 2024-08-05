#!/bin/bash

if [ -z "$1" ]; then
    docker rmi jnuho/be-go:latest
    docker build -f ../dockerfiles/Dockerfile-go -t jnuho/be-go ..
    exit
fi

PLATFORM="linux/$1"

docker rmi jnuho/be-go-$1:latest
docker build --platform "$PLATFORM" -f ../dockerfiles/Dockerfile-go -t jnuho/be-go-$1 ..

sleep 2

docker image prune -f
