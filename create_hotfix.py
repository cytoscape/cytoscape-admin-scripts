#!/usr/local/bin/python
# Hotfix release
# Release script for Hotfixes.
import sys
import argparse
import subprocess
import os


targets = ("api", "impl", "support", "gui-distribution", "app-developer")

def refresh():
    for target in targets:
        os.chdir(target)
        print(os.getcwd())
        p = subprocess.Popen(['git', 'reset', '--hard', "HEAD"], 
                stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        out, err = p.communicate()
        print out
        p = subprocess.Popen(['git', 'clean', '-f'], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        out, err = p.communicate()
        print out

        os.chdir("..")


def update_versions(target, version):
    print("Module = " + target)
    print("Version = " + version)
    os.chdir(target)
    print(os.getcwd())
    p = subprocess.Popen(['mvn', 'versions:set', '-DnewVersion=' + version], 
            stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out, err = p.communicate()
    print out

    p = subprocess.Popen(['mvn', 'versions:commit'], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out, err = p.communicate()
    print out

def build():
    p = subprocess.Popen(['mvn', 'clean', 'install'])
    p.communicate()

def commit(target, message):
    os.chdir(target)

    p = subprocess.Popen(['git', 'add', '-A'])
    p.communicate()
    p = subprocess.Popen(['git', 'commit', '-am ' + message])
    p.communicate()



# main
def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-v', '--version')
    parser.add_argument('-d', '--dir', required=True)
    parser.add_argument('reset', nargs='?')
    parser.add_argument('-c', '--commit', nargs=1, required=False)
    parser.add_argument('-t', '--test', required=False, nargs='?')
    args = parser.parse_args()

    if not args.dir:
        print("No target")
        return
    else:
        os.chdir(args.dir)

    if args.reset:
        print("=========== RESET ==============")
        refresh()
        return

    if args.commit:
        print("Commit changes...")
        for target in targets:
            commit(target, args.commit[0])
            os.chdir("..")

        return



    if args.version is None:
        print('Version number is missing.');
        return

    print("######### Creating release candidate for " + args.version + " #########")
    print("Target dir is: " + os.getcwd())



    for target in targets:
        update_versions(target, args.version)
        if args.test:
            build()
        os.chdir("..")



if __name__ == '__main__':
    main()
