#! /usr/bin/env python3

import argparse
import subprocess
import re
import socket
from send_nsca import send_nsca

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions


class RsyncWatchError(Exception):
    """Base exception for this script."""


class StatsNotFoundError(RsyncWatchError):
    """Raised when some stats regex couldn’t be found in stdout."""


def parse_args():
    parser = argparse.ArgumentParser(
        description='A Python script to monitor the execution of a rsync task.'
    )

    parser.add_argument(
        '--host-name',
        help='The hostname to submit over NSCA to the monitoring.',
    )

    parser.add_argument(
        '--check-hostname',
        help='Check if a remote host is reachable over the network by SSHing '
             'into it and retrieve its hostname.'
    )

    parser.add_argument(
        '--raise-exception',
        action='store_true',
        help='Raise an exception if one check doesn’t pass, else the rsync '
             'job gets skipped.',
    )

    parser.add_argument(
        '--check-file',
        help='Check if a file exists.'
    )

    parser.add_argument(
        '--check-mount',
        help='Check if a mount point exists.'
    )

    parser.add_argument(
        '--check-ping',
        help='Check if a remote host is reachable by pinging.'
    )

    parser.add_argument(
        '--nsca-remote-host',
        help='IP address of the NSCA remote host.'
    )

    parser.add_argument(
        'src',
        help='The source ([[USER@]HOST:]SRC)'
    )

    parser.add_argument(
        'dest',
        help='The destination ([[USER@]HOST:]DEST)'
    )

    return parser.parse_args()


def comma_int_to_int(comma_integer):
    """Convert a integer containing commas to a integer without commas.

    :param string comma_integer: a integer containing commas

    :return: A integer without commas
    :rtype: int
    """
    return int(comma_integer.replace(',', ''))


def parse_stats(stdout):
    """Parse the standard output of the rsync process.

    :param string stdout: The standard output of the rsync process

    :return: A dictionary containing all the stats numbers.
    :rtype: dict
    """
    result = {}

    # num_files
    match = re.search(r'\nNumber of files: ([\d,]*)', stdout)
    if match:
        result['num_files'] = comma_int_to_int(match[1])
    else:
        raise StatsNotFoundError(
            'Number of files: X,XXX (reg: X,XXX, dir: X,XXX)'
        )

    # num_created_files
    match = re.search(r'\nNumber of created files: ([\d,]*)', stdout)
    if match:
        result['num_created_files'] = comma_int_to_int(match[1])
    else:
        raise StatsNotFoundError(
            'Number of created files: X,XXX (reg: X,XXX, dir: X,XXX)'
        )

    # num_deleted_files
    match = re.search(r'\nNumber of deleted files: ([\d,]*)', stdout)
    if match:
        result['num_deleted_files'] = comma_int_to_int(match[1])
    else:
        raise StatsNotFoundError(
            'Number of deleted files: X,XXX (reg: X,XXX, dir: X,XXX)'
        )

    # num_files_transferred
    match = re.search(r'\nNumber of regular files transferred: ([\d,]*)\n',
                      stdout)
    if match:
        result['num_files_transferred'] = comma_int_to_int(match[1])
    else:
        raise StatsNotFoundError('Number of regular files transferred: X,XXX')

    # total_size
    match = re.search(r'\nTotal file size: ([\d,]*) bytes\n', stdout)
    if match:
        result['total_size'] = comma_int_to_int(match[1])
    else:
        raise StatsNotFoundError('Total file size: X,XXX bytes')

    # transferred_size
    match = re.search(r'\nTotal transferred file size: ([\d,]*) bytes\n',
                      stdout)
    if match:
        result['transferred_size'] = comma_int_to_int(match[1])
    else:
        raise StatsNotFoundError('Total transferred file size: X,XXX bytes')

    # literal_data
    match = re.search(r'\nLiteral data: ([\d,]*) bytes\n', stdout)
    if match:
        result['literal_data'] = comma_int_to_int(match[1])
    else:
        raise StatsNotFoundError('Literal data: X,XXX bytes')

    # matched_data
    match = re.search(r'\nMatched data: ([\d,]*) bytes\n', stdout)
    if match:
        result['matched_data'] = comma_int_to_int(match[1])
    else:
        raise StatsNotFoundError('Matched data: X,XXX bytes')

    # list_size
    match = re.search(r'\nFile list size: ([\d,]*)\n', stdout)
    if match:
        result['list_size'] = comma_int_to_int(match[1])
    else:
        raise StatsNotFoundError('File list size: X,XXX')

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
    match = re.search(r'\nTotal bytes sent: ([\d,]*)\n', stdout)
    if match:
        result['bytes_sent'] = comma_int_to_int(match[1])
    else:
        raise StatsNotFoundError('Total bytes sent: X,XXX')

    # bytes_received
    match = re.search(r'\nTotal bytes received: ([\d,]*)\n', stdout)
    if match:
        result['bytes_received'] = comma_int_to_int(match[1])
    else:
        raise StatsNotFoundError('Total bytes received: X,XXX')

    return result


def format_performance_data(stats):
    pairs = []
    for key, value in stats.items():
        pairs.append('{}={}'.format(key, value))

    return ' '.join(pairs)


def service_name(host_name, src, dest):
    """Format a service name to use as a Nagios or Icinga service name.

    :param string host_name: The hostname of the machine the rsync job running
      on.
    :param string src: A source string rsync understands
    :param string dest: A destination string rsync understands

    :return: The service name
    :rtype: string
    """
    result = 'rsync_{}_{}_{}'.format(host_name, src, dest)
    result = re.sub(r'[/@:\.]', '-', result)
    result = re.sub(r'-*_-*', '_', result)
    result = re.sub(r'-{2,}', '-', result)
    result = re.sub(r'_{2,}', '_', result)
    result = re.sub(r'-$', '', result)
    result = re.sub(r'^-', '', result)
    return result


class Checks:
    """Collect multiple check results."""

    def __init__(self, raise_exception=True):
        self.raise_exception = raise_exception
        self._messages = []
        self.passed = True

    @property
    def messages(self):
        return ' '.join(self._messages)

    def _log_fail(self, message):
        self._messages.append(message)
        self.passed = False

    def check_ping(self, dest):
        process = subprocess.run(['ping', '-c', 3, dest])
        if process.returncode != 0:
            self._log_fail('ping: “{}” is not reachable.'.format(dest))

    def check_hostname(self, ssh_host, hostname=''):
        """Check if the given host is online by retrieving its hostname.

        :param string ssh_host: A ssh host string in the form of:
          `user@hostname` or `hostname` or `alias` (as specified in
          `~/.ssh/config`)
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
        if not (process.returncode == 0 and
                process.stdout.strip() == hostname):
            self._log_fail('hostname: “{}” is not reachable.'.format(ssh_host))

    def has_passed(self):
        if self.raise_exception and not self.passed:
            raise RsyncWatchError(self.messages)
        return self.passed


def main():
    args = parse_args()

    checks = Checks(raise_exception=args.raise_exception)

    if args.check_ping:
        checks.check_ping(args.check_ping)

    if checks.has_passed():
        process = subprocess.run(
            ['rsync', '-av', '--stats', args.src, args.dest],
            encoding='utf-8',
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        print(process.stdout)
        if args.nsca_remote_host:
            if not args.host_name:
                host_name = socket.gethostname()
            else:
                host_name = args.host_name

            service = service_name(host_name, args.src, args.dest)
            stats = parse_stats(process.stdout)
            text_output = 'RSYNC OK | {}'.format(
                format_performance_data(stats)
            )

            send_nsca(
                status=0,
                host_name=host_name.encode(),
                service_name=service.encode(),
                text_output=text_output.encode(),
                remote_host=args.nsca_remote_host.encode()
            )
    else:
        print(checks.messages)


if __name__ == "__main__":
    main()
