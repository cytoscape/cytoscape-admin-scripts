#!/usr/local/bin/python

#
# Simple script to switch version numbers and properties to given value. 
# 
#

import sys
import argparse
import subprocess
import os


# List of sub-projects to be updated.
targets = ('parent', 'api', 'impl', 'support', 'gui-distribution', 'app-developer')


#
# Function to update the 
# 
def update_version_numbers(version):
    p = subprocess.Popen(['mvn', 'versions:set', '-DnewVersion=' + version], 
            stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out, err = p.communicate()
    print out

    p = subprocess.Popen(['mvn', 'versions:commit'], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out, err = p.communicate()
    print out

    # New version 
    replace = 'find . -name pom.xml | xargs sed -i "" -e \'s/' + version + '-SNAPSHOT/' + version + '/g\''
    subprocess.call(replace, shell=True)
    return



def main():
    print("++ Project Version Updator ++")
    
    # Parse commandline arguments.
    parser = argparse.ArgumentParser()

    # Required parameter 1: Cytoscape top directory. 
    parser.add_argument('-d', '--dir', required=True)
    parser.add_argument('-v', '--version', required=True)

    args = parser.parse_args()


    print("=========== Args ==============")
    print(args)
    print("===============================\n")

    print("=== Updating version number from " + args.version + "-SNAPSHOT to " + args.version + " ===\n\n")
    
    os.chdir(args.dir)
    update_version_numbers(args.version)

    print("============= Done! ==============")
    print("Run 'find . -name pom.xml -print | xargs grep " + args.version + "-SNAPSHOT' to check.")


if __name__ == '__main__':
    main()