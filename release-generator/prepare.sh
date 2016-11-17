#!/bin/sh

# Create a directory with everything we need for building a release.

BUILD_DIR=$1

function checkout {
  git clone git@github.com:cytoscape/cytoscape.git
  mv ./cytoscape ./$BUILD_DIR
  cd ./$BUILD_DIR

  # Clone repos
  ./cy.sh init
  ./cy.sh apps
}

checkout
