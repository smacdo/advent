from advent.aoc.client import AocClient, AocLoginConfig

import argparse
import logging

logger = logging.getLogger(__name__)


def sync(args):
    # Load the AOC session cookie
    login_config = AocLoginConfig.try_load_from_file(".aoc_login")

    if login_config is None:
        logging.error(".aoc_login file is missing")
        logging.error(
            "***** Please copy your adventofcode.com session cookie to .aoc_session *****"
        )
        return

    # OK
    aoc_client = AocClient(login_config)
    print([str(s) for s in aoc_client.fetch_days(2023)])

    print("sync me")


def main():
    # Argument parsing.
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title="subcommands", dest="subparser_name")

    sync_parser = subparsers.add_parser("sync")
    sync_parser.set_defaults(func=sync)

    args = parser.parse_args()

    # Dispatch subcommand.
    if args.subparser_name == "sync":
        return sync(args)

    print("hello world")


main()
