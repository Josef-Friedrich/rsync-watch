from argparse import ArgumentParser, Namespace

from rsync_watch.cli import get_argparser


def parse_args(*args: str) -> Namespace:
    parser: ArgumentParser = get_argparser()
    return parser.parse_args(args)


class TestOptionIgnoreExceptions:
    def test_not_specified(self) -> None:
        args = parse_args("a", "b")
        assert args.ignore_exceptions == [24]

    def test_single_exit_codes(self) -> None:
        args = parse_args("--ignore-exceptions", "1", "a", "b")
        assert args.ignore_exceptions == [1, 24]

    def test_multiple_exit_codes(self) -> None:
        args = parse_args("--ignore-exceptions", "1,2,3", "a", "b")
        assert args.ignore_exceptions == [1, 2, 3, 24]
