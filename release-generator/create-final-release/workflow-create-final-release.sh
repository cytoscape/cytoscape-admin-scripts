#!/bin/sh

################################################################################
#
# Script to create the final release from the existing release branch
#
################################################################################

# Target work space for this task
# All code will be copied here
BUILD_DIR="build"

# Release branch name
BRANCH="release/3.5.0"

# Current version on the release branch
CURRENT="3.5.0-RC1"

# New release version
TARGET="3.5.0"

# Clone all repositories required to build release
./prepare.sh $BUILD_DIR

# Tag all core apps
./tagging-core-apps.sh $BRANCH $BUILD_DIR $TARGET

# Update version number and merge all release branches to master
./create-release-installers.sh $BRANCH $TARGET $BUILD_DIR $CURRENT
