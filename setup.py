from setuptools import setup
import os


def read(file_name):
    return open(
        os.path.join(os.path.dirname(__file__), file_name), encoding='utf-8'
    ).read()


setup(
    name='rsync_watch',
    author='Josef Friedrich',
    author_email='josef@friedrich.rocks',
    description=('A Python script to monitor the execution of a rsync task.'),
    license='GPL3',
    project_urls={
        'Source': 'https://github.com/Josef-Friedrich/rsync-watch',
        'Tracker': 'https://github.com/Josef-Friedrich/rsync-watch/issues',
    },
    url='https://github.com/Josef-Friedrich/rsync-watch',
    python_requires='>=3.6',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
)