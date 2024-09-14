.. image:: http://img.shields.io/pypi/v/rsync-watch.svg
    :target: https://pypi.org/project/rsync-watch
    :alt: This package on the Python Package Index

.. image:: https://github.com/Josef-Friedrich/rsync-watch/actions/workflows/tests.yml/badge.svg
    :target: https://github.com/Josef-Friedrich/rsync-watch/actions/workflows/tests.yml
    :alt: Tests

.. image:: https://readthedocs.org/projects/rsync-watch/badge/?version=latest
    :target: https://rsync-watch.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

rsync-watch.py
==============

A Python script to monitor the execution of a rsync task.

Features
--------

-  The script ``rsync-watch.py`` parses the ``rsync --stats`` output and
   sends this statistics to a monitoring system like Nagios or Icinga
   using the NSCA protocol.

-  The script ``rsync-watch.py`` can be configured to perform various
   checks before starting the rsync process.

:: 

    usage: rsync-watch.py [-h] [--host-name HOST_NAME] [--dest-user-group USER_GROUP_NAME] [--exclude EXCLUDE]
                          [--rsync-args RSYNC_ARGS] [--action-check-failed {exception,skip}] [--check-file FILE_PATH]
                          [--check-ping DESTINATION] [--check-ssh-login SSH_LOGIN] [-v]
                          src dest

    A Python script to monitor the execution of a rsync task.

    positional arguments:
      src                   The source ([[USER@]HOST:]SRC)
      dest                  The destination ([[USER@]HOST:]DEST)

    options:
      -h, --help            show this help message and exit
      --host-name HOST_NAME
                            The hostname to submit over NSCA to the monitoring.
      --dest-user-group USER_GROUP_NAME
                            Both the user name and the group name of the destination will be set to this name.
      --exclude EXCLUDE     See the documention of --exclude in the rsync manual.
      --rsync-args RSYNC_ARGS
                            Rsync CLI arguments. Insert some rsync command line arguments. Wrap all arguments in one string, for
                            example: --rsync-args '--exclude "this folder"'
      -v, --version         show program's version number and exit

    checks:
      Perform different checks before running the rsync task.

      --action-check-failed {exception,skip}
                            Select action what to do when a check failed.
      --check-file FILE_PATH
                            Check if a file exists on the local machine.
      --check-ping DESTINATION
                            Check if a remote host is reachable by pinging. DESTINATION can a IP address or a host name or a full
                            qualified host name.
      --check-ssh-login SSH_LOGIN
                            Check if a remote host is reachable over the network by SSHing into it. SSH_LOGIN: “root@192.168.1.1” or
                            “root@example.com” or “example.com”.

