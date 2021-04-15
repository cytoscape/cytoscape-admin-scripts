# The following must be correctly set in order to make a Cytoscape build
# JAVA_HOME
# MAVEN_HOME
# MAC_KEYSTORE_PASSWORD
# 
# Your PATH must also include entries for the correct Maven binaries (/opt/apache-maven-3.6.0/bin/ for example)


# Build directory. Git repos will be cloned and built here. Existing cytoscape clones will be deleted and then overwritten.
BUILD_DIR=$1
# Web directly. Installers will be copied to this directory, overwriting existing files.
WEB_DIR=$2

STARTING_BRANCH=develop

cd $BUILD_DIR
rm -rf ./cytoscape

git clone git@github.com:cytoscape/cytoscape.git 

cd $BUILD_DIR/cytoscape/

./cy.sh init

cd $BUILD_DIR/cytoscape/cytoscape

./cy.sh run-all "git checkout ${STARTING_BRANCH}"
./cy.sh run-all 'git clean -f -d'
./cy.sh run-all 'git reset --hard'

mvn clean install -Dmaven.test.skip=true

cd $BUILD_DIR/cytoscape/cytoscape/gui-distribution/packaging

mvn clean install -U

cp -f $BUILD_DIR/cytoscape/cytoscape/gui-distribution/packaging/target/media/* $WEB_DIR
cp -f $BUILD_DIR/cytoscape/cytoscape/gui-distribution/assembly/target/*.{gz,zip} $WEB_DIR