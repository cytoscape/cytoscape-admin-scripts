#!/usr/bin/env python

import os
import sys
import argparse
import logging
import functools
from datetime import date
import json
import numpy as np

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


def _parse_arguments(desc, args):
    """
    Parses command line arguments

    :param desc:
    :param args:
    :return:
    """
    parser = argparse.ArgumentParser(description=desc,
                                     formatter_class=Formatter)
    parser.add_argument('outdir', help='Directory to save figures to,'
                                       'if not existing, will be created')
    parser.add_argument('--jsonfile',
                        help='Path to JSON file containing download ' +
                             'statistics from github. If set, direct query ' +
                        'is skipped')
    parser.add_argument('--matplotlibgui', default='svg',
                        help='Library to use for plotting')
    parser.add_argument('--plot_totaldownloads', action='store_true',
                        help='If set, generates downloads.svg containing '
                             'total downloads by version')
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

def convert_version_to_numeric_tuple(version):
    """

    :param version:
    :return:
    """
    split_val = version.split('.')
    if len(split_val) != 3:
        return None
    return int(split_val[0]), int(split_val[1]), int(split_val[2])

def compare_versions(item1, item2):
    """
    Compares versions of Cytoscape
    :param item1:
    :param item2:
    :return:
    """
    item1_tup = convert_version_to_numeric_tuple(item1)
    item2_tup = convert_version_to_numeric_tuple(item2)
    if item1 is None:
        if item2 is None:
            return 0
        return -1
    if item2 is None:
        return 1
    if item1_tup[0] < item2_tup[0]:
        return -1
    if item1_tup[0] > item2_tup[0]:
        return 1
    if item1_tup[1] < item2_tup[1]:
        return -1
    if item1_tup[1] > item2_tup[1]:
        return 1
    if item1_tup[2] < item2_tup[2]:
        return -1
    if item1_tup[2] > item2_tup[2]:
        return 1
    return 0


def load_json_file(jsonfile=None):
    """

    :param jsonfile:
    :return:
    """
    with open(jsonfile, 'r') as f:
        return json.load(f)


def extract_releases(data=None):
    """

    :param data:
    :return:
    """
    release_dict = {}
    for entry in data:
        key = entry['tag_name']
        if key == '3.6.1':
            continue
        release_dict[key] = {'tag_name': entry['tag_name'],
                             'name': entry['name']}
        release_dict[key]['files'] = []
        for asset in entry['assets']:
            if 'cytoscape' not in asset['name'].lower():
                continue
            created_at_str = asset['created_at'][0:asset['created_at'].index('T')]
            create_date = date.fromisoformat(created_at_str)
            release_dict[key]['files'].append({'name': asset['name'],
                                               'download_count': asset['download_count'],
                                               'created_at': create_date})
    return release_dict


def tabulate_downloads(release_dict=None):
    """

    :param release_dict:
    :return:
    """
    for version in release_dict:
        windows32 = 0
        windows = 0
        linux = 0
        mac = 0
        created_at = None
        for afile in release_dict[version]['files']:
            filename = afile['name']
            if filename.endswith('.exe') and '32bit' in filename:
                windows32 += afile['download_count']
            elif filename.endswith('.exe') or filename.endswith('.zip'):
                windows += afile['download_count']
            elif filename.endswith('.sh') or filename.endswith('.gz') or 'unix' in filename:
                linux += afile['download_count']
            elif filename.endswith('.dmg'):
                mac += afile['download_count']
            else:
                print('file does not match: ' + filename)
            if created_at is None:
                created_at = afile['created_at']
            elif afile['created_at'] < created_at:
                created_at = afile['created_at']

        release_dict[version]['mac_downloads'] = mac
        release_dict[version]['windows_downloads'] = windows
        release_dict[version]['windows32_downloads'] = windows32
        release_dict[version]['linux_downloads'] = linux
        release_dict[version]['total_downloads'] = windows + windows32 + linux + mac
        release_dict[version]['created_at'] = created_at
    return release_dict


def add_days_as_primary_release(release_dict=None, version_list=None):
    """

    :param release_dict:
    :param version_list:
    :return:
    """
    next_release_date = date.today()
    for version in version_list:
        date_diff = next_release_date - release_dict[version]['created_at']
        release_dict[version]['days_as_latest_release'] = date_diff.days
        next_release_date = release_dict[version]['created_at']


def plot_downloads(release_dict=None, version_list=None, total_downloads=None,
                   outdir=None):
    """

    :param release_dict:
    :param version_list:
    :param total_downloads:
    :param total_days:
    :return:
    """
    downloads = []
    for version in version_list:
        downloads.append(release_dict[version]['total_downloads'])

    x_pos = np.arange(len(version_list))
    fig, ax = plt.subplots()

    ax.bar(x_pos, downloads, align='center')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(version_list)
    # ax.yaxis.grid()
    ax.set_xlabel('Cytoscape Version', fontweight='bold')
    ax.set_ylabel('# Downloads', fontweight='bold')
    ax.invert_xaxis()  # labels read top-to-bottom

    ax.set_title('Total Downloads by Version (' +
                 '{:,}'.format(total_downloads) + ')',
                 fontweight='bold')
    fig.patches.extend([plt.Rectangle((0, 0), 1, 1,
                                      fill=False, color='black', alpha=1, zorder=1000,
                                      transform=fig.transFigure, figure=fig, linewidth=2.0)])
    fig.set_tight_layout(True)
    plt.savefig(outdir + '/downloads.svg')
    plt.close()


def plot_downloads_by_day(release_dict=None, version_list=None, total_downloads=None,
                          outdir=None):
    """

    :param release_dict:
    :param version_list:
    :param total_downloads:
    :return:
    """
    downloads = []
    for version in version_list:
        downloads.append(release_dict[version]['total_downloads']/release_dict[version]['days_as_latest_release'])

    x_pos = np.arange(len(version_list))
    fig, ax = plt.subplots()

    ax.bar(x_pos, downloads, align='center')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(version_list)
    # ax.yaxis.grid()
    ax.set_xlabel('Cytoscape Version', fontweight='bold')
    ax.set_ylabel('# Downloads per day', fontweight='bold')
    ax.invert_xaxis()  # labels read top-to-bottom

    ax.set_title('Downloads per day (' +
                 '{:,}'.format(total_downloads) + ' downloads)',
                 fontweight='bold')
    fig.patches.extend([plt.Rectangle((0, 0), 1, 1,
                                      fill=False, color='black', alpha=1, zorder=1000,
                                      transform=fig.transFigure, figure=fig, linewidth=2.0)])
    fig.set_tight_layout(True)
    plt.savefig(outdir + '/downloads_byday.svg')
    plt.close()


def plot_downloads_by_platform(release_dict=None, version_list=None,
                               outdir=None):
    """

    :param release_dict:
    :param version_list:
    :return:
    """
    mac = []
    linux = []
    windows = []
    windows32 = []
    lin_mac = []
    lin_mac_win = []
    for version in version_list:
        mac.append(release_dict[version]['mac_downloads']/release_dict[version]['total_downloads'])
        windows.append(release_dict[version]['windows_downloads']/release_dict[version]['total_downloads'])
        windows32.append(release_dict[version]['windows32_downloads']/release_dict[version]['total_downloads'])
        linux.append(release_dict[version]['linux_downloads']/release_dict[version]['total_downloads'])
        lin_mac.append(linux[-1]+mac[-1])
        lin_mac_win.append(linux[-1]+mac[-1]+windows[-1])

    x_pos = np.arange(len(version_list))
    fig, ax = plt.subplots()

    ax.bar(x_pos, mac, label='Linux', bottom=0)
    ax.bar(x_pos, linux, bottom=mac, label='Mac')
    ax.bar(x_pos, windows, bottom=lin_mac, label='Windows')
    ax.bar(x_pos, windows32, bottom=lin_mac_win, label='Windows 32 bit')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(version_list)
    ax.set_ylabel('Percentage', fontweight='bold')
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0))
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc='lower left',
               ncol=4, mode="expand", borderaxespad=0.)
    # ax.legend(loc=0)
    ax.set_xlabel('Cytoscape Version', fontweight='bold')
    ax.set_title('Downloads by Platform',
                 fontweight='bold', y=1.2, pad=-14)
    ax.invert_xaxis()
    fig.patches.extend([plt.Rectangle((0, 0), 1, 1,
                                      fill=False, color='black', alpha=1, zorder=1000,
                                      transform=fig.transFigure, figure=fig, linewidth=2.0)])
    fig.set_tight_layout(True)
    plt.savefig(outdir + '/downloads_by_platform.svg')
    plt.close()


def main(args):
    """

    :param args:
    :return:
    """
    desc = """
    
          
    """
    theargs = _parse_arguments(desc, args[1:])

    if not os.path.isdir(theargs.outdir):
        os.makedirs(theargs.outdir, mode=0o755)
    # setup logging
    _setup_logging(theargs)

    matplotlib.use(theargs.matplotlibgui)

    if theargs.jsonfile is not None:
        data = load_json_file(jsonfile=theargs.jsonfile)

    release_dict = extract_releases(data=data)
    final_dict = tabulate_downloads(release_dict=release_dict)
    version_list = sorted(final_dict.keys(), key=functools.cmp_to_key(compare_versions), reverse=True)
    add_days_as_primary_release(release_dict=final_dict, version_list=version_list)
    grand_total = 0
    for version in version_list:
        total_dl = float(final_dict[version]['total_downloads'])
        rel_days = float(final_dict[version]['days_as_latest_release'])
        print(version + ' [' + str(final_dict[version]['created_at']) +
              ' ' + str(final_dict[version]['days_as_latest_release']) + '] total => ' +
              str(final_dict[version]['total_downloads']) + ' {' +
              str(round(total_dl / rel_days)*30) + ' per month}' +
              ' (windows=' + str(final_dict[version]['windows_downloads']) +
              ', windows32=' + str(final_dict[version]['windows32_downloads']) +
              ', mac=' + str(final_dict[version]['mac_downloads']) +
              ', linux=' + str(final_dict[version]['linux_downloads']) + ')')
        grand_total += final_dict[version]['total_downloads']

    num_rel_days = date.today() - final_dict[version_list[-1]]['created_at']
    print('Total downloads since ' + version_list[-1] + ': ' + str(grand_total) + ', ' +
          str(round(float(grand_total)/float(num_rel_days.days)*30)) + ' downloads per month')

    if theargs.plot_totaldownloads is True:
        plot_downloads(release_dict=final_dict, version_list=version_list,
                       total_downloads=grand_total,
                       outdir=theargs.outdir)
    plot_downloads_by_day(release_dict=final_dict, version_list=version_list,
                          total_downloads=grand_total,
                          outdir=theargs.outdir)
    plot_downloads_by_platform(release_dict=final_dict,
                               version_list=version_list,
                               outdir=theargs.outdir)


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main(sys.argv))
