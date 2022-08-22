import os
import subprocess
from typing import List

from command_watcher import CommandWatcherError, Watch


class ChecksCollection:
    """Collect multiple check results.

    :params raise_exception: Raise an exception it some checks have
      failed.
    """

    raise_exception: bool
    _messages: List[str]
    passed: bool
    watch: Watch

    def __init__(self, watch: Watch, raise_exception: bool = True) -> None:
        self.watch = watch
        self.raise_exception = raise_exception
        self._messages: List[str] = []
        self.passed = True

    @property
    def messages(self) -> str:
        """
        :return: A concatenated string containing all messages of all failed
          checks.
        """
        return " ".join(self._messages)

    def _log_fail(self, message: str) -> None:
        self._messages.append(message)
        self.watch.log.warning(message)
        self.passed = False

    def check_file(self, file_path: str) -> None:
        """Check if a file exists.

        :param file_path: The file to check.
        """
        if not os.path.exists(file_path):
            self._log_fail(
                "--check-file: The file '{}' doesn’t exist.".format(file_path)
            )
        else:
            self.watch.log.info("--check-file: The file '{}' exists.".format(file_path))

    def check_ping(self, dest: str) -> None:
        """Check if a remote host is reachable by pinging to it.

        :param dest: A destination to ping to.
        """
        process = subprocess.run(
            ["ping", "-c", "3", dest],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if process.returncode != 0:
            self._log_fail("--check-ping: '{}' is not reachable.".format(dest))
        else:
            self.watch.log.info("--check-ping: '{}' is reachable.".format(dest))

    def check_ssh_login(self, ssh_host: str) -> None:
        """Check if the given host is online by retrieving its hostname.

        :param ssh_host: A ssh host string in the form of:
          `user@hostname` or `hostname` or `alias` (as specified in
          `~/.ssh/config`)
        """
        process = subprocess.run(
            ["ssh", ssh_host, "ls"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if not process.returncode == 0:
            self._log_fail("--check-ssh-login: '{}' is not reachable.".format(ssh_host))
        else:
            self.watch.log.info(
                "--check-ssh-login: '{}' is reachable.".format(ssh_host)
            )

    def have_passed(self) -> bool:
        """
        :return: True in fall checks have passed else false.
        :rtype: boolean"""
        if self.raise_exception and not self.passed:
            raise CommandWatcherError(self.messages)
        return self.passed
