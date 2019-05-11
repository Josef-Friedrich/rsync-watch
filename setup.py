import os

from setuptools import setup, find_packages
import versioneer


def read(file_name):
    """
    Read the contents of a text file and return its content.

    :param str file_name: The name of the file to read.

    :return: The content of the text file.
    :rtype: str
    """
    return open(
        os.path.join(os.path.dirname(__file__), file_name),
        encoding='utf-8'
    ).read()


setup(
    name='rsync_watch',
    author='Josef Friedrich',
    author_email='josef@friedrich.rocks',
    description=('A Python script to monitor the execution of a rsync task.'),
    license='GPL3',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    project_urls={
        'Source': 'https://github.com/Josef-Friedrich/rsync-watch',
        'Tracker': 'https://github.com/Josef-Friedrich/rsync-watch/issues',
    },
    url='https://github.com/Josef-Friedrich/rsync-watch',
    python_requires='>=3.5',
    packages=find_packages(),
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.5',
    ],
    install_requires=[
        'pycrypto>=2.0',
        'six',
        'jflib>=0.1.14',
    ],
    entry_points={
        'console_scripts': [
            'rsync-watch.py = rsync_watch:main',
        ],
    },
)