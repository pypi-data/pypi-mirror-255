#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
  ████
██    ██   Datature
  ██  ██   Powering Breakthrough AI
    ██

@File    :   base_processor.py
@Author  :   Raighne.Weng
@Version :   1.6.0
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Base Processor module
'''

from typing import List
from abc import ABC, abstractmethod


class BaseProcessor(ABC):
    """Base processor class"""

    @abstractmethod
    def valid(self, request_data):
        """Valid the input file if a valid file"""

    @abstractmethod
    def process(self, request_data) -> List[str]:
        """Function to process input file to assets"""
