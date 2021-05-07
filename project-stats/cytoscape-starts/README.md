# [Cytoscape](https://cytoscape.org) Starts

This directory contains a script to generate plots and summary reports
for [Cytoscape](https://cytoscape.org) desktop starts. 

## Requirements

 * Python 3.6+
 * tqdm
 * numpy
 * matplotlib


### Step 1 Retrieve access logs

Obtain the access logs (~15 gigabytes) and store them in a directory. This
can be done by asking the Ideker lab Sys Admin.


### Step 2 Generate Report

Open a terminal with required [Python](https://python.org) packages installed
and run the following command:

```Bash
./cytoscape_start_stats.py ./access_logs_dir ./cytoscape_starts_report -vvv
```

**NOTE:** It is assumed all the access logs are stored in `./acess_logs_dir`

**TIP:** To speed up invocation for subsequent invocations, `starts_by_day.csv` from a previous run can be passed in lieu of `./access_logs_dir` and
         the script will use start statistics from that file to generate reports
         and plots.  

The above command will parse the file passed and generate files under
`./cytoscape_starts_report` directory.

### Step 3 Review results
 
 A `csv`, `txt`, and several `svg` files will be written to the output directory specified on the command
 line (`./cytoscape_starts_report` if above command was invoked)
 
 * `summary.txt`
 
   Text file denoting total [Cytoscape](https://cytoscape.org) starts and
   date range of source data.

 * `starts_by_day.csv`
 
   CSV file denoting [Cytoscape](https://cytoscape.org) starts per day.
   For subsequent runs of `./cytoscape_start_stats.py` this can be used instead
   of `./acces_log_dir` for quicker generation of figures.
   
 * `starts_per_day.svg`

   Plot that shows [Cytoscape](https://cytoscape.org) starts per day. This plot is the one displayed
   on under **Cytoscape** section of [Cytoscape Project Statistics page](https://cytoscape.org/stat.html)
     
 * `starts_per_year.svg` 
   
    Plot that shows bar chart of [Cytoscape](https://cytoscape.org) starts per year. 
