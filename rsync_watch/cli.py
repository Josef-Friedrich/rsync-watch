from argparse import ArgumentParser
from importlib import metadata

__version__: str = metadata.version("rsync_watch")


def get_argparser() -> ArgumentParser:
    parser: ArgumentParser = ArgumentParser(
        description="A Python script to monitor the execution of a rsync task."
    )

    parser.add_argument(
        "--host-name",
        help="The hostname to submit over NSCA to the monitoring.",
    )

    parser.add_argument(
        "--dest-user-group",
        metavar="USER_GROUP_NAME",
        help="Both the user name and the group name of the destination will "
        "be set to this name.",
    )

    parser.add_argument(
        "--rsync-args",
        help="Rsync CLI arguments. Insert some rsync command line arguments. "
        "Wrap all arguments in one string, for example: "
        "--rsync-args '--exclude \"this folder\"'",
    )

    # checks

    checks = parser.add_argument_group(
        title="checks",
        description="Perform different checks before running the rsync task.",
    )

    checks.add_argument(
        "--action-check-failed",
        choices=("exception", "skip"),
        default="skip",
        help="Select action what to do when a check failed.",
    )

    checks.add_argument(
        "--check-file",
        metavar="FILE_PATH",
        help="Check if a file exists on the local machine.",
    )

    checks.add_argument(
        "--check-ping",
        metavar="DESTINATION",
        help="Check if a remote host is reachable by pinging. DESTINATION can "
        "a IP address or a host name or a full qualified host name.",
    )

    checks.add_argument(
        "--check-ssh-login",
        metavar="SSH_LOGIN",
        help="Check if a remote host is reachable over the network by SSHing "
        "into it. SSH_LOGIN: “root@192.168.1.1” "
        "or “root@example.com” or “example.com”.",
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s {version}".format(version=__version__),
    )

    parser.add_argument("src", help="The source ([[USER@]HOST:]SRC)")

    parser.add_argument("dest", help="The destination ([[USER@]HOST:]DEST)")

    return parser
