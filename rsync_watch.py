#! /usr/bin/env python3

import argparse
import subprocess
import re


class RsyncWatchError(Exception):
    """Base exception for this script."""


class StatsNotFoundError(RsyncWatchError):
    """Raised when some stats regex couldn’t be found in stdout."""


def parse_args():
    parser = argparse.ArgumentParser(
        description='A Python script to monitor the execution of a rsync task.'
    )
    parser.add_argument(
        'src',
        help='The source ([[USER@]HOST:]SRC)'
    )
    parser.add_argument(
        'dest',
        help='The destination ([[USER@]HOST:]DEST)')

    return parser.parse_args()


def parse_stats(stdout):
    """Parse the standard output of the rsync process.

    :param string stdout: The standard output of the rsync process

    :return: A dictionary containing all the stats numbers.
    :rtype: dict
    """
    result = {}

    # num_files
    # num_dirs
    match = re.search(r'\nNumber of files: (\d*) \(dir: (\d*)\)\n', stdout)
    if match:
        result['num_files'] = int(match[1])
        result['num_dirs'] = int(match[2])
    else:
        raise StatsNotFoundError('Number of files: X (dir: X)')

    # num_created_files
    match = re.search(r'\nNumber of created files: (\d*)\n', stdout)
    if match:
        result['num_created_files'] = int(match[1])
    else:
        raise StatsNotFoundError('Number of created files: X')

    # num_deleted_files
    match = re.search(r'\nNumber of deleted files: (\d*)\n', stdout)
    if match:
        result['num_deleted_files'] = int(match[1])
    else:
        raise StatsNotFoundError('Number of deleted files: X')

    # num_files_transferred
    match = re.search(r'\nNumber of regular files transferred: (\d*)\n',
                      stdout)
    if match:
        result['num_files_transferred'] = int(match[1])
    else:
        raise StatsNotFoundError('Number of regular files transferred: X')

    # total_size
    match = re.search(r'\nTotal file size: (\d*) bytes\n', stdout)
    if match:
        result['total_size'] = int(match[1])
    else:
        raise StatsNotFoundError('Total file size: X bytes')

    # transferred_size
    match = re.search(r'\nTotal transferred file size: (\d*) bytes\n', stdout)
    if match:
        result['transferred_size'] = int(match[1])
    else:
        raise StatsNotFoundError('Total transferred file size: X bytes')

    # literal_data
    match = re.search(r'\nLiteral data: (\d*) bytes\n', stdout)
    if match:
        result['literal_data'] = int(match[1])
    else:
        raise StatsNotFoundError('Literal data: X bytes')

    # matched_data
    match = re.search(r'\nMatched data: (\d*) bytes\n', stdout)
    if match:
        result['matched_data'] = int(match[1])
    else:
        raise StatsNotFoundError('Matched data: X bytes')

    # list_size
    match = re.search(r'\nFile list size: (\d*)\n', stdout)
    if match:
        result['list_size'] = int(match[1])
    else:
        raise StatsNotFoundError('File list size: X')

    # list_generation_time
    match = re.search(r'\nFile list generation time: ([\d\.]*) seconds\n',
                      stdout)
    if match:
        result['list_generation_time'] = float(match[1])
    else:
        raise StatsNotFoundError('File list generation time: X.XXX seconds')

    # list_transfer_time
    match = re.search(r'\nFile list transfer time: ([\d\.]*) seconds\n',
                      stdout)
    if match:
        result['list_transfer_time'] = float(match[1])
    else:
        raise StatsNotFoundError('File list transfer time: X.XXX seconds')

    # bytes_sent
    match = re.search(r'\nTotal bytes sent: (\d*)\n', stdout)
    if match:
        result['bytes_sent'] = int(match[1])
    else:
        raise StatsNotFoundError('Total bytes sent: X')

    # bytes_received
    match = re.search(r'\nTotal bytes received: (\d*)\n', stdout)
    if match:
        result['bytes_received'] = int(match[1])
    else:
        raise StatsNotFoundError('Total bytes received: X')

    return result


def check_host(ssh_host, hostname=''):
    """Check if the given host is online by retrieving its hostname.

    :param string ssh_host: A ssh host string in the form of: `user@hostname`
      or `hostname` or `alias` (as specified in `~/.ssh/config`)

    :param string hostname: The hostname to check from the UNIX command
      `hostname`.

    :return: True or False
    :rtype: boolean
    """
    if not hostname:
        hostname = ssh_host
    process = subprocess.run(
        ['ssh', ssh_host, 'hostname'],
        encoding='utf-8',
        stderr=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
    )
    if process.returncode == 0 and process.stdout.strip() == hostname:
        return True
    return False


def main():
    args = parse_args()

    process = subprocess.run(
        ['rsync', '-av', '--stats', args.src, args.dest],
        encoding='utf-8',
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    print(process.stdout)


if __name__ == "__main__":
    main()
