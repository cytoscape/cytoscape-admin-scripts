# [Cytoscape](https://cytoscape.org) Downloads

This directory contains scripts to generate plots and summary reports
for [Cytoscape](https://cytoscape.org) desktop downloads as well as [Cytoscape](https://cytoscape.org) App downloads.
 

## Requirements

 * Python 3.6+
 * numpy
 * matplotlib

## Cytoscape desktop download stats

This section describes the steps to generate statistics and figures
for downloads of the [Cytoscape](https://cytoscape.org) desktop application. Since 2018 [Github](https://github.com)
has been serving the installer files for the [Cytoscape](https://cytoscape.org) desktop application.

### Step 1 Download JSON file from github

Either via browser or command line download contents of this link
to a file: https://api.github.com/repos/cytoscape/cytoscape/releases

```bash
    curl https://api.github.com/repos/cytoscape/cytoscape/releases > `date +%m_%d_%Y`_releases.json 
```

**NOTE:** The file `4_13_2021_releases.json` is an example download from above link on April 13, 2021


### Step 2 Generate Report

Open a terminal with required [Python](https://python.org) and packages installed as noted
in the requirements section and run the following command:

```Bash
./cytoscape_download_stats.py `date +%m_%d_%Y`_releases.json ./cytoscape_report -vvv
```

**NOTE:** Be sure to use an update file from Step 1 since the report uses todays
          date in the calculations.

The above command will parse the file passed and generate files under
`./cytoscape_report` directory.

### Step 3 Review results
 
 A summary of downloads per version will be output to standard out and 
 two `svg` files will be written to the output directory specified on the command
 line (`./cytoscape_report` if above command was invoked)
 
 * `downloads_by_platform.svg`

   Plot that shows a breakdown of downloads by platform. This plot is the one displayed
   on under **Misc.** section of [Cytoscape Project Statistics page](https://cytoscape.org/stat.html)
     
 * `downloads_byday.svg` 
   
    Plot that shows breakdown of downloads per day by Cytoscape Version. 

## [Cytoscape](https://cytoscape.org) App download stats

This section describes the steps to generate statistics and figures
for downloads of [Cytoscape Apps.](https://appstore.cytoscape.org) 

### Step 1 Download JSON file from [AppStore](https://appstore.cytoscape.org)

Either via browser or command line download contents of this link
to a file: http://apps.cytoscape.org/download/stats/timeline

```bash
    curl http://apps.cytoscape.org/download/stats/timeline > `date +%m_%d_%Y`_app_downloads.json 
```

**NOTE:** The file `4_21_2021_app_downloads.json` is an example download from above link on April 21, 2021


### Step 2 Generate report

Open a terminal with required [Python](https://python.org) packages installed and run the following command:

```Bash
./app_download_stats.py `date +%m_%d_%Y`_app_downloads.json ./app_report -vvv
```

### Step 3 Review results

A summary of downloads per version and platform will be output to standard out and 
 two `svg` files will be written to the output directory specified on the command
 line (`./app_report` if above command was invoked)
 
 * `summary.txt`
 
    Contains summary text of date range for report and total App downloads.
 
 * `app_downloads_per_day.svg`

   Plot that shows a breakdown of App downloads per day. This plot is the one displayed
   on under **App Store** section of [Cytoscape Project Statistics page](https://cytoscape.org/stat.html)
