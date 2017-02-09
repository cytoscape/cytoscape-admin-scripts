#!/bin/bash

# Script for building all latest version of the core apps
# from the specified branch

# List of all core apps
CORE_APPS=(biopax command-dialog core-apps-meta cyREST datasource-biogrid \
json idmapper network-analyzer network-merge opencl-cycl opencl-layout \
psi-mi sbml welcome webservice-psicquic-client webservice-biomart-client)

BRANCH=$1
BUILD_DIR=$2
TAG=$3

# Record the starting point
original_dir=`pwd`

cd ./${BUILD_DIR}/apps

last_dir=`pwd`

declare -A app_versions

for app in "${CORE_APPS[@]}"; do
  cd $app
  echo "- Switching to ${BRANCH}: $app"
  git checkout $BRANCH || { echo Could not checkout branch $BRANCH; exit 1;}

  # Make sure it's the latest in the branch
  git pull origin $BRANCH

  mvn clean install || { echo Failed to build $app; exit 1;}
  cd ..
done

cd $original_dir

echo "* Finished building all core apps from $BRANCH"
