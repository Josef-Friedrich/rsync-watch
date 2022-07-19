import os
import unittest
from unittest import mock
from unittest.mock import patch

from stdout_stderr_capturing import Capturing

import rsync_watch

OUTPUT = """
sending incremental file list
Number of files: 1 (dir: 2)
Number of created files: 3
Number of deleted files: 4
Number of regular files transferred: 5
Total file size: 6 bytes
Total transferred file size: 7 bytes
Literal data: 8 bytes
Matched data: 9 bytes
File list size: 10
File list generation time: 11.000 seconds
File list transfer time: 12.000 seconds
Total bytes sent: 13
Total bytes received: 14
sent 61 bytes  received 17 bytes  156.00 bytes/sec
total size is 0  speedup is 0.00
"""


class TestCase(unittest.TestCase):
    def setUp(self):
        self.subprocess_run = None
        self.stdout = None
        self.stderr = None

    def patch(
        self,
        args: list[str],
        mocks_subprocess_run: list[mock.Mock] = [],
        watch_run_stdout: str = OUTPUT,
        watch_run_returncode: int = 0,
    ):
        with patch("sys.argv", ["cmd"] + list(args)), patch(
            "rsync_watch.subprocess.run"
        ) as self.subprocess_run, patch("rsync_watch.Watch") as Watch, Capturing(
            stream="stdout"
        ) as self.stdout, Capturing(
            stream="stderr"
        ) as self.stderr:

            self.watch = Watch.return_value
            self.watch.run.return_value.returncode = watch_run_returncode
            self.watch.stdout = watch_run_stdout
            if mocks_subprocess_run:
                self.subprocess_run.side_effect = mocks_subprocess_run

            rsync_watch.main()


class TestIntegrationMock(TestCase):
    def test_log_info(self):
        self.patch(["--host-name", "test1", "tmp1", "tmp2"])
        self.watch.run.assert_called_with(
            ["rsync", "-av", "--delete", "--stats", "tmp1", "tmp2"],
            ignore_exceptions=[24],
        )

        info = self.watch.log.info
        info.assert_any_call("Source: tmp1")
        info.assert_any_call("Destination: tmp2")
        self.watch.log.info.assert_any_call("Service name: rsync_test1_tmp1_tmp2")

    def test_rsync_args(self):
        self.patch(["--rsync-args", '--exclude "lol lol"', "tmp1", "tmp2"])
        self.watch.run.assert_called_with(
            [
                "rsync",
                "-av",
                "--delete",
                "--stats",
                "--exclude",
                "lol lol",
                "tmp1",
                "tmp2",
            ],
            ignore_exceptions=[24],
        )


class TestOptionCheckSshLogin(TestCase):
    def test_action_check_failed_pass(self):
        self.patch(
            [
                "--action-check-failed",
                "exception",
                "--check-ssh-login",
                "test@example.com",
                "tmp1",
                "tmp2",
            ],
            [mock.Mock(returncode=0)],
        )
        self.assertEqual(self.subprocess_run.call_count, 1)
        self.subprocess_run.assert_called_with(
            ["ssh", "test@example.com", "ls"], stderr=-3, stdout=-3
        )
        self.watch.run.assert_called_with(
            ["rsync", "-av", "--delete", "--stats", "tmp1", "tmp2"],
            ignore_exceptions=[24],
        )

    def test_action_check_failed_fail(self):
        with self.assertRaises(rsync_watch.CommandWatcherError) as exception:
            self.patch(
                [
                    "--action-check-failed",
                    "exception",
                    "--check-ssh-login",
                    "test@example.com",
                    "tmp1",
                    "tmp2",
                ],
                mocks_subprocess_run=[
                    mock.Mock(returncode=255),
                ],
            )
        self.assertEqual(
            str(exception.exception),
            "--check-ssh-login: 'test@example.com' is not reachable.",
        )


class TestOptionCheckPing(TestCase):
    def test_action_check_failed_fail(self):
        with self.assertRaises(rsync_watch.CommandWatcherError) as exception:
            self.patch(
                [
                    "--action-check-failed",
                    "exception",
                    "--check-ping",
                    "8.8.8.8",
                    "tmp1",
                    "tmp2",
                ],
                [mock.Mock(returncode=1)],
            )
        self.assertEqual(
            str(exception.exception), "--check-ping: '8.8.8.8' is not reachable."
        )

    def test_action_check_failed_pass(self):
        self.patch(
            [
                "--action-check-failed",
                "exception",
                "--check-ping",
                "8.8.8.8",
                "tmp1",
                "tmp2",
            ],
            [mock.Mock(returncode=0)],
        )
        self.assertEqual(self.subprocess_run.call_count, 1)
        self.subprocess_run.assert_called_with(
            ["ping", "-c", "3", "8.8.8.8"], stderr=-3, stdout=-3
        )
        self.watch.run.assert_called_with(
            ["rsync", "-av", "--delete", "--stats", "tmp1", "tmp2"],
            ignore_exceptions=[24],
        )

    def test_no_exception_fail(self):
        self.patch(
            ["--check-ping", "8.8.8.8", "tmp1", "tmp2"], [mock.Mock(returncode=1)]
        )
        self.assertEqual(self.subprocess_run.call_count, 1)
        self.subprocess_run.assert_called_with(
            ["ping", "-c", "3", "8.8.8.8"], stderr=-3, stdout=-3
        )

    def test_no_exception_pass(self):
        self.patch(
            ["--check-ping", "8.8.8.8", "tmp1", "tmp2"], [mock.Mock(returncode=0)]
        )
        self.assertEqual(self.subprocess_run.call_count, 1)
        self.subprocess_run.assert_called_with(
            ["ping", "-c", "3", "8.8.8.8"], stderr=-3, stdout=-3
        )
        self.watch.run.assert_called_with(
            ["rsync", "-av", "--delete", "--stats", "tmp1", "tmp2"],
            ignore_exceptions=[24],
        )


class TestOptionCheckFile(TestCase):
    def test_action_check_failed_pass(self):
        self.patch(
            [
                "--action-check-failed",
                "exception",
                "--check-file",
                os.getcwd(),
                "tmp1",
                "tmp2",
            ],
        )
        self.assertEqual(self.watch.run.call_count, 1)
        self.watch.run.assert_any_call(
            ["rsync", "-av", "--delete", "--stats", "tmp1", "tmp2"],
            ignore_exceptions=[24],
        )

    def test_action_check_failed_fail(self):
        with self.assertRaises(rsync_watch.CommandWatcherError) as exception:
            self.patch(
                [
                    "--action-check-failed",
                    "exception",
                    "--check-file",
                    "/d2c75c94-78b8-4f09-9fc4-3779d020bbd4",
                    "tmp1",
                    "tmp2",
                ]
            )
        self.assertEqual(
            str(exception.exception),
            "--check-file: The file '/d2c75c94-78b8-4f09-9fc4-3779d020bbd4' "
            "doesn’t exist.",
        )


class TestOptionDestUserGroup(TestCase):
    def test_dest_local(self):
        self.patch(["--dest-user-group=jf", "tmp1", "tmp2"])
        self.assertEqual(self.watch.run.call_count, 1)
        self.watch.run.assert_any_call(
            [
                "rsync",
                "-av",
                "--delete",
                "--stats",
                "--usermap=*:jf",
                "--groupmap=*:jf",
                "tmp1",
                "tmp2",
            ],
            ignore_exceptions=[24],
        )

    def test_dest_remote(self):
        self.patch(["--dest-user-group=jf", "tmp1", "remote:tmp2"])
        self.assertEqual(self.watch.run.call_count, 1)
        self.watch.run.assert_any_call(
            [
                "rsync",
                "-av",
                "--delete",
                "--stats",
                "--usermap=\\*:jf",
                "--groupmap=\\*:jf",
                "tmp1",
                "remote:tmp2",
            ],
            ignore_exceptions=[24],
        )
