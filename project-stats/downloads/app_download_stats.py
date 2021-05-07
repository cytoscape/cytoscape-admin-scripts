#!/usr/bin/env python

import os
import sys
import argparse
import logging
from datetime import datetime

import json

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
    parser.add_argument('jsonfile',
                        help='Path to JSON file from http://apps.cytosc'
                             'ape.org/download/stats/timeline')
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


def load_json_file(jsonfile=None):
    """
    Loads json file

    :param jsonfile:
    :return: contents of json file
    :rtype: dict
    """
    with open(jsonfile, 'r') as f:
        return json.load(f)


def extract_downloads_by_day(data=None):
    """
    Iterates json data to
    The data is returned in a dict with this format:

    .. code-block::

        {"Total": [
                   ["DATE", <# downloads>]
                  ]
        }


    :param data: Data loaded from github json
    :type data: dict
    :return: information about files available for download for each
             release as described above.
    :rtype: dict
    """
    download_dict = {}
    download_list = data['Total']
    for download in download_list:
        download_dict[download[0]] = download[1]
    return download_dict


def get_sorted_date_list(download_dict=None):
    """
    Get dates from **start_dict** in ascending order
    as list

    :param download_dict: dict of starts where key is date and value
                       is number of starts
    :type download_dict: dict
    :return: dates as str in ascending order in a list
    :rtype: list
    """
    date_list = list(download_dict.keys())
    date_list.sort(key=lambda xdate: datetime.strptime(xdate, '%Y-%m-%d'))
    return date_list


def plot_starts_by_day(download_dict=None, date_list=None,
                       outdir=None):
    """
    Plot starts by day saving the file named starts_by_day.svg to
    directory specified by **outdir**

    :param download_dict: starts for each day
    :type download_dict: dict
    :param date_list: Ordered start dates. Each entry is a str
    :type date_list: list
    :param outdir: Directory to save plot to
    :type outdir: str
    :return:
    """
    total_downloads = 0
    start_list = []
    for key in date_list:
        total_downloads += download_dict[key]

        start_list.append(download_dict[key])

    # setup labels to print year at 01/Jan position in date_list
    x_pos = []
    x_labels = []
    counter = 0
    for entry in date_list:
        if entry.endswith('01-01'):
            x_labels.append(entry[0:entry.index('-')])
            x_pos.append(counter)
        counter += 1

    fig, ax = plt.subplots()

    ax.plot(date_list, start_list)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(x_labels)
    ax.set_xlabel('Year', fontweight='bold')
    ax.set_ylabel('# Downloads', fontweight='bold')

    ax.set_title('Total App Downloads by Day (' +
                 '{:,}'.format(total_downloads) + ')',
                 fontweight='bold')

    fig.patches.extend([plt.Rectangle((0, 0), 1, 1,
                                      fill=False, color='black', alpha=1,
                                      zorder=1000,
                                      transform=fig.transFigure, figure=fig,
                                      linewidth=2.0)])
    fig.set_tight_layout(True)
    plt.savefig(outdir + '/app_downloads_per_day.svg')
    plt.close()
    with open(os.path.join(outdir, 'summary.txt'), 'w') as f:
        f.write('Total AppStore App Downloads: ' + '{:,}'.format(total_downloads) + ' (' +
                date_list[0] + ' - ' + date_list[-1] + ')\n')


def main(args):
    """

    :param args:
    :return:
    """
    desc = """
    Parses JSON file from:
    http://apps.cytoscape.org/download/stats/timeline
    
    to generate svg charts denoting downloads per day from AppStore

    """
    theargs = _parse_arguments(desc, args[1:])

    if not os.path.isdir(theargs.outdir):
        os.makedirs(theargs.outdir, mode=0o755)
    # setup logging
    _setup_logging(theargs)

    matplotlib.use(theargs.matplotlibgui)

    if theargs.jsonfile is not None:
        data = load_json_file(jsonfile=theargs.jsonfile)

    download_dict = extract_downloads_by_day(data=data)
    date_list = get_sorted_date_list(download_dict)

    plot_starts_by_day(download_dict=download_dict,
                       date_list=date_list,
                       outdir=theargs.outdir)


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main(sys.argv))
