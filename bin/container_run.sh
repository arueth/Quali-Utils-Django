#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

docker container run \
        -d \
        --name quali_utils_django \
        -p 8000:8000 \
        arueth/quali-utils-django:latest
