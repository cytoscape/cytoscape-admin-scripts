# cytoscape-scripts
> Utility Scripts for Cytoscape Core Developers


## History

- 10/10/2014 Version 1.3.0 - Updated for Cytoscape 3.2.0 release.
- 9/11/2013 Version 1.2.0 - This version supports read-only repository for non-core developers.

## Scripts for Developers

### cy
Git Repository management utility command for Cytoscape developers

Documentation is available [here](https://github.com/cytoscape/cytoscape).

## Scripts for Managers

### release.sh
(Under construction... Not fully automated.)


### deploy_installers.sh
This is a script to build, sign DMG, and upload the installers to specified location.

To run this script, you need:

* a Mac with certificate to sign Mac disk image (DMG).
* Entire Cytoscape repository cloned by __*cy*__ script (_cy init_)
* SSH key to access the target server without password

#### How to Run

1. ```cd CYTOSCAPE_TOP_DIR```
1. ```mkdir .cy3```
1. ```cd .cy3```
1. Copy the script to this directory.
1. Edit the script: _USER\_NAME_ should be your account
1. Run ```./deplstallers.sh -au BRANCH_NAME``` where _BRANCH\_NAME_ is the name of branch you want to deploy.
1. Once it's done, it opens the browser and displays the uploaded files.




