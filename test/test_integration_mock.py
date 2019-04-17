import unittest
from unittest.mock import patch
from unittest import mock
from jflib import Capturing
import rsync_watch
import os

OUTPUT = '''
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


class TestCase(unittest.TestCase):

    def setUp(self):
        self.send_nsca = None
        self.subprocess_run = None
        self.watch = None
        self.stdout = None
        self.stderr = None

    def patch(self, args, mocks_subprocess_run=[], watch_run_stdout=OUTPUT,
              watch_run_returncode=0):
        with patch('sys.argv',  ['cmd'] + list(args)), \
             patch('rsync_watch.send_nsca') as self.send_nsca, \
             patch('rsync_watch.subprocess.run') as self.subprocess_run, \
             patch('rsync_watch.watch') as self.watch, \
             Capturing(stream='stdout') as self.stdout, \
             Capturing(stream='stderr') as self.stderr:

            self.watch.run.return_value.returncode = watch_run_returncode
            self.watch.stdout = watch_run_stdout
            if mocks_subprocess_run:
                self.subprocess_run.side_effect = mocks_subprocess_run

            rsync_watch.main()


class TestIntegrationMock(TestCase):

    def test_log_info(self):
        self.patch(['--host-name', 'test1', 'tmp1', 'tmp2'])
        self.watch.run.assert_called_with(
            ['rsync', '-av', '--delete', '--stats', 'tmp1', 'tmp2'],
        )

        info = self.watch.log.info
        info.assert_any_call('Source: tmp1')
        info.assert_any_call('Destination: tmp2')
        info.assert_any_call(
            'Rsync command: rsync -av --delete --stats tmp1 tmp2'
        )
        self.watch.log.info.assert_any_call(
            'Service name: rsync_test1_tmp1_tmp2'
        )

    def test_rsync_args(self):
        self.patch(['--rsync-args', '--exclude "lol lol"', 'tmp1', 'tmp2'])
        self.watch.run.assert_called_with(
            ['rsync', '-av', '--delete', '--stats', '--exclude', 'lol lol',
             'tmp1', 'tmp2'],
        )

    def test_rsync_exception(self):
        with self.assertRaises(rsync_watch.RsyncWatchError) as exception:
            self.patch(['tmp1', 'tmp2'], watch_run_returncode=1)
        self.assertEqual(str(exception.exception),
                         'The rsync task fails with a non-zero exit code.')


class TestNsca(TestCase):

    nsca_output = 'RSYNC OK | num_files=1 num_created_files=3 ' \
                    'num_deleted_files=4 num_files_transferred=5 ' \
                    'total_size=6 transferred_size=7 literal_data=8 ' \
                    'matched_data=9 list_size=10 ' \
                    'list_generation_time=11.0 ' \
                    'list_transfer_time=12.0 bytes_sent=13 bytes_received=14'

    def test_nsca_without_password(self):
        self.patch(
            ['--nsca-remote-host', '1.2.3.4', '--host-name', 'test1', 'tmp1',
             'tmp2']
        )
        self.watch.run.assert_called_with(
            ['rsync', '-av', '--delete', '--stats', 'tmp1', 'tmp2'],
        )

        self.send_nsca.assert_called_with(
            host_name=b'test1',
            remote_host=b'1.2.3.4',
            service_name=b'rsync_test1_tmp1_tmp2',
            status=0,
            text_output=self.nsca_output.encode(),
            password=None,
            encryption_method=None
        )

    # --nsca-remote-host
    # --nsca-password
    # --nsca-encryption-method
    def test_nsca_with_password(self):
        self.patch(
            ['--nsca-remote-host', '1.2.3.4', '--nsca-password', '1234',
             '--nsca-encryption-method', '8',  '--host-name', 'test1', 'tmp1',
             'tmp2']
        )
        self.assertEqual(self.watch.run.call_count, 1)

        self.send_nsca.assert_called_with(
            host_name=b'test1',
            remote_host=b'1.2.3.4',
            service_name=b'rsync_test1_tmp1_tmp2',
            status=0,
            text_output=self.nsca_output.encode(),
            password=b'1234',
            encryption_method=8
        )


class TestOptionCheckSshLogin(TestCase):

    def test_action_check_failed_pass(self):
        self.patch(
            ['--action-check-failed', 'exception', '--check-ssh-login',
             'test@example.com', 'tmp1', 'tmp2'],
            [mock.Mock(returncode=0)]
        )
        self.assertEqual(self.subprocess_run.call_count, 1)
        self.subprocess_run.assert_called_with(
            ['ssh', 'test@example.com', 'ls'], stderr=-3, stdout=-3
        )
        self.watch.run.assert_called_with(
            ['rsync', '-av', '--delete', '--stats', 'tmp1', 'tmp2']
        )

    def test_action_check_failed_fail(self):
        with self.assertRaises(rsync_watch.RsyncWatchError) as exception:
            self.patch(
                ['--action-check-failed', 'exception', '--check-ssh-login',
                 'test@example.com', 'tmp1', 'tmp2'],
                mocks_subprocess_run=[
                    mock.Mock(returncode=255),
                ]
            )
        self.assertEqual(
            str(exception.exception),
            '--check-ssh-login: \'test@example.com\' is not reachable.'
        )


class TestOptionCheckPing(TestCase):

    def test_action_check_failed_fail(self):
        with self.assertRaises(rsync_watch.RsyncWatchError) as exception:
            self.patch(
                ['--action-check-failed', 'exception', '--check-ping',
                 '8.8.8.8', 'tmp1', 'tmp2'],
                [mock.Mock(returncode=1)]
            )
        self.assertEqual(str(exception.exception),
                         '--check-ping: \'8.8.8.8\' is not reachable.')

    def test_action_check_failed_pass(self):
        self.patch(
            ['--action-check-failed', 'exception', '--check-ping', '8.8.8.8',
             'tmp1', 'tmp2'],
            [mock.Mock(returncode=0)]
        )
        self.assertEqual(self.subprocess_run.call_count, 1)
        self.subprocess_run.assert_called_with(
            ['ping', '-c', '3', '8.8.8.8'], stderr=-3, stdout=-3
        )
        self.watch.run.assert_called_with(
            ['rsync', '-av', '--delete', '--stats', 'tmp1', 'tmp2'],
        )

    def test_no_exception_fail(self):
        self.patch(
            ['--check-ping', '8.8.8.8', 'tmp1', 'tmp2'],
            [mock.Mock(returncode=1)]
        )
        self.assertEqual(self.subprocess_run.call_count, 1)
        self.subprocess_run.assert_called_with(
            ['ping', '-c', '3', '8.8.8.8'], stderr=-3, stdout=-3
        )

    def test_no_exception_pass(self):
        self.patch(
            ['--check-ping', '8.8.8.8', 'tmp1', 'tmp2'],
            [mock.Mock(returncode=0)]
        )
        self.assertEqual(self.subprocess_run.call_count, 1)
        self.subprocess_run.assert_called_with(
            ['ping', '-c', '3', '8.8.8.8'], stderr=-3, stdout=-3
        )
        self.watch.run.assert_called_with(
            ['rsync', '-av', '--delete', '--stats', 'tmp1', 'tmp2'],
        )


class TestOptionCheckFile(TestCase):

    def test_action_check_failed_pass(self):
        self.patch(
            ['--action-check-failed', 'exception', '--check-file', os.getcwd(),
             'tmp1', 'tmp2'],
        )
        self.assertEqual(self.watch.run.call_count, 1)
        self.watch.run.assert_any_call(
            ['rsync', '-av', '--delete', '--stats', 'tmp1', 'tmp2'],
        )

    def test_action_check_failed_fail(self):
        with self.assertRaises(rsync_watch.RsyncWatchError) as exception:
            self.patch(
                ['--action-check-failed', 'exception',
                 '--check-file', '/d2c75c94-78b8-4f09-9fc4-3779d020bbd4',
                 'tmp1', 'tmp2']
            )
        self.assertEqual(
            str(exception.exception),
            '--check-file: The file \'/d2c75c94-78b8-4f09-9fc4-3779d020bbd4\' '
            'doesn’t exist.'
        )
