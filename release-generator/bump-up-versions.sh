BUILD_DIR=$1
NEXT_RELEASE=$2

CURRENT="3.5.0-SNAPSHOT"
TARGET="3.6.0-SNAPSHOT"

REPOSITORIES=(parent api impl support gui-distribution app-developer)

cd ./${BUILD_DIR}/cytoscape || { echo Faild to change dir; exit 1;}

# Function to update all entries without using mvn:versions.
function update_version {
  echo "* Updating version numbers..."
  find . -name pom.xml | xargs sed -i "" -e "s/${CURRENT}/${TARGET}/g"

  # Update misc. files
  cd gui-distribution/assembly/src/main/bin
  sed -E -e "s/-SNAPSHOT//g" cytoscape.sh > cytoscape-up.sh
  mv cytoscape-up.sh cytoscape.sh
  sed -E -e "s/-SNAPSHOT//g" cytoscape.bat > cytoscape-up.bat
  mv cytoscape-up.bat cytoscape.bat
}

base_dir=`pwd`
echo "Working directory: $base_dir"
update_version
cd $base_dir
mvn clean install || { echo Faild to build; exit 1;}

for repo in "${REPOSITORIES[@]}"; do
  cd $repo || { echo Faild to change dir; exit 1;}
  git checkout develop || { echo Faild to switch to develop; exit 1;}
  git pull || { echo Faild to pull; exit 1;}
  git add -A || { echo Faild to Add; exit 1;}
  git commit -m "Version number updated to ${NEXT_RELEASE}" || { echo Faild to commit; exit 1;}
  git push || { echo Faild to push; exit 1;}
  cd $base_dir || { echo Faild to change directory; exit 1;}
done
