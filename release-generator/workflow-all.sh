#!/bin/sh

# Temp workspace, containing all Cytoscape code
BUILD_DIR="build"

# New branch for release
BRANCH="release/3.5.0"

# Current development version
CURRENT="3.5.0-SNAPSHOT"

# New release version (for the core, not core apps!)
TARGET="3.5.0-RC1"


# Clone remote repository and start from scratch.
./prepare.sh $BUILD_DIR
./create-apps.sh $BRANCH $TARGET $BUILD_DIR
./create-installers.sh $BRANCH $TARGET $BUILD_DIR $CURRENT
