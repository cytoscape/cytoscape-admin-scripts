#!/usr/local/bin/python
#
# Quick & dirty sanity check script for hotfix releases.
#
# Simply displays all commits which does not exists in hotfix branch.
#


import sys
import argparse
import subprocess
import os

f = open('sanity.txt', 'w')

modules = ("api", "impl", "support", "gui-distribution", "app-developer")

for module in modules:
    os.chdir(module)
    f.write("\n\n========== " + module + ": List of commits only in develop branch =============\n")
    try:
        out_bytes = subprocess.check_output("git log --oneline hotfix/3.1.1..develop --format=format:'%an    %ad    %H    %s'", shell=True)
    except subprocess.CalledProcessError as e:
        out_bytes = e.output
        code = e.returncode

    result = {}
    # result_text = out_bytes.decode("utf-8")
    lines = str(out_bytes).split("\n")
    for line in lines:
        entry = line.split("    ")
        if len(entry) is 4:
            name = entry[0]

            entries = []
            if name in result:
                entries = result[name]

            entries.append(entry[1:4])
            result[name] = entries


    subprocess.call(['git', 'checkout', 'develop'])

    try:
        out4 = subprocess.check_output("git log --oneline develop..hotfix/3.1.1 --format=format:'%s'", shell=True)
    except subprocess.CalledProcessError as e:
        out4 = e.output
        code = e.returncode

    lines = str(out4).split("\n")
    in_dev = []
    for line in lines:
        in_dev.append(line)


    count = 0
    for name in result:
        entries = result[name]
        f.write("\n# Committer: " + name + "\n")
        for entry in entries:
            if entry[2] in in_dev:
                print("Dupricate: " + str(entry))
            else:
                f.write(entry[0] + "\t" + entry[1] + "\t" + entry[2] + "\n")


    try:
        out3 = subprocess.check_output("git checkout hotfix/3.1.1", shell=True)
    except subprocess.CalledProcessError as e:
        out3 = e.output
        code = e.returncode
    os.chdir("..")

f.close()
