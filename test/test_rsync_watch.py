import unittest
import subprocess
import os
from rsync_watch import \
    parse_stats, \
    RsyncWatchError, \
    service_name, \
    StatsNotFoundError

import rsync_watch
from unittest.mock import patch
from unittest import mock

SCRIPT = os.path.realpath(
    os.path.join(os.path.dirname(__file__), '..', 'rsync_watch.py')
)

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

sent 13,631,370 bytes  received 19,859 bytes  700,063.03 bytes/sec
total size is 4,222,882,233  speedup is 309.34
'''


def patch_mulitple(args, mocks=[]):
    with patch('sys.argv',  ['cmd'] + list(args)), \
         patch('subprocess.run') as subprocess_run:

        if mocks:
            subprocess_run.side_effect = mocks
        rsync_watch.main()
    return {
        'subprocess_run': subprocess_run
    }


class TestUnitParseStats(unittest.TestCase):

    def test_empty_string(self):
        with self.assertRaises(StatsNotFoundError) as exception:
            parse_stats('')
        self.assertEqual(str(exception.exception),
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


class TestUnitServiceName(unittest.TestCase):

    def test_special_characters(self):
        self.assertEqual(service_name('/@:.', '', ''), 'rsync_')

    def test_dash_underscore(self):
        self.assertEqual(service_name('-_-', '', ''), 'rsync_')

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


class TestIntegrationMock(unittest.TestCase):

    def test_minimal(self):
        mock_objects = patch_mulitple(['tmp1', 'tmp2'])
        mock_objects['subprocess_run'].assert_called_with(
            ['rsync', '-av', '--stats', 'tmp1', 'tmp2'],
            encoding='utf-8',
            stderr=-2,
            stdout=-1
        )

    def test_check_ping_raise_exception_fail(self):
        with self.assertRaises(RsyncWatchError) as exception:
            patch_mulitple(
                ['--raise-exception', '--check-ping', '8.8.8.8', 'tmp1',
                 'tmp2'],
                [mock.Mock(returncode=1), mock.Mock()]
            )
        self.assertEqual(str(exception.exception),
                         'ping: “8.8.8.8” is not reachable.')

    def test_check_ping_raise_exception_pass(self):
        mock_objects = patch_mulitple(
            ['--raise-exception', '--check-ping', '8.8.8.8', 'tmp1', 'tmp2'],
            [mock.Mock(returncode=0), mock.Mock()]
        )
        self.assertEqual(mock_objects['subprocess_run'].call_count, 2)
        mock_objects['subprocess_run'].assert_any_call(
            ['ping', '-c', 3, '8.8.8.8']
        )
        mock_objects['subprocess_run'].assert_any_call(
            ['rsync', '-av', '--stats', 'tmp1', 'tmp2'],
            encoding='utf-8', stderr=-2, stdout=-1
        )

    def test_check_ping_no_exception_fail(self):
        mock_objects = patch_mulitple(
            ['--check-ping', '8.8.8.8', 'tmp1', 'tmp2'],
            [mock.Mock(returncode=1), mock.Mock()]
        )
        self.assertEqual(mock_objects['subprocess_run'].call_count, 1)
        mock_objects['subprocess_run'].assert_called_with(
            ['ping', '-c', 3, '8.8.8.8']
        )

    def test_check_ping_no_exception_pass(self):
        mock_objects = patch_mulitple(
            ['--check-ping', '8.8.8.8', 'tmp1', 'tmp2'],
            [mock.Mock(returncode=0), mock.Mock()]
        )
        self.assertEqual(mock_objects['subprocess_run'].call_count, 2)
        mock_objects['subprocess_run'].assert_any_call(
            ['ping', '-c', 3, '8.8.8.8']
        )
        mock_objects['subprocess_run'].assert_any_call(
            ['rsync', '-av', '--stats', 'tmp1', 'tmp2'],
            encoding='utf-8', stderr=-2, stdout=-1
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
            'usage: rsync_watch.py',
            process.stdout
        )


if __name__ == '__main__':
    unittest.main()
