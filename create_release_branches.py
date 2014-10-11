#!/usr/local/bin/python

#
# Create new release branch from develop.
# 
# - What is this for?
# 
# 1. Create new release branch for each sub project.
# 2. Run maven versions to update version number.
# 3. Update properties by sed (this is a hack...)
# 4. Commit all changes 
#

import sys
import argparse
import subprocess
import os


targets = ('parent', 'api', 'impl', 'support', 'gui-distribution', 'app-developer')

#
# Reset all local changes and delete release branch.
#
def refresh(version):
    p = subprocess.Popen(['git', 'reset', '--hard', "HEAD"], 
            stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    p.communicate()
    
    for target in targets:
        os.chdir(target)
        print(os.getcwd())
        p = subprocess.Popen(['git', 'checkout', 'develop'])
        out, err = p.communicate()
        p = subprocess.Popen(['git', 'branch', '-D', 'release/' + str(version)])
        out, err = p.communicate()

        p = subprocess.Popen(['git', 'reset', '--hard', "HEAD^"], 
                stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        out, err = p.communicate()
        print out
        p = subprocess.Popen(['git', 'clean', '-f'], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        out, err = p.communicate()
        print out
        if err:
            sys.exit(1)

        os.chdir("..")

#
# Pull all changes from upstream.
#
def pull():
    for target in targets:
        print("Module = " + target)
        os.chdir(target)
        print(os.getcwd())
        p = subprocess.Popen(['git', 'pull'], 
                stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        out, err = p.communicate()
        print out
        os.chdir("..")


def update_version_numbers(version):
    p = subprocess.Popen(['mvn', 'versions:set', '-DnewVersion=' + version], 
            stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out, err = p.communicate()
    print out

    p = subprocess.Popen(['mvn', 'versions:commit'], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out, err = p.communicate()
    print out
    return


def build():
    p = subprocess.Popen(['mvn', 'clean', 'install'])
    out, err = p.communicate()
    if err:
        print(err)
        sys.exit(1)

    print out


def branch(version):
    new_release_branch = 'release/' + str(version)

    for target in targets:
        os.chdir(target)
        # Checkout develop.
        p = subprocess.Popen(['git', 'checkout', 'develop'])
        out, err = p.communicate()
        if err:
            print(err)
            sys.exit(1)
        p = subprocess.Popen(['git', 'branch', new_release_branch])
        out, err = p.communicate()
        if err:
            print(err)
            sys.exit(1)

        p = subprocess.Popen(['git', 'checkout', new_release_branch])
        out, err = p.communicate()
        if err:
            print(err)
            sys.exit(1)

        os.chdir("..")


def update_version(version):
    
    # Set versions from 
    os.chdir('parent')
    p = subprocess.Popen(['mvn', 'versions:set', '-DnewVersion=' + version])
    out, err = p.communicate()
    if err is not None:
        print(err)
        sys.exit(1)
    
    os.chdir("..")

    # Remove backup files.
    for target in targets:
        os.chdir(target)

        p = subprocess.Popen(['mvn', 'versions:commit'])
        out, err = p.communicate()
        if err is not None:
            print(err)
            sys.exit(1)

        os.chdir("..")


def update_props(version):
    replace = 'find . -name pom.xml | xargs sed -i "" -e \'s/' + version + '-SNAPSHOT/' + version + '/g\''
    subprocess.call(replace, shell=True)

def update_develop_props(old_version, next_version):
    replace = 'find . -name pom.xml | xargs sed -i "" -e \'s/' + old_version + '-SNAPSHOT/' + next_version + '-SNAPSHOT/g\''
    subprocess.call(replace, shell=True)


def commit(message):
    for target in targets:
        os.chdir(target)

        p = subprocess.Popen(['git', 'add', '-A'])
        p.communicate()
        p = subprocess.Popen(['git', 'commit', '-am', message])
        p.communicate()
        os.chdir("..")



# main
def main():

    print("++ Release Branch Maker ++")
    
    # Parse commandline arguments.
    parser = argparse.ArgumentParser()

    # Required parameter 1: Cytoscape top directory. 
    parser.add_argument('-d', '--dir', required=True)
    parser.add_argument('-v', '--version', required=True)
    parser.add_argument('-n', '--next', required=True)

    parser.add_argument('-u', '--update', action="store_true", default=False)
    parser.add_argument('-b', '--build', action="store_true", default=False)
    parser.add_argument('-r', '--reset', action="store_true", default=False)
    args = parser.parse_args()


    print("=========== Args ==============")
    print(args)
    print("===============================")
    
    os.chdir(args.dir)

    if args.reset:
        print("=========== RESET all local changes ==============")
        refresh(args.version)
        return

    if args.update:
        print("=========== Pull everything from upstream ==============")
        pull()
    
    if args.build:
        print("=========== Build entire Cytoscape project ==============")
        build()
        return

    print("######### Creating new release branches for " + args.version + " #########")
    print("Target dir is: " + os.getcwd())

    err = branch(args.version)
    if err:
        print("ERROR!: " + err)
        return

    # update_version(args.version)
    # update_props(args.version)
    commit(args.version + ' release branch created.')

    # Swicth back to develop
    for target in targets:
        os.chdir(target)
        # Checkout develop.
        p = subprocess.Popen(['git', 'checkout', 'develop'])
        out, err = p.communicate()
        if err:
            print(err)
            sys.exit(1)
        os.chdir("..")

    # Finally, update develop's version number
    update_version(args.next + '-SNAPSHOT')
    update_develop_props(args.version, args.next)
    commit('From now on, development branch is for ' + args.next + '.')

    # build()
    
    print("=========== Success!  Don't forget to commit ==============")


if __name__ == '__main__':
    main()
