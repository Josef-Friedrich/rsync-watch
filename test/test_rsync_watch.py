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


if __name__ == '__main__':
    unittest.main()
