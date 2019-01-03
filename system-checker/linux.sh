#!/bin/bash
####################################
# System checker script for Linux
####################################

# Target Cytoscape version for this script
CYTOSCAPE_VERSION="3.7.1"

# Cytoscpae App Store location
APP_STORE_URL="apps.cytoscape.org"

# Supported Distributions
SUPPORTED_DISTRIBUTIONS=("ubuntu" "centos" "fedora")

# Supported versions for each platform
UBUNTU_VERSIONS=("14.04" "14.10" "15.04" "15.10" "16.04" "16.10" "17 04" "17 10" "18.04" "18.10")
CENTOS_VERSIONS=("6" "7")
FEDORA_VERSIONS=("24" "25" "26")

# Supported Java verisons
SUPPORTED_JAVA_VERSIONS=("1.8.0")

# Error cheking flag
pass=true

# This user's shell
shell=$(echo $SHELL | awk -F'/' '{print $(NF)}')

# 32bit or 64bit?
machine_type=$(uname -m)

echo -e "\n\e[31m##### Cytoscape System Requirements Checker for Linux #####\e[m\n"
echo -e " - Target Cytoscape version: \e[36m$CYTOSCAPE_VERSION\e[m"
echo -e " - Your Shell: \e[36m$shell\e[m"

# Extract major version
distribution=$(lsb_release -si)
os_version=$(lsb_release -sr)

# Check distribution
echo -e "\n\e[;1m===== Checking Distribution =====\e[m\n"

dist_lower=$(echo $distribution | awk '{print tolower($0)}')

echo -e " - Linux Distribution: \e[36m$distribution\e[m"
echo -e " - Version: \e[36m$os_version\e[m"
echo -e " - Target Platform: \e[36m$machine_type\e[m\n"

os_pass=0
for dist in "${SUPPORTED_DISTRIBUTIONS[@]}"
do
    if [[ $dist == $dist_lower ]]; then
        os_pass=1
        break
    fi
done

if [ "$os_pass" -eq 1 ]
then
    echo -e "\e[36;1m - Pass: Distribution = $distribution\e[m"
else
    echo -e "\n\e[31mWARNING: This Linux distribution is not officially supported: $distribution\e[m" 1>&2
    echo "Cytoscape might work with this machine, but not tested."
    echo "Please use any of the following distributions if possible: [${SUPPORTED_DISTRIBUTIONS[@]}]"
    pass=false
fi

# Check version of the distribution

case $dist_lower in
    ubuntu)
        versions=("${UBUNTU_VERSIONS[@]}")
        ;;
    centos)
        versions=("${CENTOS_VERSIONS[@]}")
        ;;
    fedora)
        versions=("${FEDORA_VERSIONS[@]}")
        ;;
    *)
        echo "Error: Could not find supported versions for $dist_lower"
        exit 1
        ;;
esac

version_pass=0
for version in "${versions[@]}"
do
    if [[ $version == $os_version ]]; then
        version_pass=1
        break
    fi
done

if [ "$version_pass" -eq 1 ]
then
    echo -e "\e[36;1m - Pass: OS Version = $os_version\e[m"
else
    echo "Fail: This $distribution version is not supported: $os_version"
    echo "Supported versions are:"
    for ver in "${versions[@]}"
    do
        echo " - $ver"
    done
    pass=false
fi

# Test 2: Try java -version command
echo -e "\n\e[;1m===== Checking Java Version =====\e[m\n"

java_version_original=$(java -version 2>&1 | grep "java version")
java_version=$(echo $java_version_original | awk 'NR==1{gsub(/"/,""); print $3}')
java_major_version=$(echo $java_version | awk -F'_' '{print $1}')

if [[ $java_major_version == ${SUPPORTED_JAVA_VERSIONS[0]} ]]
then
    echo " - Pass: Current Java Version = $java_version"
else
    echo -e "\e[31mError: \"java\" command is not available"
    echo -e "You need to set PATH to \$JAVA_HOME/bin.\e[m"
    echo -e "\nYour current \$PATH:\n"
    echo $PATH
    pass=false
fi

# Tets 3: Check Java Home
echo -e "\n\e[;1m===== Checking \$JAVA_HOME =====\e[m\n"

if [[ $JAVA_HOME != "" ]]; then
    echo " - Pass: JAVA_HOME found: $JAVA_HOME"
else
    echo -e "\e[31mError: \$JAVA_HOME is not set.\e[m\n"
    echo -e "If you don't have Java yet, please download JDK from Oracle web site:\n"
    echo -e "http://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html\n"
    echo -e "\e[31mDon't forget to select correct version.\e[m"
    echo -e "Your machine type is: \e[31m$machine_type\e[m"
    pass=false
fi

# Test 4: Connect to App Store
echo -e "\n\e[;1m===== Checking Connection to Cytoscape App Store =====\e[m\n"

NUM_TRY=4
echo -e " - Checking connection to Cytoscape App Store...\n"

ping_pass=true
host $APP_STORE_URL || echo -e "\e[31mError: Could not resolve $APP_STORE_URL\e[m\n"; ping_pass=false
 
if [[ $ping_pass ]];then
    ping_result=$(ping -c $NUM_TRY -t 15 $APP_STORE_URL | grep loss)
    num_success=$(echo $ping_result | awk '{print $4}')
    
    echo -e "\n\e[36m - Result: $ping_result\e[m"
    
    if [[ $num_success -eq $NUM_TRY ]]; then
        echo -e "\e[36m - Success!"
    else
        echo -e "\e[31mError: Seems connection to App Store is unstable.\e[m\n"
        echo "traceroute result:"    
        traceroute $APP_STORE_URL || echo -e "\n\e[31mError: Please install traceroute command.\e[m\n"
    fi
else
    pass=false
fi

# Summary
echo -e "\n\n\e[;1m----------------------------------------\e[m"

if [[ $pass == true ]]; then
    echo -e "\n - Success!  You are ready to run Cytoscape $CYTOSCAPE_VERSION"
    exit 0
else
    echo -e "\n\e[31mYour system still has some issues."
    echo -e "Please fix those and re-run this script again.\e[m"
    exit 1
fi
