#!/bin/sh

BUILD_DIR="build"

# New branch for release
BRANCH="release/3.5.0"

# Current development version
CURRENT="3.5.0-RC1"

# New release version (for the core, not core apps!)
TARGET="3.5.0-RC2"


./create-installers.sh $BRANCH $TARGET $BUILD_DIR $CURRENT
