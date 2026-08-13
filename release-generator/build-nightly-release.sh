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
  echo "    Both directories may be relative or absolute, but neither may contain blanks:"
  echo "    Cytoscape cannot be built from a path containing spaces or tabs."
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


# cy.sh is versioned alongside the code it builds, so this constant also selects which
# cy.sh runs.  It must name a branch whose cy.sh includes
#   https://github.com/cytoscape/cytoscape/pull/34
# which is commit a9ce955f0cbd09c984bb843a7560850a1a7e4d05 on develop.  Older branches
# carry a cy.sh with no 'pull' that clones and no 'build' command, so this script cannot
# build from them.  Check a candidate branch with:
#   git merge-base --is-ancestor a9ce955f0cbd09c984bb843a7560850a1a7e4d05 origin/<branch>
STARTING_BRANCH=develop
CY_SH_COMMIT=a9ce955f0cbd09c984bb843a7560850a1a7e4d05


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

# Everything below changes directory and then refers back to $BUILD_DIR and $WEB_DIR, so
# both have to be absolute.  Resolve them here, relative to the directory this script was
# invoked from, rather than requiring the caller to have passed absolute paths.
BUILD_DIR=`cd "$BUILD_DIR" && pwd`
if [ $? != 0 ] ; then
  fatal_error "Unable to cd to $1"
fi

WEB_DIR=`cd "$WEB_DIR" && pwd`
if [ $? != 0 ] ; then
  fatal_error "Unable to cd to $2"
fi

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

cd $BUILD_DIR/cytoscape

if [ $? != 0 ] ; then
  fatal_error "Unable to cd to $BUILD_DIR/cytoscape"
fi

# A clone lands on whatever the remote's default branch happens to be, so say which branch
# this build is of before running anything out of the tree - including cy.sh itself.
git checkout ${STARTING_BRANCH}

if [ $? != 0 ] ; then
  fatal_error "git checkout ${STARTING_BRANCH} failed in $BUILD_DIR/cytoscape"
fi

# Fail here rather than three commands later.  Without this check, a branch whose cy.sh
# predates $CY_SH_COMMIT gets part way through: 'pull' pulls the repos that already exist
# but clones none, then 'build' reports "Invalid command build" - and neither message says
# "wrong branch".
git merge-base --is-ancestor $CY_SH_COMMIT HEAD

if [ $? != 0 ] ; then
  fatal_error "${STARTING_BRANCH} does not contain the cy.sh from https://github.com/cytoscape/cytoscape/pull/34 - it has no 'pull' that clones and no 'build' command, so this build cannot run"
fi

# 'pull' clones the sub projects - parent, api, impl, support, gui-distribution and
# app-developer - into this directory, and puts each new clone on develop.  A zero exit
# therefore means every repository is on develop, which is what this build wants: the
# tree was re-cloned above, so nothing is left over from a previous run to clean, reset
# or switch.  That guarantee depends on the tree being fresh; if this script is ever
# changed to reuse an existing tree, the branch of each repository has to be checked.
./cy.sh pull

if [ $? != 0 ] ; then
  fatal_error "./cy.sh pull failed in $BUILD_DIR/cytoscape"
fi

# 'build' rather than a plain 'mvn install': api and impl fork a generate-sources
# lifecycle that resolves from the local maven repository instead of the reactor, so the
# inner projects have to be built first for a cold repository to work at all.  It also
# uses -DskipTests and not -Dmaven.test.skip=true, because many modules depend on another
# module's test-jar and skipping test compilation altogether never produces them.
./cy.sh build

if [ $? != 0 ] ; then
  fatal_error "./cy.sh build failed in $BUILD_DIR/cytoscape"
fi

# The installers are a separate build: packaging is a module of gui-distribution's
# 'release' profile only, so the build above does not include it.
cd $BUILD_DIR/cytoscape/gui-distribution/packaging

if [ $? != 0 ] ; then
  fatal_error "Unable to cd to $BUILD_DIR/cytoscape/gui-distribution/packaging"
fi

mvn clean install -U

if [ $? != 0 ] ; then
  fatal_error "mvn clean install -U failed"
fi 

cp -f $BUILD_DIR/cytoscape/gui-distribution/packaging/target/media/* "$WEB_DIR"
if [ $? != 0 ] ; then
  fatal_error "cp -f $BUILD_DIR/cytoscape/gui-distribution/packaging/target/media/* $WEB_DIR failed"
fi

cp -f $BUILD_DIR/cytoscape/gui-distribution/assembly/target/*.{gz,zip} "$WEB_DIR"
if [ $? != 0 ] ; then
  fatal_error "cp -f $BUILD_DIR/cytoscape/gui-distribution/assembly/target/*.{gz,zip} $WEB_DIR failed"
fi

exit 0
