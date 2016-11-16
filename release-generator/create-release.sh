#!/bin/bash

################################################################################
#
# Release generator for Cytocape with core apps.
#
# - Requirments:
#    - bash v4.x
#    - python 3.x
#    - install4j v6 (for the last step)
#
# by Keiichiro Ono
#
################################################################################

# New branch for release
BRANCH="release/3.5.0"

# Current development version
CURRENT="3.5.0-SNAPSHOT"

# New release version (for the core, not core apps!)
TARGET="3.5.0-RC1"

# List of all core modules
REPOSITORIES=(parent api support impl gui-distribution app-developer)

# List of all core
CORE_APPS=(biopax command-dialog core-apps-meta cyREST datasource-biogrid \
json idmapper network-analyzer network-merge opencl-cycl opencl-layout \
psi-mi sbml welcome webservice-psicquic-client webservice-biomart-client)

# List of files to be updated in this release process
original_dir=`pwd`

# Get the top-level dir
git clone git@github.com:cytoscape/cytoscape.git
mv ./cytoscape ./cy-release-work-dir
cd ./cy-release-work-dir

# Clone repos
./cy.sh init
./cy.sh apps

########## Prepare new core apps ##########

# Create branch for apps
cd ./apps
last_dir=`pwd`

declare -A app_versions

for app in "${CORE_APPS[@]}"; do
  cd $app
  echo "- Switching to ${BRANCH}: $app"
  git checkout -b $BRANCH || { echo Could not checkout branch $BRANCH; exit 1;}

	# sed -E -e "s/-SNAPSHOT<\/version>/<\/version>/g" pom.xml > pom.updated.xml
	# mv pom.updated.xml pom.xml

  original_version=$(printf 'VERSION=${project.version}\n0\n'\
   | mvn org.apache.maven.plugins:maven-help-plugin:2.1.1:evaluate \
   | grep '^VERSION' \
   | sed -E -e "s/VERSION=//g")

  res=$(echo ${original_version} | sed -E -e "s/-SNAPSHOT//g")
  app_versions["${app}"]=$res
  echo "$app,$res" >> ../versions.txt

  # This is for updating children
  mvn versions:set -DnewVersion=${res}
  mvn versions:update-child-modules
  mvn versions:commit
  mvn clean install || { echo Failed to build $app; exit 1;}

  # Now commit the change to local repo.
  git add -A
  git commit -m "Version number updated to ${res} for Cytoscape release ${TARGET}."
  cd ..
done

# Update the gui-distribution/assembly/pom.xml
cd $original_dir
python ./core-app-update.py

############## Next, update Cytoscape core modules #################
cd $original_dir

# Update verison
cd ./cy-release-work-dir/cytoscape
cytoscape_dir=`pwd`

# Create new release branch
git checkout -b $BRANCH || { echo Could not checkout branch $BRANCH; exit 1;}
for repo in "${REPOSITORIES[@]}"; do
  cd $repo
  echo "# Target repo: $repo"
  git checkout -b $BRANCH || { echo Could not checkout branch $BRANCH; exit 1;}
  cd ..
done

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
cd gui-distribution/packaging
mvn clean install || { echo Failed to create installers; exit 1;}

cd ${cytoscape_dir}
# Commit changes
for repo in "${REPOSITORIES[@]}"; do
  cd $repo

  git add -A
  git commit -m "Version number updated for ${TARGET}."
  cd ..
done

git add -A
git commit -m "Version number updated for ${TARGET}."


echo "-------------- Done! ---------------"
echo "! Don't forget to re-format gui-distribution/assembly/pom.xml"
