#!/bin/bash

set -xe

function cleanup () {
  echo No cleanup needed
}

trap cleanup ERR

VERSION=$(git tag | tail -n 1 | sed -r 's/v//')
NAME=discovereasy

SOURCEDIST=${NAME}-${VERSION}.tar.gz
BINDIST=${NAME}-${VERSION}-py3-none-any.whl

echo $VERSION

cram README.md

python -m build

twine check dist/$SOURCEDIST dist/$BINDIST
twine upload --verbose dist/$SOURCEDIST dist/$BINDIST
