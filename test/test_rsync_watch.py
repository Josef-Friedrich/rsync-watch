import unittest
import subprocess
import os
from rsync_watch import parse_stats, StatsNotFoundError

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


class TestUnitParseStats(unittest.TestCase):

    def test_empty_string(self):
        with self.assertRaises(StatsNotFoundError) as exception:
            parse_stats('')
        self.assertEqual(str(exception.exception),
                         'Number of files: X (dir: X)')

    def test_output1(self):
        result = parse_stats(OUTPUT1)
        self.assertEqual(result, {
            'num_files': 1,
            'num_dirs': 2,
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


class TestIntegration(unittest.TestCase):

    def test_without_arguments(self):
        process = subprocess.run(
            [SCRIPT],
            encoding='utf-8',
            stderr=subprocess.PIPE
        )
        self.assertEqual(process.returncode, 2)
        self.assertIn(
            'the following arguments are required: src, dest',
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
            'usage: rsync_watch.py [-h] src dest',
            process.stdout
        )


if __name__ == '__main__':
    unittest.main()
