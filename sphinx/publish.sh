#!/bin/sh

# extract script directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
echo Working directory: $DIR

# generate api documentation
echo Publishing to docs..
rm -rf "$DIR/../docs"
cp -vr "$DIR/build/" "$DIR/../docs"