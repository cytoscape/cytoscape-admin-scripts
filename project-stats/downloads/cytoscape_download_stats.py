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
    parser.add_argument('jsonfile',
                        help='Path to JSON file containing download ' +
                             'statistics from Github. The JSON file can be ' +
                             'obtained by this link: ' +
                             'https://api.github.com/repos/cytoscape/'
                             'cytoscape/releases')
    parser.add_argument('outdir', help='Directory to save figures to, '
                                       'directory will be created if '
                                       'it does not exist')
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
    Converts Cytoscape Version string into a tuple of numbers

    :param version: Version of cytoscape as string
    :type version: str
    :return: (major, minor, bugfix)
    :rtype: tuple
    """
    split_val = version.split('.')
    if len(split_val) != 3:
        return None
    return int(split_val[0]), int(split_val[1]), int(split_val[2])


def compare_versions(item1, item2):
    """
    Compares versions of Cytoscape which are passed
    in as str objects

    :param item1: Cytoscape Version
    :type item1: str
    :param item2: Cytoscape Version
    :type item2: str
    :return: -1, 0, 1 if item1 is less then, equal, or greater then item2
    :rtype: int
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
    Loads json file

    :param jsonfile:
    :return: contents of json file
    :rtype: dict
    """
    with open(jsonfile, 'r') as f:
        return json.load(f)


def extract_releases(data=None):
    """
    Iterates through github json data dict to get the name of each file
    under a version tag along with date of creation and download count.

    The data is returned in a dict with this format:

    .. code-block::

        {<version>: { 'tag_name': <value of tag_name>,
                      'name': <value of name>,
                      'files': [{'name': <file name>,
                                 'download_count': <download count>,
                                 'created_at': <create date as date object>}
                               ]
                    }
        }


    :param data: Data loaded from github json
    :type data: dict
    :return: information about files available for download for each
             release as described above.
    :rtype: dict
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
    Iterates through all the versions in `release_dict`
    and classifies the file as: mac, windows, windows32, or linux
    download files.

    Classification rules:

    windows32 - If file has .exe ending and 32bit in name
    windows - If file has .exe or .zip ending and NOT 32bit in name
    linux - If file has .gz or .sh ending
    mac - If file has .dmg ending

    The following information is added to each version:

    .. code-block::

        {<version>: 'mac_downloads': <number of mac downloads>,
                    'macarm_downloads': <number of mac arm downloads>,
                    'windows_downloads': <number of windows downloads>,
                    'windows32_downloads': <number of windows 32 downloads>,
                    'linux_downloads': <number of linux downloads>,
                    'total_downloads': <total number of downloads>,
                    'created_at': <earliest creation date for files as date object>
        }

    :param release_dict: result from :py:func:`extract_releases`
    :type release_dict: dict
    :return: same `release_dict` passed in, but with extra data added
             as described above
    :rtype: dict
    """
    for version in release_dict:
        windows32 = 0
        windows = 0
        linux = 0
        mac = 0
        mac_arm = 0
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
                if 'aarch64' in filename:
                    mac_arm += afile['download_count']
                else:
                    mac += afile['download_count']
            else:
                LOGGER.warning('File does not match and '
                               'will not be counted: ' + filename)
            if created_at is None:
                created_at = afile['created_at']
            elif afile['created_at'] < created_at:
                created_at = afile['created_at']

        release_dict[version]['mac_downloads'] = mac
        release_dict[version]['macarm_downloads'] = mac_arm
        release_dict[version]['windows_downloads'] = windows
        release_dict[version]['windows32_downloads'] = windows32
        release_dict[version]['linux_downloads'] = linux
        release_dict[version]['total_downloads'] = windows + windows32 + linux + mac + mac_arm
        release_dict[version]['created_at'] = created_at
    return release_dict


def add_days_as_primary_release(release_dict=None, version_list=None):
    """
    Iterates through the Cytoscape versions and calculates the days a given
    version was the latest release. This is done by subtracting the days
    of the released version from the release date of the next release.
    For the latest release, the current date is used.

    This information is added in place to `release_dict`
    under `version` dict:

    ``release_dict[version]['days_as_latest_release']``

    :param release_dict:
    :type release_dict: dict
    :param version_list: ordered list of Cytoscape versions
    :type version_list: list
    :return: `release_dict` with days as latest release information added.
    :rtype: dict
    """
    next_release_date = date.today()
    for version in version_list:
        date_diff = next_release_date - release_dict[version]['created_at']
        release_dict[version]['days_as_latest_release'] = date_diff.days
        next_release_date = release_dict[version]['created_at']


def plot_downloads(release_dict=None, version_list=None,
                   total_downloads=None,
                   outdir=None):
    """
    Plots total downloads by version

    :param release_dict: should be dict after going through
                         :py:func:`extract_releases`,
                         :py:func:`tabulate_downloads`,
                         and :py:func:`add_days_as_primary_release`
    :type release_dict: dict
    :param version_list: ordered list of Cytoscape Versions
    :type version_list: list
    :param total_downloads: Total downloads for all versions
    :type total_downloads: int
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
    ax.set_xlabel('Cytoscape Version', fontweight='bold')
    ax.set_ylabel('# Downloads', fontweight='bold')
    ax.invert_xaxis()  # labels read top-to-bottom

    ax.set_title('Total Downloads by Version (' +
                 '{:,}'.format(total_downloads) + ')',
                 fontweight='bold')
    fig.patches.extend([plt.Rectangle((0, 0), 1, 1,
                                      fill=False, color='black', alpha=1,
                                      zorder=1000,
                                      transform=fig.transFigure, figure=fig,
                                      linewidth=2.0)])
    fig.set_tight_layout(True)
    plt.savefig(outdir + '/downloads.svg')
    plt.close()


def plot_downloads_by_day(release_dict=None, version_list=None,
                          total_downloads=None,
                          outdir=None):
    """
    Plots total downloads by version divided by number of days version was
    latest release. This makes a more fair comparison.

    :param release_dict: should be dict after going through
                         :py:func:`extract_releases`,
                         :py:func:`tabulate_downloads`,
                         and :py:func:`add_days_as_primary_release`
    :param version_list: ordered list of Cytoscape Versions
    :type version_list: list
    :param total_downloads: Total downloads for all versions
    :type total_downloads: int
    :return:
    """
    downloads = []
    for version in version_list:
        downloads.append(release_dict[version]['total_downloads']/release_dict[version]['days_as_latest_release'])

    x_pos = np.arange(len(version_list))
    fig, ax = plt.subplots()

    ax.bar(x_pos, downloads, align='center')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(version_list, rotation=-45)
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
    Plots downloads by platform in a stacked bar chart

    :param release_dict: should be dict after going through
                         :py:func:`extract_releases`,
                         :py:func:`tabulate_downloads`,
                         and :py:func:`add_days_as_primary_release`
    :param version_list: ordered list of Cytoscape Versions
    :type version_list: list
    :return:
    """
    mac = []
    macarm = []
    linux = []
    windows = []
    windows32 = []
    lin_mac = []
    lin_mac_macarm = []
    lin_mac_win = []
    for version in version_list:
        macarm.append(release_dict[version]['macarm_downloads']/release_dict[version]['total_downloads'])
        mac.append(release_dict[version]['mac_downloads']/release_dict[version]['total_downloads'])
        windows.append(release_dict[version]['windows_downloads']/release_dict[version]['total_downloads'])
        windows32.append(release_dict[version]['windows32_downloads']/release_dict[version]['total_downloads'])
        linux.append(release_dict[version]['linux_downloads']/release_dict[version]['total_downloads'])
        lin_mac.append(linux[-1]+mac[-1])
        lin_mac_macarm.append(lin_mac[-1]+macarm[-1])
        lin_mac_win.append(lin_mac_macarm[-1] + windows[-1])

    x_pos = np.arange(len(version_list))
    fig, ax = plt.subplots()

    ax.bar(x_pos, mac, label='Linux', bottom=0)
    ax.bar(x_pos, linux, bottom=mac, label='Mac')
    ax.bar(x_pos, macarm, bottom=lin_mac, label='Mac ARM')
    ax.bar(x_pos, windows, bottom=lin_mac_macarm, label='Windows')
    ax.bar(x_pos, windows32, bottom=lin_mac_win, label='Windows 32 bit')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(version_list, rotation=-45)
    ax.set_ylabel('Percentage', fontweight='bold')
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0))
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc='lower left',
               ncol=5, mode="expand", borderaxespad=0.)
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
    Parses JSON file from:
    https://api.github.com/repos/cytoscape/cytoscape/releases
    
    to generate svg charts denoting downloads per day by version and
    breakdown of downloads by platform.

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
              ' (' + str(final_dict[version]['days_as_latest_release']) + ' days)] total => ' +
              str(final_dict[version]['total_downloads']) + ' {' +
              str(round(total_dl / rel_days)*30) + ' per month}' +
              ' (windows=' + str(final_dict[version]['windows_downloads']) +
              ', windows32=' + str(final_dict[version]['windows32_downloads']) +
              ', mac=' + str(final_dict[version]['mac_downloads']) +
              ', macarm=' + str(final_dict[version]['macarm_downloads']) +
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
