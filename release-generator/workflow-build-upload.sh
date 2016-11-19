#!/bin/sh

BUILD_DIR="build"

# New branch for release
BRANCH="release/3.5.0"

start_dir=`pwd`

./prepare.sh $BUILD_DIR
./build-all-core-apps.sh $BUILD_DIR $BRANCH

cd ./${BUILD_DIR}/cytoscape
./cy.sh switch $BRANCH || { echo Failed to switch; exit 1; }
./cy.sh pull || { echo Failed to pull; exit 1; }
mvn clean install || { echo Failed to build new; exit 1; }
cd gui-distribution/packaging || { echo Failed to change dir; exit 1; }

mvn clean install || { echo Failed to build new installer; exit 1; }

cd $start_dir

./upload.sh $BUILD_DIR
