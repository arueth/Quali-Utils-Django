#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [ -z "$1" ]; then
  CONFIG_FILE=dev.conf
else
  CONFIG_FILE=${1}.conf
fi
source ${DIR}/.config/${CONFIG_FILE}

docker container run \
        -d \
        -e DJANGO_PORT=${DJANGO_PORT} \
        -e DATABASE_NAME=${DATABASE_NAME} \
        -e DATABASE_USER=${DATABASE_USER} \
        -e DATABASE_PASSWORD=${DATABASE_PASSWORD} \
        -e DATABASE_HOST=${DATABASE_HOST} \
        -e DATABASE_PORT=${DATABASE_PORT} \
        -e CLOUDSHELL_SERVER=${CLOUDSHELL_SERVER} \
        -e CLOUDSHELL_USERNAME=${CLOUDSHELL_USERNAME} \
        -e CLOUDSHELL_PASSWORD=${CLOUDSHELL_PASSWORD} \
        -e CLOUDSHELL_DOMAIN=${CLOUDSHELL_DOMAIN} \
        --name ${CONTAINER_NAME} \
        --network ${NETWORK} \
        -p 8000:8000 \
        ${IMAGE_NAME}:${IMAGE_TAG}
