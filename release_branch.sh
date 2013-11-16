#!/bin/sh
#
#
# Create release branches from develop
# 
#  1. TAG the project to the target version.
#  2. Start Release branch
#  3. Push changes to the upstream.
# 
#  by Keiichiro Ono
#

##### Target Repositories #####
REPOSITORIES=(parent api support impl gui-distribution app-developer)


#
# Reset all local changes.
#  This deletes all local changes!
#
function resetAll {
	git checkout master
	git reset --hard $(git branch -av | grep "remotes/origin/master" | awk '{ print $2 }')
	git checkout develop
	git reset --hard $(git branch -av | grep "remotes/origin/develop" | awk '{ print $2 }')
	git checkout $branch
	git reset --hard $(git branch -av | grep "remotes/origin/$branch" | awk '{ print $2 }')
	git branch -avv
}


while getopts 'c:' OPT
do
	case $OPT in
		c)	FLG_C=1
				branch="$OPTARG"
				;;
		?)	echo $ERROR_MESSAGE 1>&2
				exit 1 ;;
	esac
done

#######################################
# Reset everything                    #
#######################################
if [ "$FLG_C" ]; then
	echo " - Clear option is ON."
	# Cleanup and exit
	if [ -z $branch ]; then
		echo "Branch name is required to reset."
		exit 1
	fi

	for project in "${REPOSITORIES[@]}"; do
		echo "\n - Resetting local changes: $project"
		cd ../$project
		resetAll
	done

	echo "\n\n - Everything had been reset to HEAD of remote branches."
	exit 0
fi

