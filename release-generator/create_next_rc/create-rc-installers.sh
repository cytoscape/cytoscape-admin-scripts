
#!/bin/bash

BRANCH=$1
TARGET=$2
BUILD_DIR=$3
CURRENT=$4

echo "Switching branch..."
cd ./${BUILD_DIR}/cytoscape
./cy.sh switch $BRANCH || { echo Failed to switch to $BRANCH; exit 1;}

cytoscape_dir=`pwd`

# Batch update (for version numbers)
cd ${cytoscape_dir}
echo "* Updating version numbers..."
find . -name pom.xml | xargs sed -i "" -e "s/${CURRENT}/${TARGET}/g"

# Update misc. files
cd gui-distribution/assembly/src/main/bin
sed -E -e "s/-SNAPSHOT//g" cytoscape.sh > cytoscape-up.sh
mv cytoscape-up.sh cytoscape.sh
sed -E -e "s/-SNAPSHOT//g" cytoscape.bat > cytoscape-up.bat
mv cytoscape-up.bat cytoscape.bat
cd ${cytoscape_dir}

# Build everything
mvn clean install || { echo Failed to build Cytoscape; exit 1;}

# Create installers.  This requires Install4j v6.
# Works Mac only due to code signing...
cd gui-distribution/packaging
mvn clean install || { echo Failed to create installers; exit 1;}

cd ${cytoscape_dir}

# Commit changes
for repo in "${REPOSITORIES[@]}"; do
  cd $repo

  git add -A
  git commit -m "Version number updated for ${TARGET}."
  git tag ${TARGET}
  cd ..
done

git add -A
git commit -m "Version number updated for ${TARGET}."
git tag ${TARGET}

echo "-------------- Done! ---------------"
echo "New installers are ready in $BUILD_DIR/cytoscape/gui-distribution/packaging/target/install4j"
