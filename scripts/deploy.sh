#!/bin/bash

# Build and tag docker image
docker build -t "capi:latest" .
docker tag "capi:latest" "$REPO_URI:capi" #TODO: change to REPO_URI:latest prior to merging
docker tag "capi:latest" "$REPO_URI:$TRAVIS_COMMIT"
$(aws ecr get-login --no-include-email)
echo "pushing $REPO_URI:capi to ECR"
docker push "$REPO_URI:capi" #TODO: change to REPO_URI:latest prior to merging
docker push "$REPO_URI:$TRAVIS_COMMIT"

# Force deploy service to pick up new docker image & wait for success
python scripts/restart_service.py $CLUSTER $SERVICE
