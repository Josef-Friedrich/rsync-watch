#! /usr/bin/env python3

import argparse
import subprocess
import re
import socket
import os
import shlex
from rsync_watch.nsca import send_nsca

from rsync_watch._version import get_versions
__version__ = get_versions()['version']


class NscaInterface:
    """Class that should be overloaded by the Nsca() class. To provide a
    stable interface. The class Nsca() needs many configuration values which
    are not always available."""

    def send_nsca(self, *args):
        pass


nsca = NscaInterface()
"""Global instance of the Nsca() class."""


class RsyncWatchError(Exception):
    """Base exception for this script."""

    def __init__(self, msg):
        nsca.send(
            status=2,
            text_output='{}: {}'.format(
                self.__class__.__name__,
                msg,
            )
        )


class StatsNotFoundError(RsyncWatchError):
    """Raised when some stats regex couldn’t be found in stdout."""


def parse_args():
    """
    :return: A `ArgumentParse` object.
    :rtype: object
    """
    parser = argparse.ArgumentParser(
        description='A Python script to monitor the execution of a rsync task.'
    )

    parser.add_argument(
        '--host-name',
        help='The hostname to submit over NSCA to the monitoring.',
    )

    parser.add_argument(
        '--rsync-args',
        help='Rsync CLI arguments. Insert some rsync command line arguments.'
             'Wrap all arguments in one string, for example: '
             '--rsync-args \'--exclude \"this folder\"\'',
    )

    # checks

    checks = parser.add_argument_group(
        title='checks',
        description='Perform different checks before running the rsync task.'
    )

    checks.add_argument(
        '--action-check-failed',
        choices=('exception', 'skip'),
        default='skip',
        help='Select action what to do when a check failed.',
    )

    checks.add_argument(
        '--check-file',
        metavar='FILE_PATH',
        help='Check if a file exists on the local machine.'
    )

    checks.add_argument(
        '--check-ping',
        metavar='DESTINATION',
        help='Check if a remote host is reachable by pinging. DESTINATION can '
             'a IP address or a host name or a full qualified host name.'
    )

    checks.add_argument(
        '--check-ssh-login',
        metavar='SSH_LOGIN',
        help='Check if a remote host is reachable over the network by SSHing '
             'into it. SSH_LOGIN: “root@192.168.1.1” '
             'or “root@example.com” or “example.com”.'
    )

    # nsca

    nsca = parser.add_argument_group(
        title='nsca',
        description='Send status messages to the monitoring.'
    )

    nsca.add_argument(
        '--nsca-remote-host',
        help='IP address of the NSCA remote host.'
    )

    nsca.add_argument(
        '--nsca-password',
        help='The NSCA password.'
    )

    nsca.add_argument(
        '--nsca-encryption-method',
        help='The NSCA encryption method. The supported encryption methods '
             'are: 0 1 2 3 4 8 11 14 15 16'
    )

    parser.add_argument(
        '-v',
        '--version',
        action='version',
        version='%(prog)s {version}'.format(version=get_versions()['version'])
    )

    parser.add_argument(
        'src',
        help='The source ([[USER@]HOST:]SRC)'
    )

    parser.add_argument(
        'dest',
        help='The destination ([[USER@]HOST:]DEST)'
    )

    return parser


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
    # This line is sometimes missing on rsync --version 3.1.2
    # raise no error
    match = re.search(r'\nNumber of deleted files: ([\d,]*)', stdout)
    if match:
        result['num_deleted_files'] = comma_int_to_int(match[1])
    else:
        result['num_deleted_files'] = 0

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
    """
    :param dict stats: A dictionary containing the performance data.

    :return: A concatenated string
    :rtype: string
    """
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
    result = re.sub(r'[/@:\.~]', '-', result)
    result = re.sub(r'-*_-*', '_', result)
    result = re.sub(r'-{2,}', '-', result)
    result = re.sub(r'_{2,}', '_', result)
    result = re.sub(r'-$', '', result)
    result = re.sub(r'^-', '', result)
    return result


class Checks:
    """Collect multiple check results.

    :params boolean raise_exception: Raise exception it some checks have
      failed.
    """

    def __init__(self, raise_exception=True):
        self.raise_exception = raise_exception
        self._messages = []
        self.passed = True

    @property
    def messages(self):
        """
        :return: A concatenated string containing all messages of all failed
          checks.
        :rtype: string
        """
        return ' '.join(self._messages)

    def _log_fail(self, message):
        self._messages.append(message)
        self.passed = False

    def check_file(self, file_path):
        """Check if a file exists.

        :param string file_path: The file to check.
        """
        if not os.path.exists(file_path):
            self._log_fail(
                '--check-file: The file “{}” doesn’t exist.'.format(file_path)
            )

    def check_ping(self, dest):
        """Check if a remote host is reachable by pinging to it.

        :param string dest: A destination to ping to.
        """
        process = subprocess.run(['ping', '-c', '3', dest],
                                 stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)
        if process.returncode != 0:
            self._log_fail('--check-ping: “{}” is not reachable.'.format(dest))

    def check_ssh_login(self, ssh_host):
        """Check if the given host is online by retrieving its hostname.

        :param string ssh_host: A ssh host string in the form of:
          `user@hostname` or `hostname` or `alias` (as specified in
          `~/.ssh/config`)

        :return: True or False
        :rtype: boolean
        """
        process = subprocess.run(['ssh', ssh_host, 'ls'],
                                 stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)
        if not process.returncode == 0:
            self._log_fail(
                '--check-ssh-login: “{}” is not reachable.'.format(ssh_host)
            )

    def have_passed(self):
        """
        :return: True in fall checks have passed else false.
        :rtype: boolean"""
        if self.raise_exception and not self.passed:
            raise RsyncWatchError(self.messages)
        return self.passed


class Nsca:
    """Send NSCA messages to a monitoring server. Wrapper to setup to various
    informations for the monitoring process.
    """

    def __init__(self, host_name, service_name, remote_host, password=None,
                 encryption_method=None):
        self.host_name = host_name.encode()

        self.service_name = service_name.encode()

        self.remote_host = None
        if remote_host:
            self.remote_host = remote_host.encode()

        self.encryption_method = None
        if encryption_method:
            self.encryption_method = int(encryption_method)

        self.password = None
        if password:
            self.password = password.encode()

    def send(self, status, text_output):
        """Send a NSCA message to a monitoring server."""
        print('NSCA status: {}'.format(status))
        print('NSCA text output: {}'.format(text_output))
        if self.remote_host:
            send_nsca(
                status=int(status),
                host_name=self.host_name,
                service_name=self.service_name,
                text_output=text_output.encode(),
                remote_host=self.remote_host,
                password=self.password,
                encryption_method=self.encryption_method
            )


def main():
    """Main function. Gets called by `entry_points` `console_scripts`."""
    args = parse_args().parse_args()

    if not args.host_name:
        host_name = socket.gethostname()
    else:
        host_name = args.host_name

    service = service_name(host_name, args.src, args.dest)
    print('Service name: {}'.format(service))

    global nsca
    nsca = Nsca(host_name=host_name, service_name=service,
                remote_host=args.nsca_remote_host,
                password=args.nsca_password,
                encryption_method=args.nsca_encryption_method)

    raise_exception = False
    if args.action_check_failed == 'exception':
        raise_exception = True
    checks = Checks(raise_exception=raise_exception)
    if args.check_file:
        checks.check_file(args.check_file)
    if args.check_ping:
        checks.check_ping(args.check_ping)
    if args.check_ssh_login:
        checks.check_ssh_login(args.check_ssh_login)

    if checks.have_passed():
        rsync_command = ['rsync', '-av', '--delete', '--stats']
        if args.rsync_args:
            rsync_command += shlex.split(args.rsync_args)
        rsync_command += [args.src, args.dest]

        print('Source: {}'.format(args.src))
        print('Destination: {}'.format(args.dest))
        print('Rsync command: {}'.format(' '.join(rsync_command)))

        process = subprocess.run(rsync_command, encoding='utf-8',
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT)

        print('Rsync output:')
        print(process.stdout)
        if process.returncode != 0:
            msg = 'The rsync task fails with a non-zero exit code.'
            raise RsyncWatchError(msg)

        stats = parse_stats(process.stdout)
        text_output = 'RSYNC OK | {}'.format(
            format_performance_data(stats)
        )

        print('Monitoring output: {}'.format(text_output))

        nsca.send(status=0, text_output=text_output)
    else:
        print(checks.messages)


if __name__ == "__main__":
    main()
