#!/bin/bash

################################################################################
#
# Script to create installers for final release version
#
################################################################################

# Existing release branch name, e.g., release/3.5.0
BRANCH=$1

# Final release version (e.g., 3.5.0)
TARGET=$2

# Workspace directory name
BUILD_DIR=$3

# Current version on the release branch (e.g., 3.5.0-RC2)
CURRENT=$4

# Name of the repositories for Cytoscape Core modules
REPOSITORIES=(parent api impl support gui-distribution app-developer)

################################################################################

echo "Switching branch..."

# Move into the Cytoscape directory in your local workspace
cd ./${BUILD_DIR}/cytoscape

# Switch to release branch
./cy.sh switch $BRANCH || { echo Failed to switch to $BRANCH; exit 1;}

# Record the Cytoscape top-level directory location
cytoscape_dir=`pwd`

################################################################################
#
# Step 1: Update version numbers in pom files
#  - Simply replace all of the version numbers to next one using sed
#
################################################################################
cd ${cytoscape_dir}
echo "* Updating version numbers..."
find . -name pom.xml | xargs sed -i "" -e "s/${CURRENT}/${TARGET}/g"


################################################################################
#
# Merge everything back to master branch
#
################################################################################
cd ${cytoscape_dir}

for repo in "${REPOSITORIES[@]}"; do
  cd $repo

  # First, commit the changes to the local repository
  git add -A
  git commit -m "Version number updated for the final release version ${TARGET}."

  # Merge it back to master!
  git checkout master

  # Force to use release branch, because it is the only source of change
  # for the master branch
  git merge --no-edit -X theirs $BRANCH

  # Tag it
  git tag ${TARGET}
  cd ..
done


# This is for the top level project (cytoscape/cytoscape)
git add -A
git commit -m "Version number updated for the final release version ${TARGET}."
git checkout master
git merge --no-edit -X theirs $BRANCH
git tag ${TARGET}

################################################################################
#
# Create installers:
#
# !!!!!!!!!!!!!!!! This requires Install4j v6 !!!!!!!!!!!!!!!!!!!!!!
#
# Make sure you have Install4j on your machine
#
################################################################################

# Build everything on master branch
mvn clean install || { echo Failed to build Cytoscape; exit 1;}

# Create installers
cd gui-distribution/packaging
mvn clean install || { echo Failed to create installers; exit 1;}

echo "-------------- Done! ---------------"
echo "New installers are ready in $BUILD_DIR/cytoscape/gui-distribution/packaging/target/install4j"
echo "Don't forget to sign DMG!  Also, you need to deploy JAR and Apps to remote now."
