#!/bin/sh

# 1. Create a directory containing everything we need for building a new release.
# Since this is a new local repo, you can trash this any time you want.

# Target directory.  Everything will be downloaded into this dir.
BUILD_DIR=$1

# Clone everything into $BUILD_DIR
function clone_all {
  git clone git@github.com:cytoscape/cytoscape.git
  mv ./cytoscape ./$BUILD_DIR
  cd ./$BUILD_DIR

  # Clone repos
  ./cy.sh init
  ./cy.sh apps
}

# Execute it
clone_all
