#!/bin/bash -ex

# Build and tag docker image
docker build --build-arg network=$TRAVIS_BRANCH -t "capi:$TRAVIS_BRANCH" .
docker tag "capi:$TRAVIS_BRANCH" "$REPO_URI:$TRAVIS_BRANCH"
docker tag "capi:$TRAVIS_BRANCH" "$REPO_URI:$TRAVIS_COMMIT"
$(aws ecr get-login --no-include-email --region $AWS_DEFAULT_REGION)
docker push "$REPO_URI:$TRAVIS_BRANCH"
docker push "$REPO_URI:$TRAVIS_COMMIT"

# Force deploy service to pick up new docker image & wait for success
python scripts/restart_service.py $CLUSTER $SERVICE
