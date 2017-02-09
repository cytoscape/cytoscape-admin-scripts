#!/bin/bash

# Script for creating final release version of the core apps

# List of all core apps
# Make sure this includes all of the Core Apps!
CORE_APPS=(biopax command-dialog core-apps-meta cyREST datasource-biogrid \
json idmapper network-analyzer network-merge opencl-cycl opencl-layout \
psi-mi sbml welcome webservice-psicquic-client webservice-biomart-client)

# Release branch name, e.g. release/3.5.0
BRANCH=$1

# Target work directory name
BUILD_DIR=$2

# Tag for the release, e.g. 3.5.0
TAG=$3

# Record the original location
original_dir=`pwd`

# Go into the core app directory in the workspace
cd ./${BUILD_DIR}/apps

# Build all apps and if looks OK, tag it
for app in "${CORE_APPS[@]}"; do
  # Go into an app's directory
  cd $app

  echo "- Switching to ${BRANCH}: $app"

  # Make sure we are on the correct release branch
  git checkout $BRANCH || { echo Could not checkout branch $BRANCH; exit 1;}

  # Pull the latest code on the branch
  git pull origin $BRANCH

  # Build the app
  mvn clean install || { echo Failed to build $app; exit 1;}

  # Now, tag it with the release version number (e.g. 3.5.0)
  git tag $TAG

  # Move to the next app
  cd ..
done

# Going back to the original location
cd $original_dir

echo "All apps are successfully tagged.  Remember, all of the changes are still local.  You need to push tags later."
