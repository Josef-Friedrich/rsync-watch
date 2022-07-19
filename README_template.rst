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

{{ cli('rsync-watch.py --help') | literal }}
