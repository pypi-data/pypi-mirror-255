#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
  ████
██    ██   Datature
  ██  ██   Powering Breakthrough AI
    ██

@File    :   main.py
@Author  :   Raighne.Weng
@Version :   1.6.0
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   CLI main entrance
'''

import sys

from datature.nexus.cli.commands import Commands
from datature.nexus.cli import functions, messages
from datature.nexus.error import ErrorWithCode, ForbiddenError


def main() -> None:
    """
    Executes the main function of cli.

    """
    try:
        commands = Commands()
        args = commands.parse_args()

        if args.command == "projects":
            handle_project_command(commands)
        elif args.command == "assets":
            handle_asset_command(commands)
        elif args.command == "annotations":
            handle_annotation_command(commands)
        elif args.command == "artifacts":
            handle_artifact_command(commands)
        else:
            commands.print_help()
    except KeyboardInterrupt:
        sys.exit(0)
    except (ForbiddenError, ErrorWithCode, IOError) as error:
        handle_error(error)


def handle_project_command(commands):
    """
    Executes the project level function of cli.

    """
    args = commands.parse_args()
    if args.action == "auth":
        functions.authenticate()
    elif args.action == "select":
        functions.select_project()
    elif args.action == "list":
        functions.list_projects()
    else:
        commands.print_help(args.command)


def handle_asset_command(commands):
    """
    Executes the asset level function of cli.

    """
    args = commands.parse_args()
    if args.action == "upload":
        functions.upload_assets(args.path, args.groups)
    elif args.action == "groups":
        functions.assets_group(args.group)
    else:
        commands.print_help(args.command)


def handle_annotation_command(commands):
    """
    Executes the annotation level function of cli.

    """
    args = commands.parse_args()
    if args.action == "upload":
        functions.upload_annotations(args.path)
    elif args.action == "download":
        functions.download_annotations(args.path, args.format)
    else:
        commands.print_help(args.command)


def handle_artifact_command(commands):
    """
    Executes the artifact level function of cli.

    """
    args = commands.parse_args()
    if args.action == "download":
        functions.download_artifact(args.artifact_id, args.format)
    else:
        commands.print_help(args.command)


def handle_error(error):
    """
    Cli handle error functions.

    """
    if isinstance(error, ForbiddenError):
        print(messages.AUTHENTICATION_FAILED_MESSAGE)
    else:
        print(messages.UNKNOWN_ERROR_SUPPORT_MESSAGE)
    sys.exit(1)
