#!/bin/sh

# Target workspace
BUILD_DIR=$1

# Clone everything into $BUILD_DIR
function clone_all {
  git clone git@github.com:cytoscape/cytoscape.git

  # Rename it
  mv ./cytoscape ./$BUILD_DIR
  cd ./$BUILD_DIR

  # Clone repos
  ./cy.sh init
  ./cy.sh apps
}

# Execute it
clone_all
