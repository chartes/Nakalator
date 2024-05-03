# -*- coding: utf-8 -*-
"""This module contains I/O utilities functions"""

import yaml


def load_yaml(file: str) -> dict:
    """Load a YAML file and return its content as a dictionary

    :param file: path to the YAML file
    :type file: str
    :return: content of the YAML file
    :rtype: dict
    """
    return yaml.load(open(file, "r"), Loader=yaml.FullLoader)


def create_file_cur(image: str) -> dict:
    """Create a file object for a given image

    :param image: path to the image file
    :type image: str
    :return: file object
    :rtype: dict
    """
    file_open = open(image, "rb")
    return {"file": file_open}
