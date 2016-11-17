#!/bin/sh

################################################################################
#
# Script to upload installers to UCSD server
#
################################################################################

BUILD_DIR=$1

# Server name to be used for hosting installers.
REMOTE_SERVER="chenel.ucsd.edu"

# Change this to your account
USER_NAME="kono"

cd ./${BUILD_DIR}/cytoscape/gui-distribution/packaging

# mvn clean install || { echo Abort: Installer Build Failed; exit 1; }
# ./sign-dmg.sh 'Developer ID Application' || { echo Abort: Could not sign DMG for Mac.; exit 1; }

cd ./target/install4j

echo "Uploading new installers..."
deployDir="build-$(date "+%Y-%m-%d-%H-%M-%S-%Z")"

server="$REMOTE_SERVER:~/public_html/data/cy3latest/$deployDir/"

# Create directory
ssh $REMOTE_SERVER mkdir /cellar/users/$USER/public_html/data/cy3latest/$deployDir

# scp ./signed/* $server || { echo Abort: Could not upload signed file.; exit 1; }
scp ./*.dmg $server || { echo Abort: Could not upload signed file.; exit 1; }
scp ./*.exe $server || { echo Abort: Could not upload Windows installers.; exit 1; }
scp ./*.zip $server || { echo Abort: Could not upload zipped file.; exit 1; }
scp ./*.gz $server || { echo Abort: Could not upload gzipped file.; exit 1; }
scp ./*.sh $server || { echo Abort: Could not upload UNIX installer.; exit 1; }

deployURL="http://chianti.ucsd.edu/~$USER_NAME/data/cy3latest/$deployDir"
echo "Finished.  Visit $deployURL"
open $deployURL
