# library(devtools)
# install_github("dami82/easyPubMed", force = TRUE, build_opts = NULL)
# library(easyPubMed)
library(europepmc)
library(dplyr)
library(magrittr)
library(tidyr)

##Search for Cytoscape
##Run once to see how many records there are. Default returned is 100.
cytoscape_search <- europepmc::epmc_search(query='cytoscape')

##Update query with limit based on how many are available. Note this will be very slow.
cytoscape_search <- europepmc::epmc_search(query='cytoscape', limit=21247)

##Make subsets
stats <- cytoscape_search %>%
  select(c("pmid", "journalTitle", "citedByCount")) %>%
  drop_na()

### papers sorted by citations
citation_count <- stats %>%
  arrange(desc(citedByCount))

### journals sorted by paper counts
journal_count <- stats %>%
  group_by(journalTitle) %>%
  summarise(count = n()) %>%
  arrange(desc(count), journalTitle)

##Write to files
setwd("~/Dropbox (Gladstone)/Work/Cytoscape")
write.csv(citation_count, file="CytoPubsCitationCount.csv", row.names = FALSE)
write.csv(journal_count, file="CytoPubsJournalCount.csv", row.names = FALSE)

