#!/bin/bash

set -e

FILE=./scripts/openapi.json 

if test -f "$FILE"; then
    echo "openapi.json exists, replacing it"
    rm $FILE
fi

wget -P ./scripts/ http://127.0.0.1:8000/api/openapi.json


VERSION=$(cat $FILE | jq '.info.version' -r)

PROJECT_NAME=$(cat scripts/openapi.json | jq '.info.title' -r)

docker run --rm \
  -v ${PWD}:/local openapitools/openapi-generator-cli generate \
  -i /local/scripts/openapi.json \
  -g python \
  -o /local/python-sdk \
  --additional-properties packageVersion=${VERSION} \
  --additional-properties packageName=${PROJECT_NAME} \
  --additional-properties projectName=${PROJECT_NAME}

