#!/bin/sh

# Target work space for this task
# All code will be copied here
BUILD_DIR="build"

# Branch for release
BRANCH="release/3.5.0"

# Current version
CURRENT="3.5.0-RC1"

# New release version (for the core, not core apps!)
TARGET="3.5.0-RC2"


./prepare.sh $BUILD_DIR
./build-apps.sh $BRANCH $BUILD_DIR $TARGET
./create-rc-installers.sh $BRANCH $TARGET $BUILD_DIR $CURRENT
