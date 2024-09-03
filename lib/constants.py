# -*- coding: utf-8 -*-
# Licence : MIT

"""constants.py

This module contains the constants used in the Nakalator project.
"""
import os
from datetime import datetime
from pathlib import Path

import yaml

from lib.utils.io_utils import load_yaml


base_dir_create = Path(os.getcwd()) / "nakalator_workspace"
data_dir_create = base_dir_create / "data"
metadatas_dir_create = base_dir_create / "metadatas"
output_dir_create = base_dir_create / "output"

data_dir = Path(os.getcwd()) / "data"
metadatas_dir = Path(os.getcwd()) / "metadatas"
output_dir = Path(os.getcwd()) / "output"

credentials_path = Path(os.getcwd()) / "credentials.yml"

try:
    credentials = load_yaml(str(credentials_path))
except yaml.YAMLError as exc:
    credentials = {}
except FileNotFoundError as exc:
    credentials = {}

try:
    API_NAKALA_KEY_TEST = credentials["API_NAKALA_KEY_TEST"]
    API_NAKALA_KEY_PROD = credentials["API_NAKALA_KEY_PROD"]
except KeyError as exc:
    API_NAKALA_KEY_TEST = ""
    API_NAKALA_KEY_PROD = ""

NAKALA_ROUTES = {
    "production": {
      "base_url": "https://nakala.fr",
      "api_url": "https://api.nakala.fr",
    },
    "test": {
      "base_url": "https://test.nakala.fr",
      "api_url": "https://apitest.nakala.fr",
    },
}

METADATA_AUTO = [
    {
        "value": "",
        "lang":"fr",
        "typeUri": "http://www.w3.org/2001/XMLSchema#string",
        "propertyUri": "http://nakala.fr/terms#creator"
    },
    {
        "value": datetime.now().strftime("%Y-%m-%d"),
        "typeUri": "http://www.w3.org/2001/XMLSchema#string",
        "propertyUri": "http://nakala.fr/terms#created"
    },
    {
        "value": "CC-BY-4.0",
        "typeUri": "http://www.w3.org/2001/XMLSchema#string",
        "propertyUri": "http://nakala.fr/terms#license"
    },
    {
        "value": "http://purl.org/coar/resource_type/c_c513",
        "lang": "",
        "typeUri": "http://www.w3.org/2001/XMLSchema#anyURI",
        "propertyUri": "http://nakala.fr/terms#type"
    },
    {
        "value": "École nationale des chartes - PSL",
        "lang": "fr",
        "typeUri": "http://www.w3.org/2001/XMLSchema#string",
        "propertyUri": "http://purl.org/dc/terms/publisher"
    },
]
