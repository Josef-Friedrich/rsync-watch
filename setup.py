from setuptools import setup, find_packages
import os
import versioneer


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
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    project_urls={
        'Source': 'https://github.com/Josef-Friedrich/rsync-watch',
        'Tracker': 'https://github.com/Josef-Friedrich/rsync-watch/issues',
    },
    url='https://github.com/Josef-Friedrich/rsync-watch',
    python_requires='>=3.6',
    packages=find_packages(),
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires = ['pycrypto>=2.0', 'six'],
    entry_points = {
        'console_scripts': [
            'rsync-watch.py = rsync_watch:main',
        ],
    },
)