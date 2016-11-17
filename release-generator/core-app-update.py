from bs4 import BeautifulStoneSoup
import re
import csv

import sys, getopt

args = sys.argv
build_dir = args[1]

def replaceVer(node):
    exe = node.executions.find_all('execution')
    for e in exe:
        if e.id.text == 'copy':
            items = e.configuration.artifactItems.find_all('artifactItem')
            for item in items:
                app_name = item.artifactId.text
                if app_name == 'cy-rest':
                    # Special case: cyREST
                    app_name = 'cyREST'
                item.version.string.replace_with(ver_map[app_name])

# Read versions from output of shell script
VER_FILE = './' + build_dir + '/apps/versions.txt'
ver_map = {}

with open(VER_FILE, 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        ver_map[row[0]] = row[1]

print(ver_map)

XMLFILE = './' + build_dir + '/cytoscape/gui-distribution/assembly/pom.xml'

f = open(XMLFILE, 'r')
soup = BeautifulStoneSoup(f.read())
f.close()

res = soup.build.plugins.find_all('plugin')
print(type(res))

for r in res:
    p = r.artifactId
    if p.text == 'maven-dependency-plugin':
        replaceVer(r)

with open(XMLFILE, "w+b") as file:
    file.write(soup.prettify('utf-8', formatter='xml'))
