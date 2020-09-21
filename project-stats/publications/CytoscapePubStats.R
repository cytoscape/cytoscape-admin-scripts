# library(devtools)
# install_github("dami82/easyPubMed", force = TRUE, build_opts = NULL)
# library(easyPubMed)
library(europepmc)
library(dplyr)
library(magrittr)

##Search for Cytoscape
##Run once to see how many records there are. Default returned is 100.
cytoscape_search <- europepmc::epmc_search(query='cytoscape')

##Update query with limit based on how many are available. Note this will be very slow.
cytoscape_search <- europepmc::epmc_search(query='cytoscape', limit=21247)

##Make subset
columns <- c("pmid", "journalTitle", "citedByCount")
stats <- cytoscape_search[columns]

journal_count <- stats %>%
  group_by(journalTitle) %>%
  summarise(count = n()) %>%
  arrange(desc(count), journalTitle)

