#!/bin/bash

# Workspace directory name
BUILD_DIR=$1
BRANCH=$2

# Name of the repositories for Cytoscape Core modules
REPOSITORIES=(parent api impl support gui-distribution app-developer)

################################################################################

echo "Push changes to remote..."

# Move into the Cytoscape directory in your local workspace
cd ./${BUILD_DIR}/cytoscape

# Switch to release branch
./cy.sh switch $BRANCH || { echo Failed to switch to $BRANCH; exit 1;}

# Record the Cytoscape top-level directory location
cytoscape_dir=`pwd`

for repo in "${REPOSITORIES[@]}"; do
  cd $repo
  git push
  git push --tags
  cd ..
done

cd $cytoscape_dir

echo "-------------- Done! ---------------"
