#!/bin/bash

if [ -z "$1" ]; then
  BUILD_DIR="build"
else
  BUILD_DIR=$1
fi

BRANCH=$2

# List of all core
CORE_APPS=(biopax command-dialog core-apps-meta cyREST datasource-biogrid \
json idmapper network-analyzer network-merge opencl-cycl opencl-layout \
psi-mi sbml welcome webservice-psicquic-client webservice-biomart-client)

cd ./${BUILD_DIR}/apps

for app in "${CORE_APPS[@]}"; do
  cd $app
  git checkout $BRANCH || { echo Faild to change branch; exit 1;}
  git pull || { echo Faild to pull; exit 1;}
  mvn clean install || { echo Faild to build latest ${app}; exit 1;}
  mvn deploy || { echo Faild to deploy to Nexus ${app}; exit 1;}
  cd .. || { echo Faild to change directory; exit 1;}
done
