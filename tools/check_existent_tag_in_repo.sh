#!/bin/bash
VERSION="$1"
TAG=$(git tag -l $VERSION)
if [ -n "$TAG" ]
then
  echo "::error::This bio-api version tag already exists in repository."
  exit 1
fi
