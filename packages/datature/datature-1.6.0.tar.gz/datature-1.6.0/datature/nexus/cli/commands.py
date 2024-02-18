#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
  ████
██    ██   Datature
  ██  ██   Powering Breakthrough AI
    ██

@File    :   commands.py
@Author  :   Raighne.Weng
@Version :   1.6.0
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   CLI supported commands
'''

import sys
from typing import Optional
from argparse import ArgumentParser, _SubParsersAction

from datature import nexus

# pylint: disable=W0212


class Commands:
    """All Datature CLI commands."""

    def __init__(self) -> None:
        self.parser = ArgumentParser(
            prog='datature',
            description=
            "Command line tool to create/upload/download datasets on datature nexus.",
        )

        self.parser.add_argument('-v',
                                 '--version',
                                 action='version',
                                 version=f'%(prog)s {nexus.__version__}')

        self.subparsers = self.parser.add_subparsers(dest="command")
        self._add_project_parser()
        self._add_asset_parser()
        self._add_annotation_parser()
        self._add_artifact_parser()
        self._add_help_parser()

    def _add_project_parser(self):
        """Project level parser."""
        projects = self.subparsers.add_parser(
            "projects",
            help="Projects management.",
            description=
            "datature projects - auth/list/select project from saved project.",
        )
        projects_action = projects.add_subparsers(dest="action")

        projects_action.add_parser('auth',
                                   help='Authenticate and save the project.')
        projects_action.add_parser(
            'select', help='Select the project from saved projects.')
        projects_action.add_parser('list', help='List the saved projects.')

        projects_action.add_parser('help',
                                   help='Show this help message and exit.',
                                   add_help=False)

    def _add_asset_parser(self):
        """Asset level parser."""
        assets = self.subparsers.add_parser(
            "assets",
            help="Assets management.",
            description="datature assets - upload/group assets.",
        )
        assets_action = assets.add_subparsers(dest="action")

        assets_upload = assets_action.add_parser(
            'upload',
            help='Bulk update assets.',
        )
        assets_upload.add_argument("path",
                                   nargs='*',
                                   help='The asset path to upload.')
        assets_upload.add_argument("groups",
                                   nargs='*',
                                   help='The asset groups to upload.')

        assets_group = assets_action.add_parser(
            'groups',
            help='List assets group details.',
        )
        assets_group.add_argument("group",
                                  nargs='*',
                                  help='The asset group name.')

        assets_action.add_parser('help',
                                 help='Show this help message and exit.',
                                 add_help=False)

    def _add_annotation_parser(self):
        """Annotation level parser."""
        annotations = self.subparsers.add_parser(
            "annotations",
            help="Annotations management.",
            description="datature annotations - upload/download annotations.",
        )
        annotations_action = annotations.add_subparsers(dest="action")

        annotations_upload = annotations_action.add_parser(
            'upload',
            help='Bulk upload annotations from file.',
        )
        annotations_upload.add_argument("path",
                                        nargs='*',
                                        help='The annotations file path.')

        annotations_download = annotations_action.add_parser(
            'download',
            help='Bulk download annotations to file.',
        )
        annotations_download.add_argument("path",
                                          nargs='*',
                                          help='The annotations file path.')
        annotations_download.add_argument(
            "format", nargs='*', help='The annotations format to download.')

        annotations_action.add_parser('help',
                                      help='Show this help message and exit.',
                                      add_help=False)

    def _add_artifact_parser(self):
        """Artifact level parser."""
        artifacts = self.subparsers.add_parser(
            "artifacts",
            help="Artifacts management.",
            description="datature artifacts - download artifact models.",
        )
        artifacts_action = artifacts.add_subparsers(dest="action")

        artifacts_download = artifacts_action.add_parser(
            'download',
            help='Download artifact model.',
        )
        artifacts_download.add_argument("artifact_id",
                                        nargs='*',
                                        help='The id of the artifact.')
        artifacts_download.add_argument("format",
                                        nargs='*',
                                        help='The artifact model format.')

        artifacts_action.add_parser('help',
                                    help='Show this help message and exit.',
                                    add_help=False)

    def _add_help_parser(self):
        """Help level parser."""
        help_parser = self.subparsers.add_parser(
            "help",
            description="Show this help message and exit.",
        )
        help_action = help_parser.add_subparsers(dest="action")

        command_names = ["project", "asset", "annotation", "artifact"]
        for command_name in command_names:
            help_action.add_parser(command_name)

    def parse_args(self) -> ArgumentParser:
        """
        Parses and validates the CLI commands.

        :return: The parser to use.
        """
        args = self.parser.parse_args()

        if not args.command:
            self.print_help()
            sys.exit()

        return args

    def print_help(self, subparser: Optional[str] = None):
        """
        Prints the help information.

        : param subparser: The name of subparser.
        :return: None
        """
        parser = self.parser

        if subparser:
            parser = next(action.choices[subparser]
                          for action in parser._actions
                          if isinstance(action, _SubParsersAction)
                          and subparser in action.choices)

        parser.print_help()
