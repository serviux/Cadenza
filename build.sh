#!/bin/bash
aws_access_key_id=$(aws configure get aws_access_key_id)
aws_secret_access_key=$(aws configure get aws_secret_access_key)
docker build \
--build-arg FILE_PATH="Metalmancy.mp3" \
--build-arg AWS_ACCESS_KEY_ID=$aws_access_key_id \
--build-arg AWS_SECRET_ACCESS_KEY=$aws_secret_access_key \
.

