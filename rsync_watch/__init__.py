#! /usr/bin/env python3

import argparse
import os
import re
import shlex
import socket
import subprocess

from jflib import command_watcher

from jflib import Watch, ConfigReader
from jflib.command_watcher import CommandWatcherError
from rsync_watch._version import get_versions

__version__ = get_versions()['version']


class StatsNotFoundError(CommandWatcherError):
    """Raised when some stats regex couldn’t be found in stdout."""


def get_argparser():
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

    def search(regex, exception_msg):
        match = re.search(regex, stdout)
        if match:
            return comma_int_to_int(match[1])
        else:
            raise StatsNotFoundError(exception_msg)

    result['num_files'] = search(
        r'\nNumber of files: ([\d,]*)',
        'Number of files: X,XXX (reg: X,XXX, dir: X,XXX)'
    )

    result['num_created_files'] = search(
        r'\nNumber of created files: ([\d,]*)',
        'Number of created files: X,XXX (reg: X,XXX, dir: X,XXX)',
    )

    # num_deleted_files
    # This line is sometimes missing on rsync --version 3.1.2
    # raise no error
    match = re.search(r'\nNumber of deleted files: ([\d,]*)', stdout)
    if match:
        result['num_deleted_files'] = comma_int_to_int(match[1])
    else:
        result['num_deleted_files'] = 0

    result['num_files_transferred'] = search(
        r'\nNumber of regular files transferred: ([\d,]*)\n',
        'Number of regular files transferred: X,XXX',
    )

    result['total_size'] = search(
        r'\nTotal file size: ([\d,]*) bytes\n',
        'Total file size: X,XXX bytes',
    )

    result['transferred_size'] = search(
        r'\nTotal transferred file size: ([\d,]*) bytes\n',
        'Total transferred file size: X,XXX bytes',
    )

    result['literal_data'] = search(
        r'\nLiteral data: ([\d,]*) bytes\n',
        'Literal data: X,XXX bytes',
    )

    result['matched_data'] = search(
        r'\nMatched data: ([\d,]*) bytes\n',
        'Matched data: X,XXX bytes',
    )

    result['list_size'] = search(
        r'\nFile list size: ([\d,]*)\n',
        'File list size: X,XXX'
    )

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

    result['bytes_sent'] = search(
        r'\nTotal bytes sent: ([\d,]*)\n',
        'Total bytes sent: X,XXX',
    )

    result['bytes_received'] = search(
        r'\nTotal bytes received: ([\d,]*)\n',
        'Total bytes received: X,XXX',
    )

    return result


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
        watch.log.warning(message)
        self.passed = False

    def check_file(self, file_path):
        """Check if a file exists.

        :param string file_path: The file to check.
        """
        if not os.path.exists(file_path):
            self._log_fail(
                '--check-file: The file \'{}\' doesn’t exist.'.format(
                    file_path
                )
            )
        else:
            watch.log.info(
                '--check-file: The file \'{}\' exists.'.format(file_path)
            )

    def check_ping(self, dest):
        """Check if a remote host is reachable by pinging to it.

        :param string dest: A destination to ping to.
        """
        process = subprocess.run(['ping', '-c', '3', dest],
                                 stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)
        if process.returncode != 0:
            self._log_fail(
                '--check-ping: \'{}\' is not reachable.'.format(dest)
            )
        else:
            watch.log.info('--check-ping: \'{}\' is reachable.'.format(dest))

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
                '--check-ssh-login: \'{}\' is not reachable.'.format(ssh_host)
            )
        else:
            watch.log.info(
                '--check-ssh-login: \'{}\' is not reachable.'.format(ssh_host)
            )

    def have_passed(self):
        """
        :return: True in fall checks have passed else false.
        :rtype: boolean"""
        if self.raise_exception and not self.passed:
            raise CommandWatcherError(self.messages)
        return self.passed


def main():
    """Main function. Gets called by `entry_points` `console_scripts`."""
    # To generate the argparser we use a not fully configured ConfigReader
    # We need args for the configs
    # We get the service name for args
    # A typical chicken-egg-situation.
    config_reader = ConfigReader(spec=command_watcher.CONFIG_READER_SPEC)
    parser = get_argparser()
    config_reader.spec_to_argparse(parser)
    args = parser.parse_args()
    del config_reader

    if not args.host_name:
        host_name = socket.gethostname()
    else:
        host_name = args.host_name

    service = service_name(host_name, args.src, args.dest)

    ini_file = os.path.join('/', 'etc', 'command-watcher.ini')
    if os.path.exists(ini_file):
        config_reader = ConfigReader(
            spec=command_watcher.CONFIG_READER_SPEC,
            argparse=args,
            ini=ini_file,
        )
    else:
        config_reader = ConfigReader(
            spec=command_watcher.CONFIG_READER_SPEC,
            argparse=(args, {}),
        )
    global watch
    watch = Watch(service_name=service, config_reader=config_reader)

    watch.log.info('Service name: {}'.format(service))

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

    if not checks.have_passed():
        watch.report(status=1, custom_output=checks.messages)
        watch.log.info(checks.messages)
    else:
        rsync_command = ['rsync', '-av', '--delete', '--stats']
        if args.rsync_args:
            rsync_command += shlex.split(args.rsync_args)
        rsync_command += [args.src, args.dest]

        watch.log.info('Source: {}'.format(args.src))
        watch.log.info('Destination: {}'.format(args.dest))

        watch.run(rsync_command)
        stats = parse_stats(watch.stdout)
        watch.report(status=0, performance_data=stats)
        watch.log.debug(stats)


if __name__ == "__main__":
    main()
