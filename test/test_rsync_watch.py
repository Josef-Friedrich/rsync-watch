import unittest
from unittest.mock import patch
import subprocess
import os

from rsync_watch import \
    Checks, \
    parse_stats, \
    service_name, \
    StatsNotFoundError


SCRIPT = 'rsync-watch.py'

OUTPUT1 = '''
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
'''

OUTPUT_REAL = '''
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
'''

OUTPUT_WITHOUT_DELETED = '''
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
'''


class TestUnitParseStats(unittest.TestCase):

    def test_empty_string(self):
        with self.assertRaises(StatsNotFoundError) as context, \
             patch('rsync_watch.watch'):
            parse_stats('')
        self.assertEqual(str(context.exception),
                         'Number of files: X,XXX (reg: X,XXX, dir: X,XXX)')

    def test_output1(self):
        result = parse_stats(OUTPUT1)
        self.assertEqual(result, {
            'num_files': 1,
            'num_created_files': 3,
            'num_deleted_files': 4,
            'num_files_transferred': 5,
            'total_size': 6,
            'transferred_size': 7,
            'literal_data': 8,
            'matched_data': 9,
            'list_size': 10,
            'list_generation_time': 11.000,
            'list_transfer_time': 12.000,
            'bytes_sent': 13,
            'bytes_received': 14,
        })

    def test_output_real(self):
        result = parse_stats(OUTPUT_REAL)
        self.assertEqual(result, {
            'num_files': 4928,
            'num_created_files': 112,
            'num_deleted_files': 214,
            'num_files_transferred': 64,
            'total_size': 4222882233,
            'transferred_size': 13472638,
            'literal_data': 13472638,
            'matched_data': 0,
            'list_size': 65536,
            'list_generation_time': 0.001,
            'list_transfer_time': 0.000,
            'bytes_sent': 13631370,
            'bytes_received': 19859,
        })

    def test_output_without_deleted(self):
        result = parse_stats(OUTPUT_WITHOUT_DELETED)
        self.assertEqual(result, {
            'num_files': 40,
            'num_created_files': 0,
            'num_deleted_files': 0,
            'num_files_transferred': 1,
            'total_size': 22083,
            'transferred_size': 14,
            'literal_data': 0,
            'matched_data': 14,
            'list_size': 1096,
            'list_generation_time': 0.001,
            'list_transfer_time': 0.000,
            'bytes_sent': 59,
            'bytes_received': 1170,
        })


class TestUnitServiceName(unittest.TestCase):

    def test_special_characters(self):
        self.assertEqual(service_name('/@:.', '', ''), 'rsync_')

    def test_dash_underscore(self):
        self.assertEqual(service_name('-_-', '', ''), 'rsync_')

    def test_tilde(self):
        self.assertEqual(service_name('l~o~l', 'tmp1', 'tmp2'),
                         'rsync_l-o-l_tmp1_tmp2')

    def test_multiple_dashs_underscore(self):
        self.assertEqual(service_name('---_---', '', ''), 'rsync_')

    def test_real_world(self):
        service = service_name(
            'wnas',
            'serverway:/var/backups/mysql',
            '/data/backup/host/serverway/mysql'
        )
        self.assertEqual(
            service,
            'rsync_wnas_serverway-var-backups-mysql_'
            'data-backup-host-serverway-mysql'
        )


class TestUnitClassChecks(unittest.TestCase):

    def get_checks(self, raise_exception):
        return Checks(raise_exception=raise_exception)

    def test_initialisation_raise_exception_true(self):
        checks = self.get_checks(raise_exception=True)
        self.assertEqual(checks.raise_exception, True)
        self.assertEqual(checks.messages, '')
        self.assertEqual(checks.passed, True)

    def test_initialisation_raise_exception_false(self):
        checks = self.get_checks(raise_exception=False)
        self.assertEqual(checks.raise_exception, False)

    def test_method_have_passed_true(self):
        checks = self.get_checks(raise_exception=False)
        self.assertEqual(checks.have_passed(), True)

    def test_method_have_passed_false(self):
        checks = self.get_checks(raise_exception=False)
        checks._log_fail('test')
        self.assertEqual(checks.have_passed(), False)

    def test_method_check_file_pass(self):
        checks = self.get_checks(raise_exception=False)
        checks.check_file(os.getcwd())
        self.assertEqual(checks.have_passed(), True)
        self.assertEqual(checks.messages, '')

    def test_method_check_file_fail(self):
        checks = self.get_checks(raise_exception=False)
        checks.check_file('/d2c75c94-78b8-4f09-9fc4-3779d020bbd4')
        self.assertEqual(checks.have_passed(), False)
        self.assertEqual(
            checks.messages,
            '--check-file: The file \'/d2c75c94-78b8-4f09-9fc4-3779d020bbd4\' '
            'doesn’t exist.'
        )


class TestIntegration(unittest.TestCase):

    def test_without_arguments(self):
        process = subprocess.run(
            [SCRIPT],
            encoding='utf-8',
            stderr=subprocess.PIPE
        )
        self.assertEqual(process.returncode, 2)
        self.assertIn(
            'the following arguments are required:',
            process.stderr
        )

    def test_help(self):
        process = subprocess.run(
            [SCRIPT, '--help'],
            encoding='utf-8',
            stdout=subprocess.PIPE
        )
        self.assertEqual(process.returncode, 0)
        self.assertIn(
            'usage: rsync-watch.py',
            process.stdout
        )
        self.assertIn(
            'Perform different checks before running the rsync task.',
            process.stdout
        )

    def test_version(self):
        process = subprocess.run(
            [SCRIPT, '--version'],
            encoding='utf-8',
            stdout=subprocess.PIPE
        )
        self.assertEqual(process.returncode, 0)
        self.assertIn(
            'rsync-watch.py ',
            process.stdout
        )


if __name__ == '__main__':
    unittest.main()
