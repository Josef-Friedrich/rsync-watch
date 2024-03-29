import os
from dataclasses import dataclass
from typing import List
from unittest.mock import Mock, patch

import pytest
from stdout_stderr_capturing import Capturing

import rsync_watch

OUTPUT: str = """
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


@dataclass
class PatchResult:
    stdout: Capturing
    stderr: Capturing
    subprocess_run: Mock
    watch: Mock

    def assert_exclude_args(self, *args: str) -> None:
        self.watch.run.assert_called_with(
            [
                "rsync",
                "-av",
                "--delete",
                "--stats",
                *args,
                "tmp1",
                "tmp2",
            ],
            ignore_exceptions=[24],
        )


def _patch(
    args: List[str],
    mocks_subprocess_run: List[Mock] = [],
    watch_run_stdout: str = OUTPUT,
    watch_run_returncode: int = 0,
) -> PatchResult:
    with patch("sys.argv", ["cmd"] + list(args)), patch(
        "rsync_watch.check.subprocess.run"
    ) as subprocess_run, patch("rsync_watch.Watch") as Watch, Capturing(
        stream="stdout"
    ) as stdout, Capturing(stream="stderr") as stderr:
        watch = Watch.return_value
        watch.run.return_value.returncode = watch_run_returncode
        watch.stdout = watch_run_stdout
        if mocks_subprocess_run:
            subprocess_run.side_effect = mocks_subprocess_run

        rsync_watch.main()

        return PatchResult(
            stdout=stdout, stderr=stderr, subprocess_run=subprocess_run, watch=watch
        )


class TestIntegrationMock:
    def test_log_info(self) -> None:
        result = _patch(["--host-name", "test1", "tmp1", "tmp2"])
        result.watch.run.assert_called_with(
            ["rsync", "-av", "--delete", "--stats", "tmp1", "tmp2"],
            ignore_exceptions=[24],
        )

        info = result.watch.log.info
        info.assert_any_call("Source: tmp1")
        info.assert_any_call("Destination: tmp2")
        result.watch.log.info.assert_any_call("Service name: rsync_test1_tmp1_tmp2")

    def test_option_rsync_args(self) -> None:
        result = _patch(["--rsync-args", '--exclude "lol lol"', "tmp1", "tmp2"])
        result.watch.run.assert_called_with(
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


class TestOptionExclude:
    def test_single(self) -> None:
        result = _patch(["--exclude=school", "tmp1", "tmp2"])
        result.assert_exclude_args("--exclude=school")

    def test_multiple(self) -> None:
        result = _patch(["--exclude=school", '--exclude="My Music"', "tmp1", "tmp2"])
        result.assert_exclude_args("--exclude=school", '--exclude="My Music"')

    def test_without_equal_sign(self) -> None:
        result = _patch(["--exclude", "school", "tmp1", "tmp2"])
        result.assert_exclude_args("--exclude=school")

    def test_without(self) -> None:
        result = _patch(["tmp1", "tmp2"])
        result.assert_exclude_args()


class TestOptionCheckSshLogin:
    def test_action_check_failed_pass(self) -> None:
        result = _patch(
            [
                "--action-check-failed",
                "exception",
                "--check-ssh-login",
                "test@example.com",
                "tmp1",
                "tmp2",
            ],
            [Mock(returncode=0)],
        )
        assert result.subprocess_run.call_count == 1
        result.subprocess_run.assert_called_with(
            ["ssh", "test@example.com", "ls"], stderr=-3, stdout=-3
        )
        result.watch.run.assert_called_with(
            ["rsync", "-av", "--delete", "--stats", "tmp1", "tmp2"],
            ignore_exceptions=[24],
        )

    def test_action_check_failed_fail(self) -> None:
        with pytest.raises(rsync_watch.CommandWatcherError) as exception:
            _patch(
                [
                    "--action-check-failed",
                    "exception",
                    "--check-ssh-login",
                    "test@example.com",
                    "tmp1",
                    "tmp2",
                ],
                mocks_subprocess_run=[
                    Mock(returncode=255),
                ],
            )
        assert (
            exception.value.args[0]
            == "--check-ssh-login: 'test@example.com' is not reachable."
        )


class TestOptionCheckPing:
    def test_action_check_failed_fail(self) -> None:
        with pytest.raises(rsync_watch.CommandWatcherError) as exception:
            _patch(
                [
                    "--action-check-failed",
                    "exception",
                    "--check-ping",
                    "8.8.8.8",
                    "tmp1",
                    "tmp2",
                ],
                [Mock(returncode=1)],
            )
        assert exception.value.args[0] == "--check-ping: '8.8.8.8' is not reachable."

    def test_action_check_failed_pass(self) -> None:
        result = _patch(
            [
                "--action-check-failed",
                "exception",
                "--check-ping",
                "8.8.8.8",
                "tmp1",
                "tmp2",
            ],
            [Mock(returncode=0)],
        )
        assert result.subprocess_run.call_count == 1
        result.subprocess_run.assert_called_with(
            ["ping", "-c", "3", "8.8.8.8"], stderr=-3, stdout=-3
        )
        result.watch.run.assert_called_with(
            ["rsync", "-av", "--delete", "--stats", "tmp1", "tmp2"],
            ignore_exceptions=[24],
        )

    def test_no_exception_fail(self) -> None:
        result = _patch(
            ["--check-ping", "8.8.8.8", "tmp1", "tmp2"], [Mock(returncode=1)]
        )
        assert result.subprocess_run.call_count == 1
        result.subprocess_run.assert_called_with(
            ["ping", "-c", "3", "8.8.8.8"], stderr=-3, stdout=-3
        )

    def test_no_exception_pass(self) -> None:
        result = _patch(
            ["--check-ping", "8.8.8.8", "tmp1", "tmp2"], [Mock(returncode=0)]
        )
        assert result.subprocess_run.call_count == 1
        result.subprocess_run.assert_called_with(
            ["ping", "-c", "3", "8.8.8.8"], stderr=-3, stdout=-3
        )
        result.watch.run.assert_called_with(
            ["rsync", "-av", "--delete", "--stats", "tmp1", "tmp2"],
            ignore_exceptions=[24],
        )


class TestOptionCheckFile:
    def test_action_check_failed_pass(self) -> None:
        result = _patch(
            [
                "--action-check-failed",
                "exception",
                "--check-file",
                os.getcwd(),
                "tmp1",
                "tmp2",
            ],
        )
        assert result.watch.run.call_count == 1
        result.watch.run.assert_any_call(
            ["rsync", "-av", "--delete", "--stats", "tmp1", "tmp2"],
            ignore_exceptions=[24],
        )

    def test_action_check_failed_fail(self) -> None:
        with pytest.raises(rsync_watch.CommandWatcherError) as exception:
            _patch(
                [
                    "--action-check-failed",
                    "exception",
                    "--check-file",
                    "/d2c75c94-78b8-4f09-9fc4-3779d020bbd4",
                    "tmp1",
                    "tmp2",
                ]
            )
        assert (
            exception.value.args[0]
            == "--check-file: The file '/d2c75c94-78b8-4f09-9fc4-3779d020bbd4' "
            "doesn’t exist."
        )


class TestOptionDestUserGroup:
    def test_dest_local(self) -> None:
        result = _patch(["--dest-user-group=jf", "tmp1", "tmp2"])
        assert result.watch.run.call_count == 1
        result.watch.run.assert_any_call(
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

    def test_dest_remote(self) -> None:
        result = _patch(["--dest-user-group=jf", "tmp1", "remote:tmp2"])
        assert result.watch.run.call_count == 1
        result.watch.run.assert_any_call(
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
