BUILD_DIR=$1
BRANCH=$2

REPOSITORIES=(gui-distribution app-developer)

cd ./${BUILD_DIR}/cytoscape || { echo Faild to change dir; exit 1;}

# Make sure everything passes the test
# mvn clean install || { echo Faild to build; exit 1;}

echo `pwd`

for repo in "${REPOSITORIES[@]}"; do

  cd $repo || { echo Faild to change dir; exit 1;}
  git checkout -b $BRANCH || { echo Faild to switch; exit 1;}
  git add -A || { echo Faild to Add; exit 1;}
  git commit -m "Version number updated for release"
  git push -u origin $BRANCH || { echo Faild to push; exit 1;}
  cd - || { echo Faild to change directory; exit 1;}
done

#
# for repo in "${REPOSITORIES[@]}"; do
#   cd $repo
#   git push -u origin $BRANCH
#   mvn clean deploy
#   cd .. || { echo Faild to change directory; exit 1;}
# done
