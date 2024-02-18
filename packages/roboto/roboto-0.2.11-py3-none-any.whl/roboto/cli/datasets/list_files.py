#  Copyright (c) 2023 Roboto Technologies, Inc.
import argparse
import sys

from ...domain.datasets import Dataset
from ..command import RobotoCommand
from ..context import CLIContext
from .shared_helpdoc import DATASET_ID_HELP


def list_files(args, context: CLIContext, parser: argparse.ArgumentParser):
    record = Dataset.from_id(
        args.dataset_id,
        context.datasets,
        context.files,
        context.transaction_manager,
    )

    for f in record.list_files(args.include, args.exclude):
        sys.stdout.write(f"{f.relative_path}\n")


def list_files_setup_parser(parser):
    parser.add_argument(
        "-d", "--dataset-id", type=str, required=True, help=DATASET_ID_HELP
    )
    parser.add_argument(
        "-i",
        "--include",
        type=str,
        nargs="*",
        help="Zero or more include filters (if path points to a directory)",
    )
    parser.add_argument(
        "-x",
        "--exclude",
        type=str,
        nargs="*",
        help="Zero or more exclude filters (if path points to a directory)",
    )


list_files_command = RobotoCommand(
    name="list-files",
    logic=list_files,
    setup_parser=list_files_setup_parser,
    command_kwargs={"help": "Lists files for a specific dataset."},
)
