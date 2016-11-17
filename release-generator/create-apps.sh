#!/bin/bash

# List of all core
CORE_APPS=(biopax command-dialog core-apps-meta cyREST datasource-biogrid \
json idmapper network-analyzer network-merge opencl-cycl opencl-layout \
psi-mi sbml welcome webservice-psicquic-client webservice-biomart-client)

BRANCH=$1
TARGET=$2
BUILD_DIR=$3

# Record the starting point
original_dir=`pwd`

########## Prepare new core apps ##########
# Create branch for apps
cd ./${BUILD_DIR}/apps

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

  # Tag the release
  git tag ${res}
  cd ..
done

# Update the gui-distribution/assembly/pom.xml
cd $original_dir
cd ./cytoscape/gui-distribution/assembly
git checkout -b $BRANCH
python ./core-app-update.py ${BUILD_DIR}

cd $original_dir

echo "------------- Core Apps Are ready to deploy! -------------"
