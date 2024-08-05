#!/bin/bash

if [ -z "$1" ]; then
    docker rmi jnuho/be-py:latest
    docker build -f ../dockerfiles/Dockerfile-py -t jnuho/be-py ..
    exit
fi

PLATFORM="linux/$1"

docker rmi jnuho/be-py-$1:latest
docker build --platform "$PLATFORM" -f ../dockerfiles/Dockerfile-py -t jnuho/be-py-$1 ..

sleep 2

docker image prune -f
