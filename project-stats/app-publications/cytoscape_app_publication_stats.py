#!/usr/bin/env python

import os
import sys
import argparse
import logging
import re
import pandas
import requests
import time
import json
import datetime
import csv
from tqdm import tqdm

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick


class Formatter(argparse.ArgumentDefaultsHelpFormatter,
                argparse.RawDescriptionHelpFormatter):
    pass


LOG_FORMAT = "%(asctime)-15s %(levelname)s %(relativeCreated)dms " \
             "%(filename)s::%(funcName)s():%(lineno)d %(message)s"

LOGGER = logging.getLogger(__name__)


LOGGER.info('Starting program')


MEDLINE_TO_LABEL = {'TA  - ': 'journal',
                    'GR  - ': 'grant',
                    'TI  - ': 'title',
                    'DP  - ': 'publishdate',
                    'PL  - ': 'origin',
                    'LID - ': 'doi'}
"""
Used to translate the cryptic medline
codes to something human readable
"""

LABEL_TO_MEDLINE = {}
"""
Inverse of MEDLINE_TO_LABEL dict
so it has human readable labels mapped
to medline tags
"""

for key in MEDLINE_TO_LABEL.keys():
    LABEL_TO_MEDLINE[MEDLINE_TO_LABEL[key]] = key


def _parse_arguments(desc, args):
    """
    Parses command line arguments

    :param desc:
    :param args:
    :return:
    """
    parser = argparse.ArgumentParser(description=desc,
                                     formatter_class=Formatter)
    parser.add_argument('queryfile',
                        help='File with result of query: '
                             'select name,citation,'
                             'downloads from apps_app '
                             'where citation is not null '
                             'and citation != \'\'; ')
    parser.add_argument('outdir',
                        help='Output directory')
    parser.add_argument('--matplotlibgui', default='svg',
                        help='Library to use for plotting')
    parser.add_argument('--email', required=True,
                        help='A valid email address to send to the ncbi web api,'
                             'as required in the documentation.')
    parser.add_argument('--logconf', default=None,
                        help='Path to python logging configuration file in '
                             'this format: '
                             'https://docs.python.org/3/library/'
                             'logging.config.html#logging-config-fileformat'
                             '. Setting this overrides -v parameter '
                             'which uses default logger.')
    parser.add_argument('--verbose', '-v', action='count', default=0,
                        help='Increases verbosity of logger to standard '
                             'error for log messages '
                             'in this module and in. Messages are output '
                             'at these python logging levels -v = ERROR, '
                             '-vv = WARNING, -vvv = INFO, '
                             '-vvvv = DEBUG, -vvvvv = NOTSET')

    return parser.parse_args(args)


def _setup_logging(args):
    """
    Sets up logging based on parsed command line arguments.
    If args.logconf is set use that configuration otherwise look
    at args.verbose and set logging for this module and the one
    in ndexutil specified by TSV2NICECXMODULE constant
    :param args: parsed command line arguments from argparse
    :raises AttributeError: If args is None or args.logconf is None
    :return: None
    """

    if args is None or args.logconf is None:
        level = (50 - (10 * args.verbose))
        logging.basicConfig(format=LOG_FORMAT,
                            level=level)
        LOGGER.setLevel(level)
        return

    # logconf was set use that file
    logging.config.fileConfig(args.logconf,
                              disable_existing_loggers=False)


def get_app_citations_from_file_as_dict(queryfile):
    """
    Using pandas reads `queryfile` as a tab delimited
    text file with the following format:

    name citation downloads
    X    ID       ##

    It is assumed X is the app name, ID is the pubmed id of the
    publication for that app found in the app store and ## is
    the number of downloads

    :param queryfile: tab delimited file containing apps and
                      id of its publication
    :type queryfile: str
    :return: dict where key is app name and value is tuple(<CITATION>,<DOWNLOADS>)
    :rtype: dict
    """
    df = pandas.read_csv(queryfile, delimiter='\t', header=0)
    citation_dict = dict()
    for index, row in df.iterrows():
        citation_dict[row['name']] = (row['citation'], row['downloads'])
    return citation_dict


def download_medline_for_publications(urlprefix=None, outfile=None, toolargs=None, the_ids=None,
                                      sleep_time=1,
                                      filewrite_mode='w'):
    """
    Downloads medline file for `the_ids` ids passed in.
    To keep NCBI service happy this method sleeps for `sleep_time`
    set to 1 second.

    :param urlprefix: Starting URL for service that is assumed to end with /
    :type urlprefix: str
    :param outfile: output file
    :type outfile: str
    :param toolargs: should contain &tool=<name of tool>&email=<your email>
                     which is passed along to service as requested by ncbi
    :type toolargs: str
    :param the_ids: one id or if multiple comma delimited ids up to 200
    :type the_ids: str
    :param sleep_time: time in seconds to sleep before downloading, ncbi
                       will block if requests are 3 or more per second.
    :type sleep_time: int

    :param filewrite_mode: 'w' to write a new file or 'a' to append
    :type filewrite_mode: str
    :return: True upon success otherwise False
    :rtype: bool
    """

    # get medline file for Cytoscape App publication
    time.sleep(sleep_time)
    query_url = urlprefix + 'efetch.fcgi?db=pubmed&id=' + str(the_ids) + '&rettype=medline' + toolargs
    LOGGER.debug('Running query to download medline for id(s): ' + str(the_ids))
    res = requests.get(query_url)
    if res.status_code is not 200:
        LOGGER.error('Received code ' + str(res.status_code) + ' from query: ' + query_url)
        return False
    if res.text is not None:
        if res.text.startswith('id: '):
            LOGGER.error('There might be something wrong with this entry: ' + str(res.text))
            return False
    with open(outfile, filewrite_mode) as f:
        f.write(res.text)
        res.close()
    return True


def download_citing_publications(urlprefix=None, outfile=None, toolargs=None, the_ids=None,
                                 sleep_time=1):
    """
    Using NCBI service this method gets a json document of citation ids
    and stores it in `outfile` passed in if the `outfile` does NOT already
    exist. To keep NCBI service happy this method sleeps for `sleep_time`
    set to 1 second.

    :param urlprefix: Starting URL for service that is assumed to end with /
    :type urlprefix: str
    :param outfile: output file
    :type outfile: str
    :param toolargs: should contain &tool=<name of tool>&email=<your email>
                     which is passed along to service as requested by ncbi
    :type toolargs: str
    :param the_ids: one id or if multiple comma delimited ids up to 200
    :type the_ids: str
    :param sleep_time: time in seconds to sleep before downloading, ncbi
                       will block if requests are 3 or more per second.
    :type sleep_time: int
    :return: True upon success otherwise False
    :rtype: bool
    """
    if not os.path.isfile(outfile):
        time.sleep(sleep_time)
        query_url = urlprefix + 'elink.fcgi?dbfrom=pubmed&retmode=json&linkname=pubmed_pubmed_citedin&id=' +\
                    str(the_ids) + toolargs
        LOGGER.debug('Running query to get citing publications for id(s): ' + str(the_ids))
        res = requests.get(query_url)
        if res.status_code is not 200:
            LOGGER.error('Received code ' + str(res.status_code) + ' from query: ' + query_url)
            return False
        with open(outfile, 'w') as f:

            f.write(res.text)
            res.close()
    return True


def get_ids_of_citing_publications(cited_json=None):
    """
    Parses the JSON from ncbi output to get
    the list of citation ids

    :param cited_json: Output from ncbi elink.fcgi web call
    :return: citation ids
    :rtype: list
    """
    with open(cited_json, 'r') as f:
        data = json.load(f)
    if 'linksets' not in data:
        return []

    if len(data['linksets']) is 0:
        return []

    if 'linksetdbs' not in data['linksets'][0]:
        return []
    if len(data['linksets'][0]['linksetdbs']) is 0:
        return []
    return data['linksets'][0]['linksetdbs'][0]['links']


def write_app_report_csv(outfile=None, citation_dict=None, cited_pubs=None):
    """
    Writes out a CSV file with information about the Cytoscape App's publication

    :param outfile: output CSV file
    :param citation_dict: dict where key is app name
                          and value is a tuple of
                          (<citation id>,<number downloads>)
    :type citation_dict: dict
    :param cited_pubs: dict where key is app name
                       and value is a list of citation ids
    :type cited_pubs: dict
    :return: None
    """
    with open(outfile, 'w') as f:
        fieldnames = ['App',
                      'NumberDownloads',
                      'CitationId',
                      'NumberCitations',
                      'Origin', 'Journal',
                      'PublishDate']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for key in citation_dict.keys():
            row = {'App': key,
                   'NumberDownloads': citation_dict[key][1],
                   'CitationId': citation_dict[key][0],
                   'NumberCitations': len(cited_pubs[key]),
                   'Origin': ' '.join(citation_dict[key][2]['origin']),
                   'Journal': ' '.join(citation_dict[key][2]['journal']),
                   'PublishDate': ' '.join(citation_dict[key][2]['publishdate'])}
            writer.writerow(row)
    return None


def get_article_info_from_medline(medlinefile=None,
                                  mapping_dict=MEDLINE_TO_LABEL):
    """
    Given a medline file with single or multiple entries gets a
    dict with key set to keys in LABELS_TO_MEDLINE and values
    set to a list of elements found with under those fields
    as set by the mapping MEDLINE_TO_LABEL

    :param medlinefile:
    :return:
    """
    article_dict = dict()
    with open(medlinefile, 'r') as f:
        for line in f:
            for key in mapping_dict.keys():
                if line.startswith(key):
                    if mapping_dict[key] not in article_dict:
                        article_dict[mapping_dict[key]] = []
                    article_dict[mapping_dict[key]].append(line[len(key):].rstrip())

    return article_dict


def get_field_from_batch_medline(medlinefile=None, fieldprefix=None):
    """
    Given a `medlinefile` with multiple medlines in it. This function
    gets a list of values for all fields that start with prefix `fieldprefix`

    :param medlinefile: file containing medline data
    :param fieldprefix: a prefix to look for in file ie 'AU  -'
    :return: values from all lines that start with `fieldprefix`
    :rtype: list
    """
    result = []
    fieldprefix_len = len(fieldprefix)
    with open(medlinefile, 'r') as f:
        for line in f:
            if line.startswith(fieldprefix):
                result.append(line[fieldprefix_len:].rstrip())

    return result


def grant_value_cleanup_func(val):
    """
    Takes grant string and cleans it up
    with basically a big case statement below

    :param val:
    :return:
    """
    if val is None or '':
        return val

    if '/NIH HHS/United States' in val:
        return val
    if ' NIH HHS/United States' in val:
        return re.sub('^.*\/','',
                      re.sub(' NIH HHS\/United States', '', val))
    if 'Wellcome Trust' in val:
        return 'Wellcome Trust'
    if 'Medical Research Council' in val:
        return 'Medical Research Council'
    if 'European Regional Development' in val:
        return 'European Regional Development'
    if 'European Research Council' in val:
        return 'European Research Council'
    if '/Cancer Research UK/' in val:
        return 'Cancer Research UK'
    if '/Worldwide Cancer Research/United Kingdom' in val:
        return 'Worldwide Cancer Research UK'
    if 'British Heart Foundation/' in val:
        return 'British Heart Foundation'
    if 'Howard Hughes Medical Institute' in val:
        return 'Howard Hughes Medical Institute'
    if 'CIHR/Canada' in val or\
            'Canadian Institutes of Health Research' in val:
        return 'CIHR Canada'
    if 'Deutsche Forschungsgemeinschaft' in val:
        return 'Deutsche Forschungsgemeinschaft'
    if 'Natural Science Foundation of China' in val or\
            'National Natural Scientific Foundation of China' in val or\
            'National Nature Science Foundation of China' in val or\
            'National Science Foundation of China' in val:
        return 'National Natural Science Foundation of China'
    if 'National Institute of Allergy and Infectious Diseases' in val:
        return 'NIAID'
    if 'Gordon and Betty Moore Foundation' in val:
        return 'Gordon and Betty Moore Foundation'
    return val


def write_count_summary(outfile=None, medlinefile=None,
                        fieldprefix=None, fieldlabel=None,
                        value_cleanup_func=None):
    """
    Writes out a CSV file with two columns Country of origin and number of publications
    with that country of origin

    :param outfile:
    :param outdir:
    :param batch_medlinefiles:
    :return:
    """
    origin_dict = dict()

    the_list = get_field_from_batch_medline(medlinefile=medlinefile,
                                            fieldprefix=fieldprefix)
    for entry in the_list:
        if value_cleanup_func is not None:
            updatedentry = value_cleanup_func(entry)
        else:
            updatedentry = entry
        if updatedentry not in origin_dict:
            origin_dict[updatedentry] = 0
        origin_dict[updatedentry] += 1

    with open(outfile, 'w') as f:
        fieldnames = [fieldlabel, 'Count']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for entry in origin_dict.keys():
            row = {fieldlabel: entry,
                   'Count': origin_dict[entry]}
            writer.writerow(row)


def merge_medline_files(outfile=None, batch_medlinefiles=None):
    """
    Merges all the medline files into a single file checking for duplicates
    by looking at PMID- line

    :param outfile:
    :param batch_medlinefiles:
    :return:
    """
    pmid_set = set()
    with open(outfile, 'w') as out_stream:
        for medlinefile in tqdm(batch_medlinefiles):
            skip_medline = False
            with open(medlinefile, 'r') as input_stream:
                for line in input_stream:
                    if line.startswith('PMID-'):
                        pmid = line[len('PMID-'):].rstrip()
                        if pmid in pmid_set:
                            skip_medline = True
                        else:
                            pmid_set.add(pmid)
                            skip_medline = False
                    if skip_medline is False:
                        out_stream.write(line)


def plot_journal_summary(inputfile=None,
                         outfile=None, top_count=15):
    """
    Takes journal publication summary CSV file and
    generates pie chart

    :param inputfile: Path to cited_publications_journal.csv file
    :type inputfile: str
    :param outfile: Path to write piechart
    :type outfile: str
    :return:
    """
    df = pandas.read_csv(inputfile, delimiter=',', header=0)
    df.set_index('Journal', inplace=True)
    num_journals = len(df)
    total_citations = df['Count'].sum()
    df.sort_values(by=['Count'], ascending=False, inplace=True)
    top_df = df[:top_count]
    fig, ax = plt.subplots()
    top_total_citations = top_df['Count'].sum()
    # autopct='%1.0f%%'
    # autopct=lambda pct: top_total_citations*pct/total_citations
    # ax = top_df.plot(kind='pie', y='Count', ax=ax,
    #                 autopct=lambda pct: '{:.0f}%'.format(top_total_citations * pct / total_citations),
    #                 legend=False)

    ax = top_df.plot(kind='bar', y='Count', ax=ax,
                     legend=False)
    ax.yaxis.label.set_text('# Citations')
    ax.xaxis.label.set_text('Citation Venue')
    ax.set_title('Top ' + str(top_count) + ' of ' +
                 '{:,}'.format(num_journals) +
                 ' Cytoscape Citation Venues' +
                 '\n(' + '{:,}'.format(top_total_citations) + ' of ' +
                 '{:,}'.format(total_citations) + ' citations)',
                 fontweight='bold')
    fig.patches.extend([plt.Rectangle((0, 0), 1, 1,
                                      fill=False, color='black',
                                      alpha=1, zorder=1000,
                                      transform=fig.transFigure,
                                      figure=fig, linewidth=2.0)])
    fig.set_tight_layout(True)
    plt.savefig(outfile)
    plt.close()


def plot_grant_summary(inputfile=None,
                       outfile=None, top_count=15):
    """
    Takes cited publication grant summary CSV file and
    generates pie chart

    :param inputfile: Path to cited_publications_journal.csv file
    :type inputfile: str
    :param outfile: Path to write piechart
    :type outfile: str
    :return:
    """
    df = pandas.read_csv(inputfile, delimiter=',', header=0)
    df.set_index('Grant', inplace=True)
    num_agencies = len(df)
    df.sort_values(by=['Count'], ascending=False, inplace=True)
    top_df = df[:top_count]
    fig, ax = plt.subplots()

    ax = top_df.plot(kind='bar', y='Count', ax=ax,
                     legend=False)
    ax.yaxis.label.set_text('# Citations')
    ax.xaxis.label.set_text('Funding Agency')
    ax.set_title('Top ' + str(top_count) + ' of ' + '{:,}'.format(num_agencies) +
                 ' Funding Agencies for Cytoscape Citations',
                 fontweight='bold')
    fig.patches.extend([plt.Rectangle((0, 0), 1, 1,
                                      fill=False, color='black',
                                      alpha=1, zorder=1000,
                                      transform=fig.transFigure,
                                      figure=fig, linewidth=2.0)])
    fig.set_tight_layout(True)
    plt.savefig(outfile)
    plt.close()


def main(args):
    """

    :param args:
    :return:
    """
    desc = """
    Using pubmed web API, this tool generates 
    reports of publications that cite
    the publications listed in the tab delimited
    <queryfile> passed into this tool.
    
    Given a tab delimited file of format:
    
    name citation downloads
    X    ID       ##
    
    Where 'X' is the app name, 'ID' is 
    the pubmed id of publication for the app,
    and '##' is the number of downloads for the app
    
    The results of this tool end up in the output
    directory specified by <outdir> command line parameter
    
    Key output files under <outdir>:
    
    data/
        - For each app contains a
          medline file of the app publication,
          a json file containing the list of papers
          citing the app publication, and a medline
          file for all publications citing the
          app publication. This is kept for caching
          purposes.
          
    summary.txt 
        - Denotes number of citations referencing
          papers in <queryfile> and some other info
       
    app_summary_report.csv 
        - CSV file containing information
          about publications from <queryfile>
                             
    unique_set_of_cited_publication.medline 
        - A unique set of publications that site
          those listed in <queryfile> in medline
          format. Subsequent documentation 
          refers to this file as
          'unique medline file.'
          
    cited_publications_country_of_origin.csv
        - CSV containing counts of country
          of origin for publications citing
          papers in <queryfile>. This is 
          calculated using the 'unique medline file'
          
    cited_publications_grants.csv
        - CSV containing counts of grants
          for publications citing
          papers in <queryfile>. Logic has been
          added to merge grants down since
          each grant line in a paper can
          vary and contains grant ids etc. This is 
          calculated using the 'unique medline file'
          
    cited_publications_journal.csv
        - CSV containing counts of journals
          for publications citing
          papers in <queryfile>. This is 
          calculated using the 'unique medline file'
          
    """
    theargs = _parse_arguments(desc, args[1:])

    outdir = os.path.abspath(theargs.outdir)
    data_outdir = os.path.join(outdir, 'data')
    if not os.path.isdir(data_outdir):
        os.makedirs(data_outdir, mode=0o755)

    # setup logging
    _setup_logging(theargs)

    matplotlib.use(theargs.matplotlibgui)

    toolargs = '&tool=cytoscapeAppPubStats&email=' + theargs.email
    urlprefix = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
    citation_dict = get_app_citations_from_file_as_dict(theargs.queryfile)

    total_cite_count = 0
    unique_citations = set()
    cited_pubs = dict()
    batch_medlinefiles = []
    update_merged_medlines = False
    for key in tqdm(citation_dict.keys()):
        LOGGER.debug('Examining: ' + key)
        medlinefile = os.path.join(data_outdir, key + '.medline')
        if not os.path.isfile(medlinefile):
            download_medline_for_publications(urlprefix=urlprefix,
                                              outfile=medlinefile,
                                              toolargs=toolargs,
                                              the_ids=citation_dict[key][0])

        # get id of publications citing Cytoscape App publication
        cited_json = os.path.join(data_outdir, key + '.cited.json')
        download_citing_publications(urlprefix=urlprefix,
                                     outfile=cited_json,
                                     toolargs=toolargs,
                                     the_ids=citation_dict[key][0])

        # get count of publications citing Cytoscape App publication
        cited_pub_ids = get_ids_of_citing_publications(cited_json)
        cited_pubs[key] = cited_pub_ids
        total_cite_count += len(cited_pub_ids)
        unique_citations.update(cited_pub_ids)

        if len(cited_pub_ids) > 0:
            ofile = os.path.join(data_outdir, key +
                                 '.cited_papers.medline')
            batch_medlinefiles.append(ofile)
            if not os.path.isfile(ofile):
                # queries 200 and above need to be made with some search
                # history api, but the documentation is confusing
                # so I just added logic to perform the queries in batches
                batch_size = 199
                batched_pub_ids = [cited_pub_ids[i * batch_size:(i + 1) * batch_size]
                                   for i in range((len(cited_pub_ids) +
                                                   batch_size - 1) // batch_size)]
                first_entry = True
                write_mode = 'w'
                update_merged_medlines = True
                for entry in batched_pub_ids:
                    if first_entry is False:
                        write_mode = 'a'
                    download_medline_for_publications(urlprefix=urlprefix,
                                                      outfile=ofile,
                                                      toolargs=toolargs,
                                                      the_ids=','.join(entry),
                                                      filewrite_mode=write_mode)
                    first_entry = False

        # get information from medline about Cytoscape App publication
        article_dict = get_article_info_from_medline(medlinefile=medlinefile)

        # add article information to citation_dict tuple
        citation_dict[key] = (citation_dict[key][0], citation_dict[key][1],
                              article_dict)

    # write summary report of Cytoscape App publications
    write_app_report_csv(outfile=os.path.join(outdir, 'app_summary_report.csv'),
                         citation_dict=citation_dict, cited_pubs=cited_pubs)

    merged_medline_file = os.path.join(outdir, 'unique_set_of_cited_publication.medline')
    if not os.path.isfile(merged_medline_file) or update_merged_medlines is True:
        merge_medline_files(outfile=merged_medline_file, batch_medlinefiles=batch_medlinefiles)

    # write origin summary file
    write_count_summary(outfile=os.path.join(outdir,
                                             'cited_publications_country_of_origin.csv'),
                        medlinefile=merged_medline_file,
                        fieldprefix=LABEL_TO_MEDLINE['origin'],
                        fieldlabel='Country')


    # write grant summary file
    grant_summary = os.path.join(outdir,
                                 'cited_publications_grants.csv')
    write_count_summary(outfile=grant_summary,
                        medlinefile=merged_medline_file,
                        fieldprefix=LABEL_TO_MEDLINE['grant'],
                        fieldlabel='Grant',
                        value_cleanup_func=grant_value_cleanup_func)

    # write journal summary file
    journal_summary = os.path.join(outdir, 'cited_publications_journal.csv')
    write_count_summary(outfile=journal_summary,
                        medlinefile=merged_medline_file,
                        fieldprefix=LABEL_TO_MEDLINE['journal'],
                        fieldlabel='Journal',
                        value_cleanup_func=None)

    plot_journal_summary(inputfile=journal_summary,
                         outfile=os.path.join(outdir,
                                              'top_publications_journal.svg'))
    plot_grant_summary(inputfile=grant_summary,
                       outfile=os.path.join(outdir,
                                            'top_agencies_funding.svg'))

    # output some summary statistics
    with open(os.path.join(outdir, 'summary.txt'), 'w') as f:
        f.write('Time: ' +
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '\n')
        f.write('Number of Cytoscape App Publications: ' + str(len(citation_dict.keys())) + '\n')
        f.write('Total citations: ' + str(total_cite_count) + '\n')
        f.write('Total unique citations: ' + str(len(unique_citations)) + '\n')


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main(sys.argv))
