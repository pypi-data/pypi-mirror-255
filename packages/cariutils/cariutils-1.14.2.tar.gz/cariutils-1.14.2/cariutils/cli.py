"""
#
# CLI base classes
#
# Copyright(c) 2018, Carium, Inc. All rights reserved.
#
"""

import os
import sys
from argparse import ArgumentParser
from typing import List, NoReturn, Optional, Sequence

from cariutils.shortcuts import import_class


class Command:

    name = ""
    description = ""
    usage = ""

    @classmethod
    def init_args(cls, subparser: ArgumentParser) -> None:
        pass

    def __init__(self, args):
        self.args = args

    def execute(self) -> int:
        raise NotImplementedError("Command.execute()")

    def _execute(self) -> int:
        return self.execute()


class Cli:

    commands: Sequence[str] = []
    description = "cli"
    django_settings_module = ""
    cache_parser = False  # Creating the parser can be very, very slow when run many times in unit tests

    _parser_cache = {}

    @classmethod
    def init_args(cls, parser: ArgumentParser) -> None:
        pass

    @classmethod
    def create_arg_parser(cls):
        return ArgumentParser(description=cls.description)

    @classmethod
    def main(cls, argv: Optional[List[str]] = None) -> NoReturn:

        # Automatically setup Django if necessary
        if "DJANGO_SETTINGS_MODULE" not in os.environ:
            if cls.django_settings_module != "":
                os.environ["DJANGO_SETTINGS_MODULE"] = cls.django_settings_module

        if "DJANGO_SETTINGS_MODULE" in os.environ:
            import django

            django.setup()

        parser = cls._load_parser()

        args = parser.parse_args(argv if argv is not None else sys.argv[1:])
        if args.cmd_class is None:
            raise ValueError("subcommand is expected")

        sys.exit(args.cmd_class(args)._execute() or 0)

    @classmethod
    def _load_parser(cls):
        if not cls.cache_parser:
            return cls.load_parser()

        if cls not in cls._parser_cache:
            cls._parser_cache[cls] = cls.load_parser()

        return cls._parser_cache[cls]

    @classmethod
    def load_parser(cls):
        parser = cls.create_arg_parser()
        parser.set_defaults(cmd_class=None)
        cls.init_args(parser)

        # Initialize commands
        subparsers = parser.add_subparsers()
        for cmd in cls.get_commands():
            if "." not in cmd:
                cmd = "{}.{}".format(cls.__module__, cmd)

            cmd_class = import_class(cmd)
            if cmd_class.name is None:
                raise ValueError("{} class does not have name".format(cmd_class.__name__))

            params = {
                section: getattr(cmd_class, section)
                for section in ("description", "usage")
                if hasattr(cmd_class, section)
            }
            _subparser = subparsers.add_parser(cmd_class.name, **params)
            _subparser.set_defaults(cmd_class=cmd_class)
            cmd_class.init_args(_subparser)

        return parser

    @classmethod
    def get_commands(cls) -> Sequence[str]:
        return cls.commands

    @classmethod
    def reset(cls):
        cls._parser_cache.clear()
