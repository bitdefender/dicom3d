#!/bin/sh

# extract script directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
echo Working directory: $DIR

# generate api documentation
echo Building API documentation..
rm -rf "$DIR/source/api/"
sphinx-apidoc -M -o "$DIR/source/api" \
    "$DIR/../dicom3d/" \
    "$DIR/../dicom3d/geometry.py" \
    "$DIR/../dicom3d/section.py" \
    "$DIR/../dicom3d/dataset.py" \
    "$DIR/../dicom3d/series.py" \
    "$DIR/../dicom3d/data/getfiles.py" \
    "$DIR/../dicom3d/examples/"

# build documentation
echo Building documentation in HTML format..
rm -rf "$DIR/build/"
sphinx-build -b html "$DIR/source/" "$DIR/build/"

echo Done!
