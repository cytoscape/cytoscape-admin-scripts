

# Build script for Cytocape with core apps.


# List of all core modules
REPOSITORIES=(parent api support impl gui-distribution app-developer)

# List of all core
CORE_APPS=(biopax command-dialog core-apps-meta cyREST datasource-biogrid \
json idmapper network-analyzer network-merge opencl-cycl opencl-layout \
psi-mi sbml welcome webservice-psicquic-client webservice-biomart-client)

# Get the script
git clone git@github.com:cytoscape/cytoscape.git
mv ./cytoscape ./cy-release-work-dir
cd ./cy-release-work-dir

# Clone repo
# ./cy.sh init
./cy.sh apps

BRANCH="release/3.5.0"
TARGET="3.5.0-RC1"

# Create branch for apps
cd ./apps
last_dir=`pwd`

declare -A app_versions

for app in "${CORE_APPS[@]}"; do
  cd $app
  echo "- Switching to ${BRANCH}: $app"
  git checkout -b $BRANCH || { echo Could not checkout branch $BRANCH; }
	sed -E -e "s/-SNAPSHOT<\/version>/<\/version>/g" pom.xml > pom.updated.xml
	mv pom.updated.xml pom.xml
  # mvn clean install || { echo Failed to build new version: $app; }
  res=$(printf 'VERSION=${project.version}\n0\n'\
   | mvn org.apache.maven.plugins:maven-help-plugin:2.1.1:evaluate \
   | grep '^VERSION' \
   | sed -E -e "s/VERSION=//g")

  app_versions["${app}"]=$res
  echo "RES is: $res"
  cd ..
done

echo "------ New Core App Versions ------"
for app_name in "${!app_versions[@]}"; do
  echo "$app_name: ${app_versions[$app_name]}";
done
echo "-----------------------------------"

cd $last_dir

# Show changes
for app in "${CORE_APPS[@]}"; do
  cd $app
  echo "# Result: $app"
  echo ${app_versions[${app}]}
  git diff
  cd ..
done


# Update verison
# echo "* Updating version numbers..."
# cd ./cytoscape
# mvn versions:set -DnewVersion=3.5.0-RC1 || { echo Could not update project version.; exit 1; }
# mvn versions:commit || { echo Could not commit change to the version number.; exit 1; }
