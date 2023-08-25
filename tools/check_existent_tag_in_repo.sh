#!/bin/bash
if [ -n "$(git tag -l ${{ env.VERSION }})" ]
then
  echo "::error::This bio-api version tag already exists in repository."
  exit 1
fi
