#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
  ████
██    ██   Datature
  ██  ██   Powering Breakthrough AI
    ██

@File    :   upload.py
@Author  :   Raighne.Weng
@Version :   1.6.0
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Upload python SDK documentation to readme
'''

import os
import re

README_API_KEY = os.getenv("README_API_KEY")

documentations = [
    "project", "asset", "tag", "annotation", "workflow", "run", "artifact",
    "deploy", "operation"
]

# pylint: disable=C0103
for documentation in documentations:
    page_slug = f"{documentation}-sdk-functions"
    markdown_path = os.path.join(f"build/markdown/datature_{documentation}.md")

    # Read Document to do some simple change
    with open(markdown_path, "r", encoding="utf8") as rd:
        md = rd.read().splitlines(True)
        md = "".join(md[1:])

        md = md.replace("### _class_", "# _class_")
        md = md.replace("#### _classmethod_", "## _classmethod_")
        md = md.replace("* **Returns**", "### Return")
        md = md.replace("* **Example**", "### Example")
        md = md.replace(
            "* **Parameters**",
            "### Parameters\n| Name | Description |\n| --- | --- |")
        md = md.replace("    A dictionary", "A dictionary")
        md = md.replace("    ```", "```")
        md = md.replace("```json", "```Text json")
        md = md.replace("    **", "**")
        md = md.replace("    * **", "**")
        md = md.replace("datature.sdk.api.types.", "")
        md = md.replace("datature_types.md#", "types-sdk-functions#")

    with open(markdown_path, "w", encoding="utf8") as wr:
        wr.write(md)

    # Read lines to change * **Parameters** to headers
    with open(markdown_path, "r", encoding="utf8") as rd:
        lines = rd.readlines()

    lines = list(filter(lambda x: x.strip() != "", lines))

    pattern = re.compile(r'\*\*\s*(\w+)\s*\*\*\s*–\s*(.*)$')
    for i, line in enumerate(lines):
        match = pattern.match(line.strip())
        if match:
            lines[i] = f'| {match.group(1)} | {match.group(2)} |\n'

    with open(markdown_path, "w", encoding="utf8") as wr:
        wr.write(''.join(lines))
