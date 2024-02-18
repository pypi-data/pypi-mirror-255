#  Copyright (c) 2023 Roboto Technologies, Inc.

#  Copyright (c) 2023 Roboto Technologies, Inc.

import argparse

from ...domain.collections import Collection
from ..command import RobotoCommand
from ..context import CLIContext
from .shared_helpdoc import COLLECTION_ID_HELP


def delete(args, context: CLIContext, parser: argparse.ArgumentParser):
    Collection.from_id(
        collection_id=args.collection_id,
        delegate=context.collections,
    ).delete()
    print(f"Deleted collection {args.collection_id}")


def delete_setup_parser(parser):
    parser.add_argument("collection_id", type=str, help=COLLECTION_ID_HELP)


delete_command = RobotoCommand(
    name="delete",
    logic=delete,
    setup_parser=delete_setup_parser,
    command_kwargs={"help": "Delete a collection."},
)
