import argparse
import sys
from enum import Enum

from . import config, helpers, running


class ConfigAction(Enum):
    SYNC = "sync"
    CREATE = "create"


def cli_main(args) -> int:
    if args.debug:
        print(args)

    if args.which == "run":
        return running.main(
            debug=args.debug,
            is_simulate=args.simulate,
            project=args.project,
            table=args.table,
            partition_date=args.partition_date,
            request_page_limit=args.request_page_limit,
            history_days=args.history_days,
            raise_exception=args.raise_exception,
        )
    elif args.which == "config":
        return config.main(
            debug=args.debug,
            is_simulate=args.simulate,
            project=args.project,
            action=args.action,
            base_dir=args.base_dir,
        )
    else:
        print(helpers.bcolors.FAIL + "Unknown command" + helpers.bcolors.ENDC)
        return 1


def main():
    parser = argparse.ArgumentParser(description="datalake", prog="shopcloud-datalake")

    subparsers = parser.add_subparsers(help="commands", title="commands")
    parser.add_argument("--debug", "-d", help="Debug", action="store_true")
    parser.add_argument(
        "--simulate", "-s", help="Simulate the process", action="store_true"
    )
    parser.add_argument("--secrethub-token", help="Secrethub-Token", type=str)
    parser.add_argument("--project", help="The GCP project", type=str)
    parser.add_argument("--base-dir", help="Base directory", type=str, default="tables")
    parser.add_argument("--config", help="The Config Filename", type=str)

    parser_run = subparsers.add_parser("run", help="run")
    parser_run.add_argument(
        "--partition-date", help="Partition date", type=helpers.valid_date
    )
    parser_run.add_argument(
        "--history-days",
        help="Number of days in the history to run",
        type=int,
        default=1
    )
    parser_run.add_argument(
        "--request-page-limit", help="Limit per page", type=int, default=None
    )
    parser_run.add_argument(
        "--raise-exception",
        help="Raise exception flag",
        action="store_true"
    )
    parser_run.add_argument(
        "table", help="Table name", type=str, nargs="?", default=None
    )
    parser_run.set_defaults(which="run")

    parser_config = subparsers.add_parser("config", help="config")
    parser_config.add_argument(
        "action",
        help="Action to perform",
        type=str,
        choices=[ConfigAction.SYNC.value, ConfigAction.CREATE.value],
    )
    parser_config.set_defaults(which="config")

    args = parser.parse_args()
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    rc = cli_main(args)
    if rc != 0:
        sys.exit(rc)
