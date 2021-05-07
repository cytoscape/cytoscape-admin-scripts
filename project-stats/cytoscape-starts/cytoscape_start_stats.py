#!/usr/bin/env python

import os
import sys
import argparse
import logging
import csv
from datetime import datetime
import numpy as np
from tqdm import tqdm


import matplotlib
import matplotlib.pyplot as plt


class Formatter(argparse.ArgumentDefaultsHelpFormatter,
                argparse.RawDescriptionHelpFormatter):
    pass


LOG_FORMAT = "%(asctime)-15s %(levelname)s %(relativeCreated)dms " \
             "%(filename)s::%(funcName)s():%(lineno)d %(message)s"

LOGGER = logging.getLogger(__name__)


LOGGER.info('Starting program')


def _parse_arguments(desc, args):
    """
    Parses command line arguments

    :param desc:
    :param args:
    :return:
    """
    parser = argparse.ArgumentParser(description=desc,
                                     formatter_class=Formatter)
    parser.add_argument('inputdir',
                        help='Path to directory containing access log files')
    parser.add_argument('outdir', help='Directory to save figures to, '
                                       'directory will be created if '
                                       'it does not exist')
    parser.add_argument('--matplotlibgui', default='svg',
                        help='Library to use for plotting')
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


def process_access_logs(accessdir=None, start_dict=None):
    """

    :param accessdir:
    :return:
    """
    bot_skipped = 0
    for entry in tqdm(os.listdir(accessdir)):
        if 'access' not in entry:
            continue
        full_path = os.path.join(accessdir, entry)
        if not os.path.isfile(full_path):
            continue
        bot_skipped += parse_access_log(accesslog=full_path, start_dict=start_dict)
    LOGGER.info('Skipped ' + str(bot_skipped) + ' bot lines')
    date_list = get_sorted_date_list(start_dict)
    return start_dict, date_list


def parse_access_log(accesslog=None, start_dict=None):
    """

    :param accesslog:
    :return:
    """
    bot_skipped = 0
    count = 0
    with open(accesslog, 'r') as f:
        for line in f:

            if line.find('"GET /cytoscape-news/news.html ') == -1:
                continue

            # skip the bots
            if 'bot' in line:
                LOGGER.debug('Skipping line cause bot found in text: ' + line)
                bot_skipped += 1
                continue

            # ip_end_index = line.index(' - - ')
            date_start_index = line.index('[')
            date_end_index = line.index(':')
            # first_slash = line.index('/')
            date_str = line[date_start_index+1:date_end_index]
            # ip_address = line[0:ip_end_index]

            # print(date_obj)
            if date_str not in start_dict:
                start_dict[date_str] = 0
            start_dict[date_str] += 1

            count += 1
    return bot_skipped


def load_starts_csv(inputcsv=None, start_dict=None):
    """

    :param inputcsv:
    :param start_dict:
    :return:
    """
    with open(inputcsv, 'r') as f:
        c_reader = csv.reader(f, delimiter=',', )
        for row in c_reader:
            if '/' not in row[0]:
                continue
            start_dict[row[0]] = int(row[1])
    date_list = get_sorted_date_list(start_dict)
    return start_dict, date_list


def plot_starts_by_day(start_dict=None, date_list=None,
                       outdir=None):
    """
    Plot starts by day saving the file named starts_by_day.svg to
    directory specified by **outdir**

    :param start_dict: starts for each day
    :type start_dict: dict
    :param date_list: Ordered start dates. Each entry is a str
    :type date_list: list
    :param outdir: Directory to save plot to
    :type outdir: str
    :return:
    """
    total_starts = 0
    start_list = []
    for key in date_list:
        total_starts += start_dict[key]
        start_list.append(start_dict[key])

    # setup labels to print year at 01/Jan position in date_list
    x_pos = []
    x_labels = []
    counter = 0
    for entry in date_list:
        if entry.startswith('01/Jan'):
            x_labels.append(entry[entry.rindex('/')+1:])
            x_pos.append(counter)
        counter += 1

    fig, ax = plt.subplots()

    ax.plot(date_list, start_list)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(x_labels)
    ax.set_xlabel('Year', fontweight='bold')
    ax.set_ylabel('# Starts', fontweight='bold')

    ax.set_title('Total Starts by Day (' +
                 '{:,}'.format(total_starts) + ')',
                 fontweight='bold')

    fig.patches.extend([plt.Rectangle((0, 0), 1, 1,
                                      fill=False, color='black', alpha=1,
                                      zorder=1000,
                                      transform=fig.transFigure, figure=fig,
                                      linewidth=2.0)])
    fig.set_tight_layout(True)
    plt.savefig(outdir + '/starts_per_day.svg')
    plt.close()
    with open(os.path.join(outdir, 'summary.txt'), 'w') as f:
        f.write('Total Starts: ' + '{:,}'.format(total_starts) + ' (' +
                date_list[0] + ' - ' + date_list[-1] + ')\n')


def get_sorted_date_list(start_dict=None):
    """
    Get dates from **start_dict** in ascending order
    as list

    :param start_dict: dict of starts where key is date and value
                       is number of starts
    :type start_dict: dict
    :return: dates as str in ascending order in a list
    :rtype: list
    """
    date_list = list(start_dict.keys())
    date_list.sort(key=lambda xdate: datetime.strptime(xdate, '%d/%b/%Y'))
    return date_list


def save_starts_per_day(start_dict=None,
                        date_list=None,
                        outdir=None):
    """
    Takes **start_dict** and saves a file named starts_by_day.csv
    to **outdir** directory.

    Example of output:

    .. code-block:: python

        Date,NumberOfStarts
        01/Jan/2014,234

    :param start_dict: dict of starts by day
    :type start_dict: dict
    :param outdir: Directory to save file
    :type outdir: str
    :return:
    """
    with open(os.path.join(outdir, 'starts_by_day.csv'), 'w') as f:
        f.write('Date,NumberOfStarts\n')
        for key in date_list:
            f.write(str(key) + ',' + str(start_dict[key]) + '\n')


def plot_starts_by_year(start_dict=None,
                        outdir=None,
                        plot_values=False):
    """
    Plot starts by year saving output to file starts_by_year.svg
    under **outdir** directory

    :param start_dict: dict of starts by day
    :type start_dict: dict
    :param outdir: Directory to save starts by year
    :type outdir: str
    :param plot_values: If ``True`` the values of each bar will be output
                        along with percent increase from previous year
    :type plot_values: bool
    :return:
    """
    total_starts = 0
    starts_per_year = {}
    for key in start_dict:
        year = key[key.rindex('/')+1:]
        if year not in starts_per_year:
            starts_per_year[year] = 0
        starts_per_year[year] += start_dict[key]
        total_starts += start_dict[key]

    year_list = list(starts_per_year.keys())
    year_list.sort()
    year_list = year_list[1:-1]
    x_pos = np.arange(len(year_list))
    fig, ax = plt.subplots()

    starts_list = []
    for y in year_list:
        starts_list.append(starts_per_year[y])

    ax.bar(x_pos, starts_list, align='center')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(year_list)
    ax.set_xlabel('Year', fontweight='bold')
    ax.set_ylabel('# Starts', fontweight='bold')

    ax.set_title('Total Starts by Year (' +
                 '{:,}'.format(total_starts) + ')',
                 fontweight='bold')

    if plot_values is True:
        for index, value in enumerate(starts_list):
            if index > 0 and index < len(starts_list):
                pc_increase = ' - ' +\
                              str(round((float(value -
                                               starts_list[index-1])/float(starts_list[index-1]))*100)) + '%'
            else:
                pc_increase = ''

            plt.text(index-0.5, value + 4, str(value) + str(pc_increase))
    fig.patches.extend([plt.Rectangle((0, 0), 1, 1,
                                      fill=False, color='black', alpha=1,
                                      zorder=1000,
                                      transform=fig.transFigure, figure=fig,
                                      linewidth=2.0)])
    fig.set_tight_layout(True)
    plt.savefig(outdir + '/starts_per_year.svg')
    plt.close()


def main(args):
    """

    :param args:
    :return:
    """
    desc = """
    Parses Apache access logs to generate
    various CSV files and plots on Cytoscape Starts

    """
    theargs = _parse_arguments(desc, args[1:])

    if not os.path.isdir(theargs.outdir):
        os.makedirs(theargs.outdir, mode=0o755)
    # setup logging
    _setup_logging(theargs)

    matplotlib.use(theargs.matplotlibgui)

    if os.path.isdir(theargs.inputdir):
        start_dict, date_list = process_access_logs(theargs.inputdir,
                                                    start_dict={})
        save_starts_per_day(start_dict, date_list=date_list,
                            outdir=theargs.outdir)
    else:
        start_dict, date_list = load_starts_csv(theargs.inputdir,
                                                start_dict={})
    plot_starts_by_year(start_dict,
                        outdir=theargs.outdir)
    plot_starts_by_day(start_dict, date_list=date_list,
                       outdir=theargs.outdir)


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main(sys.argv))
