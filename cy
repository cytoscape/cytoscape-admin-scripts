#!/bin/sh
#
# @(#) cy version 1.0 4/25/2013
#
#  USAGE:
#    init
#
# DESCRIPTION:
#   Cytoscape 3 repository management utility.
#   This script is only for core developers.
#
# Reqiirments:
#   - git
#   - git-flow
#
# By Keiichiro Ono (kono at ucsd edu)
#
###############################################################################

# Command Name
CMDNAME=$(basename $0)

# Error Message
ERROR_MESSAGE="Usage: $CMDNAME [-h] [action]"

# Help
HELP='Cytoscape repository management tool'

# Git base URL
BASE_URL='git@github.com:cytoscape/cytoscape-'
NON_CORE_URL='git://github.com/cytoscape/cytoscape-'

# Cytoscape repository names
REPOSITORIES=(parent api impl support headless-distribution gui-distribution app-developer samples)


#######################################
# Handling command-line arguments     #
#######################################
while getopts 'hrd:' OPT
do
  case $OPT in
    r)  FLG_R=1
        echo " - Using read-only repository."
        ;;
    h)  FLG_H=1
        echo "$HELP: $ERROR_MESSAGE"
        exit 0
        ;;
    ?)  echo $ERROR_MESSAGE 1>&2
        exit 1 ;;
  esac
done

shift $(($OPTIND - 1))

COMMAND=$1
TARGET_DIR=$2

if [[ -z $COMMAND ]]; then
  echo "COMMAND is required. $ERROR_MESSAGE" 1>&2
  exit 1
fi


###############################################################################
# Functrions
###############################################################################

function reset {
  echo "This command resets all of your local changes!"
  confirm

  for REPO in "${REPOSITORIES[@]}"; do
    echo "\n - Resetting local changes: $REPO"
    cd $REPO
    git clean -f
    git reset --hard
    cd ..
  done
}

function pull {
  for REPO in "${REPOSITORIES[@]}"; do
    cd $REPO
    echo "Downloading changes from upstream: $REPO"
    git pull
    cd ..
  done
}

function push {
  echo "- Sending all local commits to upstream..."
  for REPO in "${REPOSITORIES[@]}"; do
    cd $REPO
    git push -u origin
    cd ..
  done
}

function status {
  for REPO in "${REPOSITORIES[@]}"; do
    cd $REPO || { echo Could not find subproject; exit 1; }
    echo "\n- $REPO:"
    git status
    cd ..
  done

}


function switch {
  if [[ -z $TARGET ]]; then
    echo "Branch name is required: cy switch BRANCH_NAME" 1>&2
    exit 1
  fi

  for REPO in "${REPOSITORIES[@]}"; do
    echo "\n - Switching to ${TARGET}: $REPO"
    cd $REPO || { echo Could not find subproject; exit 1; }

    # Switch
    git checkout $TARGET || { echo Could not checkout branch $TARGET; exit 1; }
    cd ..
  done

}

# Not finished yet.
function resetAll {
  git checkout master
  git reset --hard $(git BRANCH -av | grep "remotes/origin/master" | awk '{ print $2 }')
  git checkout develop
  git reset --hard $(git BRANCH -av | grep "remotes/origin/develop" | awk '{ print $2 }')
  git checkout $BRANCH
  git reset --hard $(git BRANCH -av | grep "remotes/origin/$BRANCH" | awk '{ print $2 }')
  git BRANCH -avv
}

function confirm {
  printf 'Do you really want to continue?  Type [yes] to proceed: '
  read answer

  if [[ $answer != 'yes' || -z $answer ]]; then
    echo "Abort\n"
    exit 0
  fi
}

#################################################################################
#
# Project initializer.
#
#   This function clones top-level pom.xml and then clones all sub-projects
#   into the top-level Cytoscape directory.
#
#   Use -d option to specify directory.  Otherwise, it will create new project
#   in the current directory.
#
#################################################################################
function init {
  # By default, clone everything in current directory.

  echo "Target directory = $TARGET_DIR"

  if [[ -z "$TARGET_DIR" ]]; then
    TARGET_DIR=$(pwd)
  elif ! [ -e "$TARGET_DIR" ]; then
    echo "No such dir: $TARGET_DIR"
    exit 1
  fi

  echo "Cytoscape project will be cloned to: ${TARGET_DIR}"

  cd $TARGET_DIR || { echo Could not find target directory: $TARGET_DIR; exit 1; }

  # Clone cy
  let LENGTH=${#BASE_URL}-1

  CY3REPO_URL=$(echo $BASE_URL | cut -c 1-$LENGTH)
  git clone "${CY3REPO_URL}.git" || { echo Could not clone remote repository: $TARGET_DIR; exit 1; }

  cd cytoscape

  for REPO in "${REPOSITORIES[@]}"; do
    REPO_URL="$BASE_URL$REPO.git"
    echo "Cloning: $REPO (URI = $REPO_URL)"
    git clone $REPO_URL $REPO
    cd $REPO
    git checkout master
    git flow init -d
    git checkout develop
    cd ..
  done

  echo "\n\n - Finished: here is the current status:\n"
  status
}



###############################################################################
# Main workflow
###############################################################################

# Save current directory location
START_DIR=$(pwd)

case $COMMAND in
  init )    init ;;
  reset )    reset ;;
  push )    push ;;
  pull )    pull ;;
  switch )  switch ;;
  status )  status ;;

  * )      echo "Invalid command $COMMAND: $ERROR_MESSAGE"
          exit 1;;
esac
