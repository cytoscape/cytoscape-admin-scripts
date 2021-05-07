#!/bin/bash


usage() {
  echo ""
  echo "$1"
  echo ""
  echo " Usage: <build directory> <deploy directory> (optional comma delimited email addresses)"
  echo ""
  echo "    This script builds Cytoscape using <build directory> as a temporary directory, deploying"
  echo "    the binaries to <deploy directory>."
  echo ""
  echo "    This script requires the following commands to be in the path and working: mvn, git, & java"
  echo ""
  echo "    If there is an error, this script fails with a non zero exit code."
  echo "    If (optional comma delimited email addresses) parameter is set, then an email"
  echo "    will be sent."
  echo ""
  exit 2
}

if [ $# -lt 2 ] ; then
  usage "Required parameters <build directory> and <deploy directory> are missing"
fi

if [ $# -gt 3 ] ; then
  usage "Only 3 parameters are supported by this script"
fi

#/home/cybuilder/builds

# Target directory.  Everything will be downloaded into this dir.
BUILD_DIR=$1
WEB_DIR=$2

EMAIL_ADDRESSES=""

if [ $# -eq 3 ] ; then
  EMAIL_ADDRESSES=$3
fi

if [ ! -d "$BUILD_DIR" ] ; then
  usage "$BUILD_DIR must be a directory"
fi

if [ ! -d "$WEB_DIR" ] ; then
  usage "$WEB_DIR must be a directory"
fi


STARTING_BRANCH=develop


fatal_error() {
  echo "$1" 1>&2
  if [ -n "$EMAIL_ADDRESSES" ] ; then
    echo "Attempting to send email to $EMAIL_ADDRESSES"
    echo "On `hostname` in $BUILD_DIR Cytoscape build failed: $1" | mail -s "`date` Cytoscape nightly build failed" $EMAIL_ADDRESSES 
  fi
  exit 1
}

log_warning() {
  echo "$1" 1>&2
}

log_info() {
  echo "$1"
}

env
which java
which mvn
which git

cd $BUILD_DIR
if [ $? != 0 ] ; then
  fatal_error "Unable to cd to $BUILD_DIR"
fi

if [ -e "cytoscape" ] ; then
  date_stamp=`date +%s`
  /bin/mv cytoscape cytoscape.${date_stamp}
  if [ $? != 0 ] ; then
    fatal_error "mv cytoscape cytoscape.${date_stamp} failed"
  fi 
  if [ -d "cytoscape.${date_stamp}" ] ; then
    /bin/rm -rf "cytoscape.${date_stamp}"
  fi
fi

log_info "Cloning github.com:cytoscape/cytoscape.git to $BUILD_DIR/cytoscape"
git clone git@github.com:cytoscape/cytoscape.git 

if [ $? != 0 ] ; then
  fatal_error "Error cloning github.com:cytoscape/cytoscape.git"
fi

cd $BUILD_DIR/cytoscape/

if [ $? != 0 ] ; then
  fatal_error "Unable to cd to $BUILD_DIR/cytoscape/"
fi

./cy.sh init

cd $BUILD_DIR/cytoscape/cytoscape

if [ $? != 0 ] ; then
  fatal_error "Unable to cd to $BUILD_DIR/cytoscape/cytoscape"
fi

./cy.sh run-all "git checkout ${STARTING_BRANCH}"
./cy.sh run-all 'git clean -f -d'
./cy.sh run-all 'git reset --hard'

mvn clean install -Dmaven.test.skip=true

if [ $? != 0 ] ; then
  fatal_error "mvn clean install -Dmaven.test.skip=true failed"
fi

cd $BUILD_DIR/cytoscape/cytoscape/gui-distribution/packaging

if [ $? != 0 ] ; then
  fatal_error "Unable to cd to $BUILD_DIR/cytoscape/cytoscape/gui-distribution/packaging"
fi

mvn clean install -U

if [ $? != 0 ] ; then
  fatal_error "mvn clean install -U failed"
fi 

cp -f $BUILD_DIR/cytoscape/cytoscape/gui-distribution/packaging/target/media/* $WEB_DIR
if [ $? != 0 ] ; then
  fatal_error "cp -f $BUILD_DIR/cytoscape/cytoscape/gui-distribution/packaging/target/media/* $WEB_DIR failed"
fi

cp -f $BUILD_DIR/cytoscape/cytoscape/gui-distribution/assembly/target/*.{gz,zip} $WEB_DIR
if [ $? != 0 ] ; then
  fatal_error "cp -f $BUILD_DIR/cytoscape/cytoscape/gui-distribution/assembly/target/*.{gz,zip} $WEB_DIR failed"
fi

exit 0
