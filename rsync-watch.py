#! /usr/bin/env python3

import argparse
import subprocess


def parse_args():
    parser = argparse.ArgumentParser(
        description='A Python script to monitor the execution of a rsync task.'
    )
    parser.add_argument(
        'src',
        help='The source ([[USER@]HOST:]SRC)'
    )
    parser.add_argument(
        'dest',
        help='The destination ([[USER@]HOST:]DEST)')

    return parser.parse_args()


def parse_stats(stdout):
    pass
    # num_files=${STAT_NUM_FILES} \
    # num_created_files=${STAT_NUM_CREATED_FILES} \
    # num_deleted_files=${STAT_NUM_DELETED_FILES} \
    # num_files_transferred=${STAT_NUM_FILES_TRANSFERRED} \
    # total_size=${STAT_TOTAL_SIZE} \
    # transferred_size=${STAT_TRANSFERRED_SIZE} \
    # literal_data=${STAT_LITERAL_DATA} \
    # matched_data=${STAT_MATCHED_DATA} \
    # list_size=${STAT_LIST_SIZE} \
    # list_generation_time=${STAT_LIST_GENERATION_TIME} \
    # list_transfer_time=${STAT_LIST_TRANSFER_TIME} \
    # bytes_sent=${STAT_BYTES_SENT} \
    # bytes_received=${STAT_BYTES_RECEIVED}"


def main():
    args = parse_args()

    process = subprocess.run(
        ['rsync', '-av', '--stats', args.src, args.dest],
        encoding='utf-8',
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    print(process.stdout)


if __name__ == "__main__":
    main()
