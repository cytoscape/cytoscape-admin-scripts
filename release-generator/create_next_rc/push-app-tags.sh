CORE_APPS=(biopax command-dialog core-apps-meta cyREST datasource-biogrid \
json idmapper network-analyzer network-merge opencl-cycl opencl-layout \
psi-mi sbml welcome webservice-psicquic-client webservice-biomart-client)

BUILD_DIR=$1

# Record the original location
original_dir=`pwd`

# Go into the core app directory in the workspace
cd ./${BUILD_DIR}/apps

# Build all apps and if looks OK, tag it
for app in "${CORE_APPS[@]}"; do
  cd $app
  git push --tags
  cd ..
done

# Going back to the original location
cd $original_dir

echo "All tags are pushed."
