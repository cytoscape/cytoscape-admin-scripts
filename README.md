# cytoscape-admin-scripts

## Introduction

This repository contains scripts and instructions for managing the Cytoscape Release process, system requirements checking, and other core Cytoscape organization tools.

### Primary build scripts

These are the primary scripts used for building installable versions of Cytoscape. These, or their eventual replacements, should always be able to produce a Cytoscape build and the accompanying Install4j installers.

Both scripts drive the `cy.sh` repository management script from https://github.com/cytoscape/cytoscape; see https://github.com/cytoscape/cytoscape/pull/34 for its commands. `STARTING_BRANCH` must name a branch whose `cy.sh` includes that change, and each script checks this before building.

* ```release-generator/build-nightly-release.sh```
  - A fully automated build that can be run via a cron job. This build generates installers and puts them in a www accessible directory. This script DOES NOT sign the Mac installer, as nightly builds are not intended for public consumption.

* ```release-generator/jupyter-notebooks/Cytoscape SNAPSHOT Release Builder.ipynb```
  - A step by step Jupyter notebook that generates a release from the develop branch. This script generates installers and puts them in a www accessible directory. This script signs Mac installers and is a public consumable SNAPSHOT.

### System checker script

* ```/system-checker```
  - These are OS specific scripts intended for Cytoscape users to run to evaluate if their system can run Cytoscape. These script files are linked to from [cytoscape.org]() help pages, and should not be moved or renamed without changing the relevant pages in [cytoscape.org]().

### Project statistics

* ```/project-stats```
  - Scripts that generate the statistics and reports behind the [Cytoscape Project Statistics page](https://cytoscape.org/stat.html): desktop and app downloads, desktop starts, app publications cited in the App Store, and Cytoscape publication data. Each subdirectory has its own README covering requirements and how to run it.
