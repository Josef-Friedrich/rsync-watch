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
