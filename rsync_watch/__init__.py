#! /usr/bin/env python


import re
import shlex
import socket
import typing

from command_watcher import CommandWatcherError, Watch

from rsync_watch.check import ChecksCollection
from rsync_watch.cli import ArgumentsDefault, __version__, get_argparser  # noqa: F401

watch: Watch


class StatsNotFoundError(CommandWatcherError):
    """Raised when some stats regex couldn’t be found in stdout."""


def convert_number_to_int(formatted_number: str) -> int:
    """Convert a integer containing commas or dots to a integer without commas or dots.

    :param comma_integer: a integer containing commas or dots

    :return: A integer without commas or dots
    """

    formatted_number = formatted_number.replace(",", "")
    formatted_number = formatted_number.replace(".", "")

    return int(formatted_number)


def convert_number_to_float(formatted_number: str) -> float:
    return float(formatted_number.replace(",", "."))


def parse_stats(stdout: str) -> typing.Dict[str, typing.Union[int, float]]:
    """Parse the standard output of the rsync process.

    https://github.com/WayneD/rsync/blob/c69dc7a5ab473bb52a575b5803026c2694761084/main.c#L416-L465

    :param stdout: The standard output of the rsync process

    :return: A dictionary containing all the stats numbers.
    """
    result: typing.Dict[str, typing.Union[int, float]] = {}

    def search(regex: str, exception_msg: str) -> int:
        match = re.search(regex, stdout)
        if match:
            return convert_number_to_int(match.group(1))
        else:
            raise StatsNotFoundError(exception_msg)

    result["num_files"] = search(
        r"\nNumber of files: ([\d,\.]*)",
        "Number of files: X,XXX (reg: X,XXX, dir: X,XXX)",
    )

    result["num_created_files"] = search(
        r"\nNumber of created files: ([\d,\.]*)",
        "Number of created files: X,XXX (reg: X,XXX, dir: X,XXX)",
    )

    # num_deleted_files
    # This line is sometimes missing on rsync --version 3.1.2
    # raise no error
    match = re.search(r"\nNumber of deleted files: ([\d,\.]*)", stdout)
    if match:
        result["num_deleted_files"] = convert_number_to_int(match.group(1))
    else:
        result["num_deleted_files"] = 0

    result["num_files_transferred"] = search(
        r"\nNumber of regular files transferred: ([\d,\.]*)\n",
        "Number of regular files transferred: X,XXX",
    )

    result["total_size"] = search(
        r"\nTotal file size: ([\d,\.]*) bytes\n",
        "Total file size: X,XXX bytes",
    )

    result["transferred_size"] = search(
        r"\nTotal transferred file size: ([\d,\.]*) bytes\n",
        "Total transferred file size: X,XXX bytes",
    )

    result["literal_data"] = search(
        r"\nLiteral data: ([\d,\.]*) bytes\n",
        "Literal data: X,XXX bytes",
    )

    result["matched_data"] = search(
        r"\nMatched data: ([\d,\.]*) bytes\n",
        "Matched data: X,XXX bytes",
    )

    result["list_size"] = search(
        r"\nFile list size: ([\d,\.]*)\n", "File list size: X,XXX"
    )

    # list_generation_time
    match = re.search(r"\nFile list generation time: ([\d,\.]*) seconds\n", stdout)
    if match:
        result["list_generation_time"] = convert_number_to_float(match.group(1))
    else:
        raise StatsNotFoundError("File list generation time: X.XXX seconds")

    # list_transfer_time
    match = re.search(r"\nFile list transfer time: ([\d,\.]*) seconds\n", stdout)
    if match:
        result["list_transfer_time"] = convert_number_to_float(match.group(1))
    else:
        raise StatsNotFoundError("File list transfer time: X.XXX seconds")

    result["bytes_sent"] = search(
        r"\nTotal bytes sent: ([\d,\.]*)\n",
        "Total bytes sent: X,XXX",
    )

    result["bytes_received"] = search(
        r"\nTotal bytes received: ([\d,\.]*)\n",
        "Total bytes received: X,XXX",
    )

    return result


def format_service_name(host_name: str, src: str, dest: str) -> str:
    """Format a service name to use as a Nagios or Icinga service name.

    :param host_name: The hostname of the machine the rsync job running
      on.
    :param src: A source string rsync understands
    :param dest: A destination string rsync understands

    :return: The service name
    """
    result: str = f"rsync_{host_name}_{src}_{dest}"
    result = re.sub(r"[/@:\.~]", "-", result)
    result = re.sub(r"-*_-*", "_", result)
    result = re.sub(r"-{2,}", "-", result)
    result = re.sub(r"_{2,}", "_", result)
    result = re.sub(r"-$", "", result)
    result = re.sub(r"^-", "", result)
    return result


def build_rsync_command(args: ArgumentsDefault) -> list[str]:
    rsync_command: list[str] = ["rsync", "-av", "--delete", "--stats"]

    if args.dest_user_group:
        # https://stackoverflow.com/a/62982981
        # zsh:1: no matches found: --usermap=*:smb
        escape_star: str = ""
        if ":" in args.dest:
            escape_star = "\\"
        rsync_command += [
            f"--usermap={escape_star}*:{args.dest_user_group}",
            f"--groupmap={escape_star}*:{args.dest_user_group}",
        ]

    if args.exclude:
        for exclude in args.exclude:
            rsync_command.append(f"--exclude={exclude}")
    if args.rsync_args:
        rsync_command += shlex.split(args.rsync_args)
    rsync_command += [args.src, args.dest]

    return rsync_command


def main() -> None:
    """Main function. Gets called by `entry_points` `console_scripts`."""
    # To generate the argparser we use a not fully configured ConfigReader.
    # We need `args` for the configs.
    # We get the service name from the args.
    # A typical chicken-egg-situation.
    parser = get_argparser()
    args = typing.cast(ArgumentsDefault, parser.parse_args())

    host_name: str
    if not args.host_name:
        host_name = socket.gethostname()
    else:
        host_name = args.host_name

    service = format_service_name(host_name, args.src, args.dest)

    watch = Watch(
        service_name=service, service_display_name=f"rsync {args.src} {args.dest}"
    )

    watch.log.info(f"Service name: {service}")

    raise_exception: bool = False
    if args.action_check_failed == "exception":
        raise_exception = True
    checks: ChecksCollection = ChecksCollection(watch, raise_exception=raise_exception)
    if args.check_file:
        checks.check_file(args.check_file)
    if args.check_ping:
        checks.check_ping(args.check_ping)
    if args.check_ssh_login:
        checks.check_ssh_login(args.check_ssh_login)

    if not checks.have_passed():
        watch.report(status=1, custom_message=checks.messages)
        watch.log.info(checks.messages)
    else:
        rsync_command: list[str] = build_rsync_command(args)

        watch.log.info(f"Source: {args.src}")
        watch.log.info(f"Destination: {args.dest}")

        watch.run(rsync_command, ignore_exceptions=args.ignore_exceptions)  # type: ignore
        stats: typing.Dict[str, int | float] = parse_stats(watch.stdout)
        watch.report(status=0, performance_data=stats)
        watch.log.debug(stats)


if __name__ == "__main__":
    main()
