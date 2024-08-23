#!/bin/bash

####################################
# System checker script for Mac
####################################

# Target Cytoscape version for this script
CYTOSCAPE_VERSION="3.10.2"

# Supported Mac OS versions
SUPPORTED_OS_VERSIONS=("10" "11" "12" "13" "14")

# Supported Java verisons
SUPPORTED_JAVA_VERSIONS=("17")

# Default location for  JDK.
JVM_LOCATION="/Library/Java/JavaVirtualMachines"

# This user's shell
shell=$(echo $SHELL | awk -F'/' '{print $(NF)}')

echo "############# Cytoscape System Requirements Checker for Mac ##############"
echo "Target Cytoscape version: $CYTOSCAPE_VERSION"

echo "Your shell is $shell"

# Extract major version
os_version_full=$(sw_vers -productVersion)
os_version=$(echo $os_version_full | awk -F'.' '{print $1}')

# Check OS version.
os_pass=0
for os in "${SUPPORTED_OS_VERSIONS[@]}"
do
    if [ "$os" = $os_version ]
    then
        echo "Compatible OS version found: $os_version"
        os_pass=1
        break
    fi
done

if [ "$os_pass" -eq 1 ]
then
    echo " - Pass: OS Version = $os_version_full"
else
    echo "Fail: This version of OS is not supported: $os_version_full"
    echo "Please upgrade your system to ${SUPPORTED_OS_VERSIONS[0]} or newer."
    exit 1
fi

# Check Java Version

# Test 1: Check Java Machine
jvms=$(find $JVM_LOCATION -name jdk-17.0* -type d)
jvm_test=$(echo $jvms | awk '{if(NF>=1){print 1}else{print 0}}')

if [[ $jvm_test -eq 1 ]]; then
    echo " - Pass: Following JDK found:"
    echo ""
    echo $jvms | awk '{gsub(/ /, "\n", $0);print}'
else
    echo "- Fail: No JDK found.  Please download and install a compatible JDK, such as Adoptium OpenJDK:"
    echo "https://adoptium.net/temurin/releases/?version=17&package=jdk"
#    exit 1
fi

# Test 2: Try java -version command
java_version_original=$(java -version 2>&1)
java_version=$(echo $java_version_original | awk 'NR==1{gsub(/"/,""); print $3}')

java_major_version=$(echo $java_version | awk -F'\.' '{print $1}')

if [[ $java_major_version == ${SUPPORTED_JAVA_VERSIONS[0]} ]]
then
    echo " - Pass: Current Java Version = $java_version"
else
    echo "Fail: Java is not reachable or is incorrect version."
    echo "Try installing or re-installing Java 17."
    exit 1
fi

# Tets 3: Check Java Home
if [[ $JAVA_HOME != "" ]]; then
    echo " - Pass: JAVA_HOME found: $JAVA_HOME"
else
    echo "JAVA_HOME is not set."
    echo "Please add the following to your .${shell}rc file:"
    echo "export JAVA_HOME=/Library/Java/JavaVirtualMachines/jdk-17.0_*.jdk/Contents/Home"
    echo "where * is the latest Java 17 update number."
    echo "And then type 'source ~/.${shell}rc'"
    exit 1
fi

# Test 4: Connect to App Store

NUM_TRY=5
echo "Checking connection to Cytoscape App Store..."
#ping_result=$(ping -c $NUM_TRY -t 15 apps.cytoscape.org | grep loss)

#num_success=$(echo $ping_result | awk '{print $4}')

#echo $ping_result

APPSTORE=$(curl -I https://apps.cytoscape.org | awk 'NR==1{print $2}')

if [[ $APPSTORE -eq "200" ]]; then
    echo "Done!  You are ready to run Cytoscape $CYTOSCAPE_VERSION"
else
    echo "https connection to App Store at https://apps.cytoscape.org is not reachable."
    echo "Please check firewall setting from System Preference."
    exit 1
fi

exit 0
