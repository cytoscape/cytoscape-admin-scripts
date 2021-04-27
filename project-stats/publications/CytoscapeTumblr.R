library(devtools)
install_github("dami82/easyPubMed", force = TRUE, build_opts = NULL)
library(easyPubMed)

##This script simplifies the creation of Tumblr posts for publications with Cytoscape network figires.
##It also records information for outreach in a shared spreadsheet.

###Read in existing outreach spreadsheet
setwd("~/Dropbox (Gladstone)/NRNB Outreach")
posts <- read.csv("CytoTumblrPosts.csv", stringsAsFactors = F)

##Collect PubMed  data
temp_df <- data.frame()
pmid <- "32977829"  ##identified manually based on network figures

x <- easyPubMed::fetch_PMID_data(pmids = pmid)
record_df <- table_articles_byAuth(pubmed_data = x, included_authors = "all", max_chars = 0, autofill = TRUE, getKeywords = TRUE)

first_author = record_df$lastname[1]
journal = record_df$journal[1]
article_title = record_df$title[length(record_df$email)]
corr_author <- subset(record_df, email!="NA")
email <- corr_author$email
corr_author <- corr_author$lastname

if (length(email) == 0){
  email<- "NA"
}

if (length(corr_author) == 0){
  corr_author<- "NA"
}

if (length(email) > 1){
  email<- paste(unlist(email), collapse=", ")
}
if (length(corr_author) > 1){
  corr_author<- paste(unlist(corr_author), collapse=", ")
}

link = paste("doi:",record_df$doi[1])

## write to temp data frame
temp_df <- rbind(temp_df, data.frame(PMID = pmid, Title = article_title, Link = link, First.Author = first_author, Corresponding.Author = corr_author, Email = email, Outreach=""))

## combine to blurb for Tumblr
author_full = paste(first_author, " et al.", sep=",")
citation = paste(journal, link, sep=" ")
line2 = paste(author_full, citation, sep=", ")
final <- c(article_title, line2)
cat(final)

## Only do this once at the end for a set of PMIDs!!
## Write to outreach spreadsheet file
posts <- rbind(posts, temp_df)
write.csv(posts, file="CytoTumblrPosts.csv", row.names = FALSE)
write.csv(posts, file="../Work/github/cytoscape-admin-scripts/project-stats/publications/CytoTumblrPosts.csv", row.names = FALSE)

