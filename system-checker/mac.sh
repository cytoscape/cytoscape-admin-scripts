#!/bin/bash

####################################
# System checker script for Mac
####################################

# Target Cytoscape version for this script
CYTOSCAPE_VERSION="3.10.3"

# Supported Mac OS versions
SUPPORTED_OS_VERSIONS=("10" "11" "12" "13" "14" "15")

# Supported Java verisons
# NOTE: Code below does not support checking for
#       multiple versions of java if set in this
#       variable
SUPPORTED_JAVA_VERSIONS=("17")

# Default location for  JDK.
JVM_LOCATION="/Library/Java/JavaVirtualMachines"

# Global test pass variable. If 0 all tests pass otherwise positive number
TEST_STATUS=0

########################################################
#
# Function to get version of java from command line and
# returns 0 if version is a supported version otherwise
# returns 1
#
# Function also sets following variables:
# JAVA_VERSION_ORIGINAL - raw output from java -version
# JAVA_VERSION - version of java extracted ie 17.0.5
# JAVA_MAJOR_VERSION - major version of java ie 17
#
#########################################################
query_for_java_version () {
	java_binary=$1
	JAVA_VERSION_ORIGINAL=$($java_binary -version 2>&1)
  	JAVA_VERSION=$(echo $JAVA_VERSION_ORIGINAL | awk 'NR==1{gsub(/"/,""); print $3}')
  	JAVA_MAJOR_VERSION=$(echo $JAVA_VERSION | awk -F'\.' '{print $1}')

  	if [[ $JAVA_MAJOR_VERSION == ${SUPPORTED_JAVA_VERSIONS[0]} ]] ; then
    	return 0
  	fi 
	return 1
}

# This user's shell
shell=$(echo $SHELL | awk -F'/' '{print $(NF)}')

echo "############# Cytoscape System Requirements Checker for Mac ##############"
echo ""
echo "Target Cytoscape version: $CYTOSCAPE_VERSION"

echo "Your shell is $shell"
echo "Testing system"

which sysctl > /dev/null 2>&1

if [ $? == 0 ] ; then
	mem_in_bytes=`sysctl -n hw.memsize 2> /dev/null`
	if [ $? == 0 ] ; then
    	mem_in_mb=`echo "ceil($mem_in_bytes/1024/1024,0)" | bc -l`
		if [ "$mem_in_mb" -ge 756 ] ; then
			echo " - Pass: Your machine has $mem_in_mb megabytes of ram"
		else
			echo " - Fail: Your machine has $mem_in_mb megabytes of ram. "
			echo "         Cytoscape may have issues with less then 756 megabytes of ram." 
			TEST_STATUS=1
		fi	
		
	fi
fi

# Extract major version
os_version_full=$(sw_vers -productVersion)
os_version=$(echo $os_version_full | awk -F'.' '{print $1}')

# Check OS version.
os_pass=0
for os in "${SUPPORTED_OS_VERSIONS[@]}"
do
    if [ "$os" = $os_version ]
    then
        os_pass=1
        break
    fi
done

if [ "$os_pass" -eq 1 ]
then
    echo " - Pass: OS Version = $os_version_full"
else
	echo " - Fail: $os_version_full is not a supported OS. Cytoscape may not work or have issues."
	TEST_STATUS=2
fi

# Check Java Version
# See if Cytoscape is installed and if bundle is within
	
for Y in `find /Applications -maxdepth 1 -name "Cytoscape_v${CYTOSCAPE_VERSION}" -type d` ; do
	java_binary="${Y}/.install4j/jre.bundle/Contents/Home/bin/java"
    if [ -e $java_binary ] ; then
		query_for_java_version "$java_binary"

  		if [ $? -eq 0 ] ; then
    		echo " - Pass: Java $JAVA_VERSION bundled with installed Cytoscape at"
			echo "         $Y"
  		fi
	fi
done

# Test 2: Check for Java under $JVM_LOCATION
jvms=$(find $JVM_LOCATION -name jdk-17.0* -type d)
jvm_test=$(echo $jvms | awk '{if(NF>=1){print 1}else{print 0}}')

if [[ $jvm_test -eq 1 ]]; then
	found_jvm_path=`echo $jvms | awk '{gsub(/ /, "\n", $0);print}'`
	echo " - Pass: Suitable system installs of JDK(s) found:"
	for j_path in `echo $jvms` ; do
		echo "         $j_path"
	done
fi

# Test 3: Try java -version command
query_for_java_version "java"	
if [ $? -eq 0 ] ; then
	echo " - Pass: java binary on path is a supported version $JAVA_VERSION"
fi

# Test 4: Check Java Home
if [[ $JAVA_HOME != "" ]]; then
	if [ -e "$JAVA_HOME/bin/java" ] ; then
		query_for_java_version "$JAVA_HOME/bin/java"
		if [ $? -eq 0 ] ; then
	    	echo " - Pass: JAVA_HOME found with supported version of java:"
			echo "         $JAVA_HOME"
		fi
	fi
fi

# Test 4: Connect to App Store
which curl > /dev/null 2>&1

if [ $? != 0 ] ; then
	echo " - Possible Fail: curl command not found. Unable to check if AppStore"
	echo "                  is accessible. Please open a web browser and verify"
    echo "                  https://apps.cytoscape.org is accessible"
	TEST_STATUS=3
else
	APPSTORE=$(curl -I https://apps.cytoscape.org 2> /dev/null | awk 'NR==1{print $2}')

	if [[ $APPSTORE -eq "200" ]]; then
    	echo " - Pass: You are ready to run Cytoscape $CYTOSCAPE_VERSION"
	else
		echo " - Fail: Seems App Store at https://apps.cytoscape.org is not reachable."
	    echo "         Please check firewall setting from System Preference or"
		echo "         or see if the appstore can be accessed in a web browser"
	    TEST_STATUS=4
	fi
fi

exit $TEST_STATUS
