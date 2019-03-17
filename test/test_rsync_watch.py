import unittest
import subprocess
import os

SCRIPT = os.path.realpath(
    os.path.join(os.path.dirname(__file__), '..', 'rsync-watch.py')
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
            'usage: rsync-watch.py [-h] src dest',
            process.stdout
        )


if __name__ == '__main__':
    unittest.main()
