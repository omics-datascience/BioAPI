#!/bin/bash
VERSION=$(grep -i 'VERSION =' $SETTINGSFILE | cut -d '=' -f2 | tr -d "' ")
echo "VERSION=$VERSION"
