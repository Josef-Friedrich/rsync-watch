#! /usr/bin/env python3

import os
import subprocess


def path(*path_segments):
    return os.path.join(os.getcwd(), *path_segments)


def open_file(*path_segments):
    file_path = path(*path_segments)
    open(file_path, "w").close()
    return open(file_path, "a")


header = open(path("README_header.md"), "r")
readme = open_file("README.md")

for line in header:
    readme.write(line)

cli_command = subprocess.Popen(
    "rsync-watch.py --help", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
)

readme.write("\n```\n")

for line in cli_command.stdout:
    readme.write(line.decode("utf-8"))
cli_command.wait()

readme.write("\n```\n")
readme.close()
