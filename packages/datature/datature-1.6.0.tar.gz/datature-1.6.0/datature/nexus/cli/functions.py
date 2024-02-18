#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
  ████
██    ██   Datature
  ██  ██   Powering Breakthrough AI
    ██

@File    :   functions.py
@Author  :   Raighne.Weng
@Version :   1.6.0
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   CLI functions
'''
# pylint: disable=E1102,R0912,C0103,R0914

import os
import re
import sys
import time
from pathlib import Path
from typing import Optional
from os.path import basename, exists, join, isdir

import inquirer
import requests
from halo import Halo
from alive_progress import alive_bar

from datature import nexus
from datature.nexus import error, config
from datature.nexus.utils import utils
from datature.nexus.cli import messages
from datature.nexus.cli.config import Config


def start_spinner(fn: callable):
    """ Start spinner for the function. """

    def wrapper(*args, **kwargs):
        wait_spinner = Halo(text=messages.REQUEST_SERVER_MESSAGE,
                            spinner='dots')
        wait_spinner.start()

        try:
            result = fn(*args, **kwargs)
            return result
        finally:
            wait_spinner.stop()

    return wrapper


def get_default_datature_client():
    """
    Get default datature client from configuration file.

    :return: The default datature client.
    """
    cli_config = Config()
    project = cli_config.get_default_project()

    if project is None:
        print(messages.NO_PROJECT_MESSAGE)
        sys.exit(1)

    return nexus.Client(project.get("project_secret")).get_project(
        project.get("project_id"))


@start_spinner
def sdk_list_project(secret_key: str):
    """ Retrieve project from server. """
    sdk_client = nexus.Client(secret_key)

    projects = sdk_client.list_projects()
    # Support to use workspace after one secret support multiple projects
    return projects


@start_spinner
def sdk_retrieve_project(project_secret: str, project_id: str):
    """ Retrieve project from server. """
    sdk_project = nexus.Client(project_secret)

    project = sdk_project.get_project(project_id)

    return project


@start_spinner
def sdk_create_upload_session():
    """ Retrieve project from server. """
    sdk_project = get_default_datature_client()

    import_session = sdk_project.annotations.create_import_session()

    return import_session


def sdk_retrieve_operation(op_id: str):
    """ Retrieve operation from server. """
    sdk_project = get_default_datature_client()

    operation = sdk_project.operations.get(op_id)
    return operation


def download_file_from_link(link: str, download_path: str):
    """
    Download file from link.

    :param link: The url link.
    :param download_path: The path to download file.
    :return: None
    """
    query_string_removed = link.split("?")[0]
    file_name = basename(query_string_removed)

    resp = requests.get(link, stream=True, timeout=120)

    total = int(resp.headers.get('content-length', 0))
    current_size = 0
    with open(join(download_path, file_name),
              'wb') as file, alive_bar(total,
                                       title='Downloading',
                                       title_length=12,
                                       manual=True) as progress_bar:
        for data in resp.iter_content(chunk_size=1024):
            size = file.write(data)
            current_size += size
            progress_bar(float(current_size / total))
        progress_bar(1.0)


def authenticate():
    """
    Authenticate the Workspace Secret with the server and creates a configuration file for it.

    :param secret_key: Secret key to use for the client login.
    :return: None
    """
    secret_key = inquirer.password(message="Enter the secret key")

    secret_key = secret_key.strip()
    if secret_key == "":
        print(messages.AUTHENTICATION_REMINDER_MESSAGE)
        sys.exit(1)

    try:
        projects = sdk_list_project(secret_key)

        project_name = inquirer.list_input(
            "Which project do you want to select?",
            choices=[project.get_info().name for project in projects],
        )

        for project in projects:
            if project.get_info().name == project_name:
                project_id = project.get_info().id

        default_project = inquirer.confirm(
            f"Make [{project_name}] the default project?", default=True)

        cli_config = Config()
        cli_config.set_project(project_id, project_name, secret_key,
                               default_project)

    except error.ForbiddenError:
        print(messages.INVALID_PROJECT_SECRET_MESSAGE)
        sys.exit(1)
    print(messages.AUTHENTICATION_MESSAGE)


def select_project():
    """
    Select project from saved configuration file.

    :return: None
    """
    cli_config = Config()
    project_names = cli_config.get_all_project_names()

    project_name = inquirer.list_input(
        "Which project do you want to select?",
        choices=project_names,
    )
    project = cli_config.get_project_by_name(project_name)

    cli_config.set_default_project(project.get("project_id"))
    print(f"{messages.ACTIVE_PROJECT_MESSAGE}: [{project_name}]")


def list_projects():
    """
    List projects from saved configuration file.

    :return: None
    """
    cli_config = Config()
    project_names = cli_config.get_all_project_names()
    default_project = cli_config.get_default_project()

    output = [[
        "NAME", "TOTAL_ASSETS", "ANNOTATED_ASSETS", "ANNOTATIONS", "TAGS"
    ]]
    for project_name in project_names:
        project = cli_config.get_project_by_name(project_name)
        try:
            project = sdk_retrieve_project(project.get("project_secret"),
                                           project.get("project_id"))
            project_info = project.get_info()

            total_assets = project_info.statistic.total_assets
            annotated_assets = project_info.statistic.annotated_assets
            total_annotations = project_info.statistic.total_annotations
            tags = project_info.tags

            output.append([
                project_name, total_assets, annotated_assets,
                total_annotations,
                len(tags)
            ])
        except error.ForbiddenError:
            print((
                f"\nProject {[project_name]} "
                "authentication failed, please use 'datature projects auth' again."
            ))
            sys.exit(1)
    print_table(output, 20)
    print(
        f"\n{messages.ACTIVE_PROJECT_MESSAGE}: [{default_project.get('project_name')}]"
    )


def cli_loop_operation(op_id: str, data_size: int):
    """
    Upload annotations from path.

    :param path: The annotation path to upload.
    :param annotation_format: The annotation format to upload.
    :return: None
    """
    # Custom manage loop
    with alive_bar(data_size, title='Processing', title_length=12,
                   manual=True) as progress_bar:
        while True:
            operation = sdk_retrieve_operation(op_id)

            if operation.status.overview == "Errored":
                print(messages.UNKNOWN_ERROR_MESSAGE)
                sys.exit(1)

            count = operation.status.progress.with_status

            queued = count.Queued
            running = count.Running
            finished = count.Finished
            cancelled = count.Cancelled
            errored = count.Errored
            percentage = float(
                (int(errored) + int(cancelled) + int(finished)) /
                (int(errored) + int(cancelled) + int(finished) + int(queued) +
                 int(running)))

            if percentage == 1:
                break

            progress_bar(percentage)
            time.sleep(config.OPERATION_LOOPING_DELAY_SECONDS)
        progress_bar(1.)
    print(messages.SERVER_COMPLETED_MESSAGE)


def upload_assets(path: Optional[Path] = None, groups: Optional[str] = None):
    """
    Upload assets from path.

    :param path: The folder to upload assets.
    :return: None
    """
    # check path if exist
    if not path:
        questions = [
            inquirer.Path("path_result",
                          message=messages.ASSETS_FOLDER_MESSAGE,
                          default=os.getcwd()),
        ]
        answer = inquirer.prompt(questions, raise_keyboard_interrupt=True)
        path = answer.get("path_result").strip()

    if not exists(path):
        print(messages.PATH_NOT_EXISTS_MESSAGE)
        sys.exit(1)

    # find all images under folder and sub folders
    file_paths = utils.find_all_assets(path)

    if len(file_paths) == 0:
        print(messages.NO_ASSETS_FOUND_MESSAGE)
        sys.exit(1)

    nifti_orientation = None
    if '.nii' in ",".join(str(file_path).lower() for file_path in file_paths):
        nifti_orientation = inquirer.text(
            messages.ASSETS_NIFTI_DIRECTION_CHOICE_MESSAGE,
            validate=lambda _, x: x in ["", "x", "y", "z"],
        )

    if not groups:
        groups_res = inquirer.text(
            messages.ASSETS_GROUPS_MESSAGE,
            default="main",
            validate=lambda _, x: re.match("^[A-Za-z0-9,]*$", x),
        )
        groups = [
            group.strip() for group in groups_res.split(',') if group.strip()
        ]

    confirm = inquirer.confirm(
        f"""{len(file_paths)} assets will be uploaded to group(s) ({
            ', '.join(groups)})?""",
        default=True)
    if not confirm:
        sys.exit(0)

    batch_size = config.ASSET_UPLOAD_SESSION_BATCH_SIZE

    num_batches = len(file_paths) // batch_size
    batches = [
        file_paths[i * batch_size:(i + 1) * batch_size]
        for i in range(num_batches)
    ]

    if len(file_paths) % batch_size != 0:
        batches.append(file_paths[num_batches * batch_size:])

    sdk_project = get_default_datature_client()
    # Loop Prepare asset metadata
    for _, batch in enumerate(batches):
        upload_session = sdk_project.assets.create_upload_session(
            groups=groups, background=True)

        with alive_bar(
                len(batch),
                title='Preparing',
                title_length=12,
        ) as progress_bar, upload_session as session:
            for file_path in batch:
                session.add_path(file_path,
                                 nifti_orientation=nifti_orientation)
                progress_bar()

        operations = upload_session.get_operation_ids()

        cli_loop_operation(operations[0], len(upload_session))


def upload_annotations(path: Optional[Path] = None):
    """
    Upload annotations from path.

    :param path: The annotation path to upload.
    :return: None
    """
    if not path:
        questions = [
            inquirer.Path("path_result",
                          message=messages.ANNOTATION_FOLDER_MESSAGE),
        ]
        answer = inquirer.prompt(questions, raise_keyboard_interrupt=True)
        path = answer.get("path_result").strip()

    # find all images under folder and sub folders
    if isdir(path):
        file_paths = utils.find_all_annotations_files(path)
    else:
        file_paths = [path]

    confirm = inquirer.confirm(
        f"""{len(file_paths)} files will be uploaded?""", default=True)
    if not confirm:
        sys.exit(0)

    batch_size = config.ANNOTATION_IMPORT_SESSION_BATCH_SIZE

    num_batches = len(file_paths) // batch_size
    batches = [
        file_paths[i * batch_size:(i + 1) * batch_size]
        for i in range(num_batches)
    ]

    if len(file_paths) % batch_size != 0:
        batches.append(file_paths[num_batches * batch_size:])

    # Loop Prepare asset metadata
    for _, batch in enumerate(batches):
        import_session = sdk_create_upload_session()

        with alive_bar(
                len(batch),
                title='Preparing',
                title_length=12,
        ) as progress_bar, import_session as session:
            for file_path in batch:
                progress_bar()

                session.add_path(file_path)

    print(messages.SERVER_COMPLETED_MESSAGE)


def download_artifact(artifact_id: Optional[str] = None,
                      model_format: Optional[str] = None,
                      path: Optional[str] = None):
    """
    Download artifact model.

    :param artifact_id: The id of the artifact.
    :param model_format: The artifact model to download.
    :param path: The path to download the model.
    :return: None
    """
    if not path:
        questions = [
            inquirer.Path("path_result",
                          message=messages.ARTIFACT_MODEL_FOLDER_MESSAGE,
                          default=os.getcwd()),
        ]
        answer = inquirer.prompt(questions, raise_keyboard_interrupt=True)
        path = answer.get("path_result").strip()

    if not exists(path):
        print(messages.PATH_NOT_EXISTS_MESSAGE)
        sys.exit(1)

    sdk_project = get_default_datature_client()

    if not artifact_id:
        # call server to list all artifacts
        artifacts = sdk_project.artifacts.list(include_exports=True)
        if len(artifacts) == 0:
            print(messages.NO_ARTIFACTS_MESSAGE)
            sys.exit(1)

        artifact_lists = []
        artifacts_key_map = {}
        for artifact in artifacts:
            key = (f"""{artifact.get('run_id')[-6:].upper()
                     }-{artifact.get('flow_title')}""")
            artifact_lists.append(key)
            artifacts_key_map[key] = artifact

        questions = [
            inquirer.List(
                "artifact",
                message=messages.ARTIFACT_DOWNLOAD_MESSAGE,
                choices=artifact_lists,
            ),
        ]
        answer = inquirer.prompt(questions, raise_keyboard_interrupt=True)
        artifact_key = answer.get("artifact")
        artifact = artifacts_key_map.get(artifact_key)

    if not model_format:
        questions = [
            inquirer.List(
                "model_format",
                message=messages.ARTIFACT_MODEL_FORMAT_DOWNLOAD_MESSAGE,
                choices=[option.format for option in artifact.export_options],
            ),
        ]
        answer = inquirer.prompt(questions, raise_keyboard_interrupt=True)
        model_format = answer.get("model_format")

    exported_formats = [export.format for export in artifact.exports]
    if model_format in exported_formats:
        # already exported, can download directly
        for model in artifact.exports:
            if model.format == model_format and model.status == "Finished":
                download_file_from_link(model.download.url, path)

    else:
        # not exported, need looping query download status
        # Loop to query status,
        wait_spinner = Halo(text=messages.EXPORT_ARTIFACT_WAITING_MESSAGE,
                            spinner='dots')
        wait_spinner.start()
        models = sdk_project.artifacts.create_export(artifact.id,
                                                     {"format": model_format})

        while True:
            models = sdk_project.artifacts.list_exported_models(
                artifact.get("id"))
            for model in models:
                if model.get("format") == model_format and model.get(
                        "status") == "Finished":
                    # start download
                    wait_spinner.stop()
                    download_file_from_link(model.download.url, path)

                    return

            time.sleep(config.OPERATION_LOOPING_DELAY_SECONDS)


def download_annotations(path: Optional[Path] = None,
                         annotation_format: Optional[str] = None):
    """
    Export annotations from path.

    :param path: The annotation path to export.
    :param annotation_format: The annotation format to export.
    :return: None
    """
    sdk_project = get_default_datature_client()
    if not path:
        questions = [
            inquirer.Path("path_result",
                          message=messages.EXPORT_ANNOTATION_FOLDER_MESSAGE,
                          default=os.getcwd()),
        ]
        answer = inquirer.prompt(questions, raise_keyboard_interrupt=True)
        path = answer.get("path_result").strip()

    if not exists(path):
        print(messages.PATH_NOT_EXISTS_MESSAGE)
        sys.exit(1)

    if not annotation_format:
        project = sdk_project.get_info()

        annotations_formats = utils.get_exportable_annotations_formats(
            project.type)
        questions = [
            inquirer.List(
                "annotation_format",
                message=messages.ANNOTATION_FORMAT_MESSAGE,
                choices=annotations_formats,
            ),
            inquirer.Text(
                "normalized",
                message=messages.DOWNLOAD_ANNOTATIONS_NORMALIZED_MESSAGE),
            inquirer.Text(
                "split_ratio",
                message=messages.DOWNLOAD_ANNOTATIONS_SPLIT_RATIO_MESSAGE,
                default=0.5,
                validate=lambda _, x: re.match(r'^(0(\.\d+)?|1(\.0+)?)$', x)),
        ]
        answer = inquirer.prompt(questions, raise_keyboard_interrupt=True)
        annotation_format = answer.get("annotation_format")
        normalized = answer.get("normalized") not in ["n", "N"]
        split_ratio = min(max(float(answer.get("split_ratio")), 0), 1)

    # Loop to query status,
    wait_spinner = Halo(text=messages.ANNOTATION_DOWNLOAD_MESSAGE,
                        spinner='dots')
    wait_spinner.start()
    operation = sdk_project.annotations.create_export({
        "format": "csv_fourcorner",
        "options": {
            "split_ratio": split_ratio,
            "seed": 1337,
            "normalized": normalized
        }
    })

    wait_spinner.stop()

    cli_loop_operation(operation.id, 1)

    sdk_project.annotations.download_exported_file(operation.id, path)

    print(messages.ANNOTATION_DOWNLOADED_MESSAGE)


def print_table(data: [[str]], column_width: int = 16):
    """
        List assets group statistics.

        :param data: The element array.
        :param column_width: The column widths and separator characters
        :return: None
        """
    # Print the table header
    print("".join(f"{item:{column_width}}" for _, item in enumerate(data[0])))

    # Print the table data
    for row in data[1:]:
        print("".join(f"{str(item):{column_width}}"
                      for _, item in enumerate(row)))


def assets_group(group: Optional[str] = None):
    """
    List assets group statistics.

    :param group: The name of group.
    :return: None
    """
    sdk_project = get_default_datature_client()

    if not group:
        project = sdk_project.get_info()

        groups = project.groups
        if groups is None or len(groups) == 0:
            print(messages.NO_ASSETS_GROUP_MESSAGE)
            sys.exit(1)

        group = inquirer.list_input(
            messages.CHOOSE_GROUP_MESSAGE,
            choices=groups,
        )

        statistics = sdk_project.assets.list_groups([group])
        statistic = statistics[0].statistic

        table = [[
            "NAME", "TOTAL", "ANNOTATED", "REVIEW", "TOFIX", "COMPLETED"
        ]]
        table.append([
            group, statistic.total_assets, statistic.annotated_assets,
            statistic.reviewed_assets, statistic.to_fixed_assets,
            statistic.completed_assets
        ])
        print_table(table)
