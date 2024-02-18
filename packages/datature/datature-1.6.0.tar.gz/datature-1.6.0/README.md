<div align="center">

# :hammer: Datature Python SDK :hammer:

[![Python - Version](https://img.shields.io/pypi/pyversions/datature?label=Python)](https://pypi.org/project/datature)
[![PyPI - Version](https://img.shields.io/pypi/v/datature?label=Pypi%20Package)](https://pypi.org/project/datature)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/datature?label=Pypi%20Downloads)](https://pypi.org/project/datature)

[![Join Datature Slack](https://img.shields.io/badge/Join%20The%20Community-Datature%20Slack-blueviolet?style=plastic)](https://datature.io/community) [![MIT license](https://img.shields.io/badge/License-Apache%202.0-blue.svg?style=plastic)](https://lbesson.apache-license.org/)

<a href="https://datature.io">
    <img
      src="assets/datature.svg"
      width="3%"
    />
</a>
<img src="assets/transparent.png" width="3%"/>
<a href="https://www.datature.io/blog">
    <img
      src="assets/blog.svg"
      width="3%"
    />
</a>
<img src="assets/transparent.png" width="3%"/>
<a href="https://developers.datature.io/">
    <img
      src="https://cdn.simpleicons.org/readme/#018EF5"
      width="3%"
    />
</a>
<img src="assets/transparent.png" width="3%"/>
<a href="https://www.youtube.com/channel/UCd3UQZ9piasi0vgfg5xI59w">
    <img
      src="https://cdn.simpleicons.org/youtube/#FF0000"
      width="3%"
    />
</a>
<img src="assets/transparent.png" width="3%"/>
<a href="https://www.linkedin.com/company/datature/">
    <img
      src="https://cdn.simpleicons.org/linkedin/#0A66C2"
      width="3%"
    />
</a>
<img src="assets/transparent.png" width="3%"/>
<a href="https://twitter.com/DatatureAI">
    <img
      src="https://cdn.simpleicons.org/twitter/#1D9BF0"
      width="3%"
    />
</a>
<img src="assets/transparent.png" width="3%"/>
<a href="https://datature.io/community">
    <img
      src="assets/slack.png"
      width="3%"
    />
</a>

---

:zap: Empower your MLOps pipelines and applications with seamless integrations :zap:

Automate tasks to manage your datasets, run training experiments, export and deploy your models from [Datature Nexus](https://www.datature.io/nexus?utm_source=github) with ease. Perform development via [Python scripts](#python-usage) or with the [CLI](#cli-usage) - your choice!

</div>

---

<div align="center">

## :rocket: Getting Started :rocket:

</div>

## :snake: Prerequisites

- `3.8` <= Python <= `3.12`

We recommend users to create a virtual environment before installing any dependencies. For more information on virtual environments, please refer to:

- [Python venv](https://docs.python.org/3/tutorial/venv.html)
- [Conda](https://conda.io/projects/conda/en/stable/user-guide/install/index.html)
- [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/)

## :gear: Installation

```sh
pip install --upgrade datature
```

---

## Python Usage

For a full list of documentation and examples, please refer to the [API docs](https://developers.datature.io/docs/python-sdk).

### Authentication

To get started, you will first need to create a project on [Datature Nexus](https://www.datature.io/nexus?utm_source=github) (signing up is free!). You will then need to locate the [project secret key](https://developers.datature.io/v1.0.0/docs/hub-and-api). This key can only be accessed if you are the Project Owner or been granted elevated permissions by the Project Owner, and will be used for all subsequent authentication when invoking the various SDK functions.

### Examples

To list projects:

```python
from datature import nexus

client = nexus.Client("3736971xxxxx")

projects = client.list_projects()
```

To upload assets:

```python
import os
from datature import nexus

logging.basicConfig()

client = nexus.Client("3736971xxxxx")

project = client.list_projects("proj_xxxxx")


upload_session = project.assets.create_upload_session(groups=["dataset"])

with upload_session as session:
  session.add_path("/Users/dataset")

print(len(upload_session))
```

### Logging

You can vary the logging level depending on your task or use case (such as `DEBUG` to provide more insights), but the default `INFO` level is typically best suited for production use.

```python
import logging

logging.basicConfig()
logging.getLogger("nexus").setLevel(logging.DEBUG)
```

---

## CLI Usage

For a full list of documentation and examples, please refer to the [CLI docs](https://developers.datature.io/docs/cli).

### Authentication

To get started, you will first need to create a project on [Datature Nexus](https://www.datature.io/nexus?utm_source=github) (signing up is free!). You will then need to locate the [project secret key](https://developers.datature.io/v1.0.0/docs/hub-and-api). This key can only be accessed if you are the Project Owner or been granted elevated permissions by the Project Owner, and will be used for all subsequent authentication when invoking the various SDK functions.

Once you have the project secret, you will now be able to make API requests using the CLI by entering the command `datature projects auth`:

```bash
datature projects auth
[?] Enter the project secret: ************************************************
[?] Make [Your Project Name] the default project? (Y/n): y

Authentication succeeded.
```

You will now be able to run your desired CLI commands as outlined above. To see all possible functions as well as view the required inputs and expected outputs, check out the following documentation.

### Project Management

`datature projects`

Show a help page of various functions to add projects, select the default project, and retrieve project information.

#### Auth Project

`datature projects auth`

Authenticate new projects using the [project secret key](https://developers.datature.io/v2.0.0/docs/hub-and-api). Multiple projects can be authenticated and stored using different secret keys.

#### Select Project

`datature projects select`

Select an active project to work on from a list of saved projects. All subsequent CLI commands will be in the context of the selected project until a different project is selected, or the shell session is terminated.

```bash
$ datature projects select

> My Cool Project
  New Test Project

Your active project is now: [Dicom]
```

#### List Projects

`datature projects list`

View a table of saved projects with columns containing the names of the projects, the total number of assets, the number of annotated assets, the number of annotations, and the number of tags for each project. The name of the active project is displayed at the bottom of the list.

```bash
$ datature projects list

NAME                TOTAL_ASSETS        ANNOTATED_ASSETS    ANNOTATIONS         TAGS
My Cool Project     4071                433                 1874                3
New Test Project    718                 53                  959                 4

Your active project is now: [My Cool Project]
```

### Asset Management

#### Upload Assets

`datature assets upload`

Upload assets to [Datature Nexus](https://www.datature.io/nexus?utm_source=github). You will be prompted to enter the path to the folder containing the assets that you wish to upload, as well as optional group name(s) to categorize the set of assets. This function is designed specially for bulk uploading of large datasets, which accelerates the process of onboarding data for subsequent annotation and training.

This function also supports DICOM and NIfTI file upload, which caters to important medical use cases.

```bash
$ datature asset upload
[?] Enter the assets folder path to be uploaded: /Downloads/Training2
[?] Enter the assets group name(s), split by ',': main
[?] 281 assets will be uploaded to group(s) (main)? (Y/n):
Preparing    |████████████████████████████████████████| 281/281 [100%] in 0.1s (2775.28/s)
Processing   |████████████████████████████████████████| 100% [281/281] in 1:17.5 (3.56/s)
Server processing completed.
```

#### Group Assets

`datature assets groups`

List asset group information within your project. You will be prompted to select an existing group or create a new group. If you select an existing group, information about the selected group will be displayed, including the total number of assets in the group, the number of assets that have been annotated, reviewed, or marked for fixes, and the number of assets that have been completed.

```bash
$ datature assets groups

> main
  groupName2

NAME            TOTAL           ANNOTATED       REVIEW          TOFIX           COMPLETED
main            8               1               0               0               0
```

### Annotation Management

#### Upload Annotations

`datature annotations upload`

Upload annotation files to [Datature Nexus](https://www.datature.io/nexus?utm_source=github) You will be prompted to enter the path of the annotation file you wish to upload and select a [supported annotation format](https://developers.datature.io/docs/uploading-annotations#supported-annotation-formats).

```bash
$ datature annotations upload
[?] Enter the annotation files path to be uploaded: /Users/Downloads/Training.csv
Processing   |████████████████████████████████████████| 100% [1/1] in 7.0s (0.14/s)
Server processing completed.
```

#### Download Annotations

`datature annotations download`

Download annotation files from [Datature Nexus](https://www.datature.io/nexus?utm_source=github). You will be prompted to enter a path to save the downloaded annotation file to, and select the desired [annotation format](https://developers.datature.io/docs/uploading-annotations#supported-annotation-formats).

```bash
$ datature annotations download
[?] Enter the annotation files path to be download: /Users/Downloads/
[?] Select the annotation file format: csv_widthheight
   csv_fourcorner
 > csv_widthheight
   coco
   pascal_voc
   yolo_keras_pytorch
   yolo_darknet
   polygon_single
   polygon_coco

Processing   |████████████████████████████████████████| 100% [1/1] in 7.0s (0.14/s)
Server processing completed.
```

### Artifact Management

#### Artifact Download

`datature artifacts download`

Download a model artifact from [Datature Nexus](https://www.datature.io/nexus?utm_source=github). You will be prompted to enter a folder path to save the model to, and select the name and [export format](https://developers.datature.io/docs/export-formats) of the artifact to download.

```bash
$ datature artifacts download
[?] Enter the folder path to save model: /Volumes/
[?] Which artifact do you want to download?: BEAF45-Workflowc
 > BEAF45-Workflowc

[?] Which model format do you want to download?: tensorflow
 > tensorflow
   tflite
   onnx

Downloading  |████████████████████████████████████████| 100% [443421394/443421394] in 7.1s (62639992.12/s)
```
