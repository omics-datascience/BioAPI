#!/bin/bash
VERSION="$1"
/usr/bin/git tag
TAG=$(git tag -l $VERSION)
echo $TAG
if [ -n "$TAG" ]
then
  echo "::error::This bio-api version tag already exists in repository."
  exit 1
fi
