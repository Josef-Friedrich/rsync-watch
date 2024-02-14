import os
import subprocess
from unittest.mock import Mock, patch

import pytest

from rsync_watch import (
    ChecksCollection,
    StatsNotFoundError,
    format_service_name,
    parse_stats,
)

SCRIPT: str = "rsync-watch.py"

OUTPUT1: str = """
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

OUTPUT_REAL: str = """
Number of files: 4,928 (reg: 3,256, dir: 1,672)
Number of created files: 112 (reg: 64, dir: 48)
Number of deleted files: 214 (reg: 125, dir: 89)
Number of regular files transferred: 64
Total file size: 4,222,882,233 bytes
Total transferred file size: 13,472,638 bytes
Literal data: 13,472,638 bytes
Matched data: 0 bytes
File list size: 65,536
File list generation time: 0.001 seconds
File list transfer time: 0.000 seconds
Total bytes sent: 13,631,370
Total bytes received: 19,859
sent 13,631,370 bytes  received 19,859 bytes
total size is 4,222,882,233  speedup is 309.34
"""

OUTPUT_WITHOUT_DELETED: str = """
receiving incremental file list
Number of files: 40 (reg: 16, dir: 24)
Number of created files: 0
Number of regular files transferred: 1
Total file size: 22,083 bytes
Total transferred file size: 14 bytes
Literal data: 0 bytes
Matched data: 14 bytes
File list size: 1,096
File list generation time: 0.001 seconds
File list transfer time: 0.000 seconds
Total bytes sent: 59
Total bytes received: 1,170
sent 59 bytes  received 1,170 bytes  819.33 bytes/sec
total size is 22,083  speedup is 17.97
"""

OUTPUT_2023: str = """
receiving incremental file list
Number of files: 2.931 (reg: 2.039, dir: 892)
Number of created files: 0
Number of deleted files: 0
Number of regular files transferred: 0
Total file size: 21.746.023.768 bytes
Total transferred file size: 0 bytes
Literal data: 0 bytes
Matched data: 0 bytes
File list size: 84.875
File list generation time: 0,147 seconds
File list transfer time: 0,000 seconds
Total bytes sent: 950
Total bytes received: 139.226
sent 950 bytes  received 139.226 bytes  3.548,76 bytes/sec
total size is 21.746.023.768  speedup is 155.133,72
"""


class TestUnitParseStats:
    def test_empty_string(self) -> None:
        with pytest.raises(StatsNotFoundError) as context, patch("rsync_watch.Watch"):
            parse_stats("")
        assert (
            context.value.args[0] == "Number of files: X,XXX (reg: X,XXX, dir: X,XXX)"
        )

    def test_output1(self) -> None:
        result = parse_stats(OUTPUT1)
        assert result == {
            "num_files": 1,
            "num_created_files": 3,
            "num_deleted_files": 4,
            "num_files_transferred": 5,
            "total_size": 6,
            "transferred_size": 7,
            "literal_data": 8,
            "matched_data": 9,
            "list_size": 10,
            "list_generation_time": 11.000,
            "list_transfer_time": 12.000,
            "bytes_sent": 13,
            "bytes_received": 14,
        }

    def test_output_real(self) -> None:
        result = parse_stats(OUTPUT_REAL)
        assert result == {
            "num_files": 4928,
            "num_created_files": 112,
            "num_deleted_files": 214,
            "num_files_transferred": 64,
            "total_size": 4222882233,
            "transferred_size": 13472638,
            "literal_data": 13472638,
            "matched_data": 0,
            "list_size": 65536,
            "list_generation_time": 0.001,
            "list_transfer_time": 0.000,
            "bytes_sent": 13631370,
            "bytes_received": 19859,
        }

    def test_output_without_deleted(self) -> None:
        result = parse_stats(OUTPUT_WITHOUT_DELETED)
        assert result == {
            "num_files": 40,
            "num_created_files": 0,
            "num_deleted_files": 0,
            "num_files_transferred": 1,
            "total_size": 22083,
            "transferred_size": 14,
            "literal_data": 0,
            "matched_data": 14,
            "list_size": 1096,
            "list_generation_time": 0.001,
            "list_transfer_time": 0.000,
            "bytes_sent": 59,
            "bytes_received": 1170,
        }

    def test_output_2023(self) -> None:
        result = parse_stats(OUTPUT_2023)
        assert result == {
            "num_files": 2931,
            "num_created_files": 0,
            "num_deleted_files": 0,
            "num_files_transferred": 0,
            "total_size": 21746023768,
            "transferred_size": 0,
            "literal_data": 0,
            "matched_data": 0,
            "list_size": 84875,
            "list_generation_time": 0.147,
            "list_transfer_time": 0.000,
            "bytes_sent": 950,
            "bytes_received": 139226,
        }


class TestUnitServiceName:
    def test_special_characters(self) -> None:
        assert format_service_name("/@:.", "", "") == "rsync_"

    def test_dash_underscore(self) -> None:
        assert format_service_name("-_-", "", "") == "rsync_"

    def test_tilde(self) -> None:
        assert format_service_name("l~o~l", "tmp1", "tmp2") == "rsync_l-o-l_tmp1_tmp2"

    def test_multiple_dashs_underscore(self) -> None:
        assert format_service_name("---_---", "", "") == "rsync_"

    def test_real_world(self) -> None:
        service = format_service_name(
            "wnas", "serverway:/var/backups/mysql", "/data/backup/host/serverway/mysql"
        )
        assert (
            service == "rsync_wnas_serverway-var-backups-mysql_"
            "data-backup-host-serverway-mysql"
        )


class TestUnitClassChecks:
    def get_checks(self, raise_exception: bool) -> ChecksCollection:
        return ChecksCollection(watch=Mock(), raise_exception=raise_exception)

    def test_initialisation_raise_exception_true(self) -> None:
        checks = self.get_checks(raise_exception=True)
        assert checks.raise_exception
        assert checks.messages == ""
        assert checks.passed

    def test_initialisation_raise_exception_false(self) -> None:
        checks = self.get_checks(raise_exception=False)
        assert not checks.raise_exception

    def test_method_have_passed_true(self) -> None:
        checks = self.get_checks(raise_exception=False)
        assert checks.have_passed()

    def test_method_have_passed_false(self) -> None:
        checks = self.get_checks(raise_exception=False)
        checks._log_fail("test")  # type: ignore
        assert not checks.have_passed()

    def test_method_check_file_pass(self) -> None:
        checks = self.get_checks(raise_exception=False)
        checks.check_file(os.getcwd())
        assert checks.have_passed()
        assert checks.messages == ""

    def test_method_check_file_fail(self) -> None:
        checks = self.get_checks(raise_exception=False)
        checks.check_file("/d2c75c94-78b8-4f09-9fc4-3779d020bbd4")
        assert not checks.have_passed()
        assert (
            checks.messages
            == "--check-file: The file '/d2c75c94-78b8-4f09-9fc4-3779d020bbd4' "
            "doesn’t exist."
        )


class TestIntegration:
    def test_without_arguments(self) -> None:
        process = subprocess.run([SCRIPT], encoding="utf-8", stderr=subprocess.PIPE)
        assert process.returncode == 2
        assert "the following arguments are required:" in process.stderr

    def test_help(self) -> None:
        process = subprocess.run(
            [SCRIPT, "--help"], encoding="utf-8", stdout=subprocess.PIPE
        )
        assert process.returncode == 0
        assert "usage: rsync-watch.py" in process.stdout
        assert (
            "Perform different checks before running the rsync task." in process.stdout
        )

    def test_version(self) -> None:
        process = subprocess.run(
            [SCRIPT, "--version"], encoding="utf-8", stdout=subprocess.PIPE
        )
        assert process.returncode == 0
        assert "rsync-watch.py " in process.stdout
