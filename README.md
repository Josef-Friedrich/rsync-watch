[![Build Status](https://travis-ci.org/Josef-Friedrich/rsync-watch.svg?branch=master)](https://travis-ci.org/Josef-Friedrich/rsync-watch)
[![pypi.org](http://img.shields.io/pypi/v/rsync_watch.svg)](https://pypi.python.org/pypi/rsync_watch)
[![Documentation Status](https://readthedocs.org/projects/rsync-watch/badge/?version=latest)](https://rsync-watch.readthedocs.io/en/latest/?badge=latest)

# rsync-watch.py

A Python script to monitor the execution of a rsync task.

## Features

* The script `rsync-watch.py` parses the `rsync --stats` output and
  sends this statistics to a monitoring system like Nagios or Icinga
  using the NSCA protocol.

* The script `rsync-watch.py` can be configured to perform various
  checks before starting the rsync process.

```
usage: rsync-watch.py [-h] [--host-name HOST_NAME] [--rsync-args RSYNC_ARGS]
                      [--action-check-failed {exception,skip}]
                      [--check-file FILE_PATH] [--check-ping DESTINATION]
                      [--check-ssh-login SSH_LOGIN]
                      [--email-subject-prefix EMAIL_SUBJECT_PREFIX]
                      [--email-from-addr EMAIL_FROM_ADDR]
                      [--email-to-addr EMAIL_TO_ADDR]
                      [--email-smtp-login EMAIL_SMTP_LOGIN]
                      [--email-smtp-password EMAIL_SMTP_PASSWORD]
                      [--email-smtp-server EMAIL_SMTP_SERVER]
                      [--nsca-remote-host NSCA_REMOTE_HOST]
                      [--nsca-password NSCA_PASSWORD]
                      [--nsca-encryption-method NSCA_ENCRYPTION_METHOD]
                      [--nsca-port NSCA_PORT] [-v]
                      src dest

A Python script to monitor the execution of a rsync task.

positional arguments:
  src                   The source ([[USER@]HOST:]SRC)
  dest                  The destination ([[USER@]HOST:]DEST)

optional arguments:
  -h, --help            show this help message and exit
  --host-name HOST_NAME
                        The hostname to submit over NSCA to the monitoring.
  --rsync-args RSYNC_ARGS
                        Rsync CLI arguments. Insert some rsync command line
                        arguments.Wrap all arguments in one string, for
                        example: --rsync-args '--exclude "this folder"'
  -v, --version         show program's version number and exit

checks:
  Perform different checks before running the rsync task.

  --action-check-failed {exception,skip}
                        Select action what to do when a check failed.
  --check-file FILE_PATH
                        Check if a file exists on the local machine.
  --check-ping DESTINATION
                        Check if a remote host is reachable by pinging.
                        DESTINATION can a IP address or a host name or a full
                        qualified host name.
  --check-ssh-login SSH_LOGIN
                        Check if a remote host is reachable over the network
                        by SSHing into it. SSH_LOGIN: “root@192.168.1.1” or
                        “root@example.com” or “example.com”.

email:
  --email-subject-prefix EMAIL_SUBJECT_PREFIX
  --email-from-addr EMAIL_FROM_ADDR
  --email-to-addr EMAIL_TO_ADDR
  --email-smtp-login EMAIL_SMTP_LOGIN
  --email-smtp-password EMAIL_SMTP_PASSWORD
  --email-smtp-server EMAIL_SMTP_SERVER

nsca:
  Send status messages to the monitoring.

  --nsca-remote-host NSCA_REMOTE_HOST
                        IP address of the NSCA remote host.
  --nsca-password NSCA_PASSWORD
                        The NSCA password.
  --nsca-encryption-method NSCA_ENCRYPTION_METHOD
                        The NSCA encryption method. The supported encryption
                        methods are: 0 1 2 3 4 8 11 14 15 16
  --nsca-port NSCA_PORT
                        The NSCA port.

```
