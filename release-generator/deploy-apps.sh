BUILD_DIR=$1
BRANCH=$2

# List of all core
CORE_APPS=(biopax command-dialog core-apps-meta cyREST datasource-biogrid \
json idmapper network-analyzer network-merge opencl-cycl opencl-layout \
psi-mi sbml welcome webservice-psicquic-client webservice-biomart-client)

cd ./${BUILD_DIR}/apps

for app in "${CORE_APPS[@]}"; do
  cd $app
  git push -u origin $BRANCH
  mvn clean deploy
  cd .. || { echo Faild to change directory; exit 1;}
done
