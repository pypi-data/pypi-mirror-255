#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
  ████
██    ██   Datature
  ██  ██   Powering Breakthrough AI
    ██

@File    :   messages.py
@Author  :   Raighne.Weng
@Version :   1.6.0
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   collect all string messages variables
'''

REQUEST_SERVER_MESSAGE = "Communicating with server."
SERVER_COMPLETED_MESSAGE = "Server processing completed."
INVALID_PROJECT_SECRET_MESSAGE = (
    "\nInvalid project secret key, "
    "generate one for your project on nexus: Advanced/API Management")
AUTHENTICATION_MESSAGE = "Authentication succeeded."
AUTHENTICATION_REMINDER_MESSAGE = (
    "\nSecret Key needed, "
    "generate one for your project on nexus: Advanced/API Management")
NO_PROJECT_MESSAGE = "\nMissing authentication, please authenticate with 'datature projects auth'."
ASSETS_FOLDER_MESSAGE = 'Enter the assets folder path to be uploaded'
ASSETS_GROUPS_MESSAGE = "Enter the assets group name(s), split by ','"
ANNOTATION_FOLDER_MESSAGE = "Enter the annotation files path to be uploaded"
ANNOTATION_FORMAT_MESSAGE = "Select the annotation file format"
NO_ARTIFACTS_MESSAGE = "\nNo artifacts can be downloaded, please start a training first."
ARTIFACT_DOWNLOAD_MESSAGE = "Which artifact do you want to download?"
ARTIFACT_MODEL_FORMAT_DOWNLOAD_MESSAGE = "Which model format do you want to download?"
EXPORT_ARTIFACT_WAITING_MESSAGE = "Processing artifact for download, it may take 5-10 minutes.\n"
ARTIFACT_MODEL_FOLDER_MESSAGE = 'Enter the folder path to save model'
EXPORT_ANNOTATION_FOLDER_MESSAGE = "Enter the folder path to save annotation files"
CHOOSE_GROUP_MESSAGE = "Which asset group do you want to list?"
INVALID_PROJECT_MESSAGE = "\nInvalid project name."
PATH_NOT_EXISTS_MESSAGE = "\nPath does not exists."
NO_ASSETS_GROUP_MESSAGE = "\nNo asset groups exist in this project."
DOWNLOAD_ANNOTATIONS_NORMALIZED_MESSAGE = "Should the annotations be normalized? [Y/n]"
DOWNLOAD_ANNOTATIONS_SPLIT_RATIO_MESSAGE = "Enter the split ratio for this download. [0-1]"
INVALID_SPLIT_RATIO_MESSAGE = "\nInvalid split ratio."
AUTHENTICATION_FAILED_MESSAGE = "\nAuthentication failed, please use 'datature projects auth' again."
UNKNOWN_ERROR_SUPPORT_MESSAGE = "\nCommunication failed, contact support at support@datature.io."
CONNECTION_ERROR_MESSAGE = "\nConnection failed, please check your network."
UNKNOWN_ERROR_MESSAGE = "\nUnknown error occurred, contact support at support@datature.io."
ANNOTATION_DOWNLOAD_MESSAGE = "Processing annotations for download."
ANNOTATION_DOWNLOADED_MESSAGE = "Downloaded annotations."
ACTIVE_PROJECT_MESSAGE = "Your active project is now"
NO_ASSETS_FOUND_MESSAGE = "No allowable assets found in folders, please change the folder path."
ASSETS_NIFTI_DIRECTION_CHOICE_MESSAGE = (
    "Select the axis of orientation, "
    "if not provided, we will save videos for each axis. ['x','y','z']")
