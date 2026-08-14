# cytoscape-admin-scripts

## Introduction

This repository contains scripts and instructions for managing the Cytoscape Release process, system requirements checking, and other core Cytoscape organization tools.

### Primary build scripts

These are the primary scripts used for building installable versions of Cytoscape. These, or their eventual replacements, should always be able to produce a Cytoscape build and the accompanying Install4j installers.

Both scripts drive the `cy.sh` repository management script from https://github.com/cytoscape/cytoscape; 

* ```release-generator/build-nightly-release.sh```
  - A fully automated build that can be run via a cron job. This build generates installers and puts them in a www accessible directory. This script DOES NOT sign the Mac installer, as nightly builds are not intended for public consumption.

* ```release-generator/jupyter-notebooks/Cytoscape SNAPSHOT Release Builder.ipynb```
  - A step by step Jupyter notebook that generates a release from the develop branch. This script generates installers and puts them in a www accessible directory. This script signs Mac installers and is a public consumable SNAPSHOT.
  - Start it with ```release-generator/jupyter-notebooks/run-jupyter.sh```, which sets the environment the notebook expects, checks the toolchain, and launches Jupyter. See below.

#### Running the SNAPSHOT notebook

The notebook takes its configuration from the environment. Jupyter passes its own environment to the kernel, so these must be set **before** Jupyter starts. `run-jupyter.sh` does this for you:

```bash
cd release-generator/jupyter-notebooks
./run-jupyter.sh
```

It refuses to start Jupyter unless `javac` and `java` are 17 or newer, Maven is present, and git is at least 1.8.5.

Every value can be overridden with envioronment variables:

| variable | default | what it does |
|---|---|---|
| `STARTING_BRANCH` | `develop` | branch to build; use `release/3.X.X` for a minor release |
| `JAVA_HOME` | `/opt/jdk-17` | JDK used for the build; must be 17 or newer |
| `MAVEN_HOME` | `/opt/maven` | Maven installation |
| `PUBLISH_ROOT` | `/var/www/html/cytoscape-builds` | installers are published under `$PUBLISH_ROOT/Cytoscape-<version>/<date>`, where the version comes from the built tree's `pom.xml` |
| `ADMIN_SCRIPTS_DIR` | the checkout this script is in | which checkout the notebook builds in |
| `PORT` | `8888` | port Jupyter listens on |

```bash
STARTING_BRANCH=release/3.11.1 PORT=8889 ./run-jupyter.sh
```

Run the notebook from the top. Sections 5 and 6 publish to the web root and submit the Mac disk image for notarization, so stop before section 5 unless you intend to publish.

### System checker script

* ```/system-checker```
  - These are OS specific scripts intended for Cytoscape users to run to evaluate if their system can run Cytoscape. These script files are linked to from [cytoscape.org]() help pages, and should not be moved or renamed without changing the relevant pages in [cytoscape.org]().

### Project statistics

* ```/project-stats```
  - Scripts that generate the statistics and reports behind the [Cytoscape Project Statistics page](https://cytoscape.org/stat.html): desktop and app downloads, desktop starts, app publications cited in the App Store, and Cytoscape publication data. Each subdirectory has its own README covering requirements and how to run it.
