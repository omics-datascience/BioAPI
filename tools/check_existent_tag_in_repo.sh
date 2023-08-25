#!/bin/bash
$VERSION=$1
if [ -n "$(git tag -l $VERSION)" ]
then
  echo "::error::This bio-api version tag already exists in repository."
  exit 1
fi
