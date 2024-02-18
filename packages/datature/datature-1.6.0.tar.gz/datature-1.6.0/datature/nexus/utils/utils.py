#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
  ████
██    ██   Datature
  ██  ██   Powering Breakthrough AI
    ██

@File    :   utils.py
@Author  :   Raighne.Weng
@Version :   1.6.0
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Utils Class module
'''

import os
import glob
import tempfile
from typing import Union
from pathlib import Path

from requests import Session, request
from requests.adapters import HTTPAdapter, Retry

from datature.nexus import models, config

SUPPORTED_MRI_EXTENSIONS = ["*.dcm", "*.DCM", '*.nii', '*.NII']

SUPPORTED_IMAGE_VIDEO_EXTENSIONS = [
    '*.jpg',
    '*.JPG',
    '*.png',
    '*.PNG',
    '*.jpeg',
    '*.JPEG',
    '*.mp4',
    '*.MP4',
]

SUPPORTED_FILE_EXTENSIONS = SUPPORTED_MRI_EXTENSIONS + \
    SUPPORTED_IMAGE_VIDEO_EXTENSIONS

ANNOTATION_FORMAT_EXTENSIONS = [
    "*.json", "*.csv", "*.xml", "*.labels", "*.txt"
]


def find_all_assets(path: str) -> [str]:
    """
    List all assets under folder, include sub folder.

    :param path: The folder to upload assets.
    :return: assets path list.
    """
    file_paths = []

    # find all assets under folder and sub folders
    for file_ext in SUPPORTED_FILE_EXTENSIONS:
        file_paths.extend(
            glob.glob(os.path.join(path, '**', file_ext), recursive=True))

    return file_paths


def find_all_annotations_files(path: str) -> [str]:
    """
    List all annotations files under folder, include sub folder.

    :param path: The folder to upload annotations files.
    :return: assets path list.
    """
    file_paths = []

    # find all assets under folder and sub folders
    for file_ext in ANNOTATION_FORMAT_EXTENSIONS:
        file_paths.extend(
            glob.glob(os.path.join(path, '**', file_ext), recursive=True))

    return file_paths


def get_exportable_annotations_formats(project_type: str) -> [str]:
    """
    Get the exported annotations formats by project type.

    :param project_type: The type of the project.
    :return: The exported annotations formats.
    """
    if project_type == "Classification":
        return ["csv_classification", "classification_tfrecord"]

    if project_type == "Keypoint":
        return ["keypoints_coco"]

    return [
        "coco", "csv_fourcorner", "csv_widthheight", "pascal_voc",
        "yolo_darknet", "yolo_keras_pytorch", "createml", "tfrecord",
        "polygon_single", "polygon_coco"
    ]


def init_gcs_upload_session():
    """
    Initializes an HTTP session for uploading files to 
        Google Cloud Storage (GCS) with a configured retry policy.

    The retry policy is configured to retry up to 5 times on specific 
        HTTP status codes (500, 502, 503, 504) that commonly represent 
        transient server errors. A backoff factor is used to introduce 
        a delay between retry attempts.

    Returns:
        Session: A requests Session object configured with the retry policy.
    """
    # Define the retry policy
    retries = Retry(total=5,
                    backoff_factor=0.1,
                    status_forcelist=[500, 502, 503, 504])

    http_session = Session()
    # Mount the retry policy for HTTP and HTTPS requests
    http_session.mount("http://", HTTPAdapter(max_retries=retries))
    http_session.mount("https://", HTTPAdapter(max_retries=retries))

    return http_session


def get_download_path(path: Union[str, Path] = None) -> Path:
    """
    Gets the download path for storing files. 
        If the provided path does not exist, it creates the directory.

    Args:
        path (Union[str, Path], optional): 
            The path where files should be downloaded or stored. 
            It can be a string or a Path object. If None, the current working directory is used.

    Returns:
        Path: The resolved download path as a Path object.
    """
    if path:
        # Check if path is a string and convert it to a Path object if necessary
        download_path = Path(path) if isinstance(path, str) else path

        # Create the directory if it doesn't exist
        download_path.mkdir(parents=True, exist_ok=True)
    else:
        # If path is None, use the current working directory
        download_path = Path.cwd()

    return download_path


def download_files_to_tempfile(signed_url: models.DownloadSignedUrl) -> str:
    """
    Downloads a file from a signed URL to a temporary file.

    Args:
        signed_url (models.DownloadSignedUrl): 
            An object containing the signed URL and the HTTP method for the request.

    Returns:
        Path: The path to the downloaded temporary file.

    Raises:
        requests.RequestException: If there is an issue with making the request.
    """
    method = signed_url.method
    url = signed_url.url

    resp = request(method,
                   url,
                   stream=True,
                   timeout=config.REQUEST_TIME_OUT_SECONDS)

    # Download the file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        for data in resp.iter_content(chunk_size=1024):
            temp_file.write(data)

    return temp_file.name
