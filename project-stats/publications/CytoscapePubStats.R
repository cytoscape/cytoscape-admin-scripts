# library(devtools)
# install_github("dami82/easyPubMed", force = TRUE, build_opts = NULL)
# library(easyPubMed)
install.packages("europepmc")
library(europepmc)
library(dplyr)
library(magrittr)
library(tidyr)

##Search for Cytoscape. Basic text search for "cytoscape" in any field.
##Run once to see how many records there are. Default returned is 100.
cytoscape_search <- europepmc::epmc_search(query='cytoscape')

##Update query with limit based on how many are available. Note this will be very slow.
cytoscape_search <- europepmc::epmc_search(query='cytoscape', limit=21247)

## Make subsets
stats <- cytoscape_search %>%
  select(c("pmid", "journalTitle", "citedByCount")) %>%
  drop_na()

### All returned papers sorted by # citations. This is for ALL returned papers. Not to be confused by # citations for specific Cytoscape papers (below).
citation_count_all <- stats %>%
  arrange(desc(citedByCount))

### Get citations for a specific paper, i.e. original Cytoscape paper (PMC403769)
cytoscape_citations <- europepmc::epmc_citations("PMC403769", data_src = "pmc", limit=50000)

### Journals sorted by paper counts
journal_count <- stats %>%
  group_by(journalTitle) %>%
  summarise(count = n()) %>%
  arrange(desc(count), journalTitle)

## Write to files
setwd("~/Dropbox (Gladstone)/Work/Cytoscape")
#write.csv(citation_count_all, file="CytoPubsCitationCountAll.csv", row.names = FALSE)
write.csv(journal_count, file="CytoPubsJournalCount.csv", row.names = FALSE)

