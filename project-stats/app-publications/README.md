# Cytoscape App Publications

This directory contains a script to analyze Cytoscape App Publications
that are cited in the Cytoscape App Store: http://appstore.cytoscape.org

The main script, `cytoscape_app_publication_stats.py`, 
takes a tab delimited file containing Cytoscape App names along
with pubmed article ids and generates a set of report files
by querying ncbi web APIs.

If the `cytoscape_papers.txt` tab delimited file is used then the analysis is
done on the three main Cytoscape publications and the `.svg` files generated are
the ones put on the [Cytoscape Project Statistics Page](https://cytoscape.org/stat.html)

To generate a report follow the steps below. 

## Requirements

 * Python 3.6+
 * requests
 * pandas
 * tqdm
 * matplotlib

### Step 1 Get updated list of Cytoscape App publications

Create a \<query file\> by connecting to app store database
and running this query to generate a tab delimited output:

```Bash
select name,citation,downloads from apps_app where citation is not null and citation != '';
```

* `apps_with_citations.10.1.2020.txt` is an example of this file

* `cytoscape_papers.txt` contains three "fake" apps with the articles corresponding to the three main Cytoscape papers. 

**NOTE:** This tool can actually be used on the main three Cytoscape papers by 
          passing `cytoscape_papers.txt` as the input \<queryfile\> in the next
          step.

### Step 2 Generate Report

Open a terminal with required [Python](https://python.org) packages noted
in the requirements section and run the following command:

```Bash
./cytoscape_app_publication_stats.py apps_with_citations.10.1.2020.txt ./report --email <PUT YOUR EMAIL HERE> -vvv
```

**NOTE:** Replace `apps_with_citations.10.1.2020.txt` in above command with \<queryfile\>
          generated in Step 1.

The above command will download needed data from ncbi and generate the reports. The data
is stored under `./report` directory.


### Step 3 Review results

Here is a description of the results

 * `data/`
 
   * This directory is a cached store of medline and citation results from
     ncbi Web API requests. The cache speeds up invocation if script is re-run.

 * `summary.txt`

   * Denotes number of citations referencing papers in \<queryfile\> and some other info
   
 * `app_summary_report.csv` 
   
    * CSV file containing information about publications from input.

 * `unique_set_of_cited_publication.medline` 
   
    * A unique set of publications that cite the Cytoscape App Publications from \<queryfile\> in medline format. Subsequent documentation refers to this file as 'unique medline file.'

 * `cited_publications_country_of_origin.csv`

    * CSV containing counts of country of origin for publications citing papers in input. This is calculated using the 'unique medline file'

 * `cited_publications_grants.csv`

    * CSV containing counts of grants for publications citing papers in input. Logic has been added to merge grants down since each grant line in a paper can vary and contains grant ids etc. This is calculated using the 'unique medline file'

 * `cited_publications_journal.csv`

    * CSV containing counts of journals for publications citing papers in \<queryfile\>. This is calculated using the 'unique medline file'`
    
 * `cited_publications_per_year.csv`
 
    * CSV containing counts of publications published each year for publications citing papers in <queryfile>. This is calculated using the 'unique medline file'
    
 * `cited_publications_author.csv`
  
    * CSV containing counts of publications published by author. in \<queryfile\>. This is calculated using the 'unique medline file'`
          
 * `cited_publications_per_year.svg`

    * Bar chart show cited publications per year for publications that cited papers in \<query file\>. Derived from 'cited_publications_per_year.csv'
          
 * `top_cited_publications_journal.svg`
    
    * Bar chart figure using top 15 publication venues for publications that cited papers in \<queryfile\>. Derived from 'cited_publications_journal.csv' 
    
* `top_cited_publications_grants.svg`
        
    * Bar chart figure using top 15 grant funding agencies for publications that cited papers in \<query file\>. Derived from 'cited_publications_grants.csv'