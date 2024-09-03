# -*- coding: utf-8 -*-

"""io_utils.py
This module contains I/O utilities functions.
"""
import os
from dataclasses import (dataclass,
                         asdict)
from typing import Union

import pandas as pd
import yaml

# Custom sort function for files
custom_sort = lambda file: (0, file) if 'prev' in file.lower() else (2, file) if 'next' in file.lower() else (1, file)

class DoubleQuotedStr(str):
    pass

def double_quoted_str_representer(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='"')

yaml.add_representer(DoubleQuotedStr, double_quoted_str_representer)

@dataclass
class NakalaItem:
    """Dataclass to store Nakala item information."""
    original_name: Union[str, None] = None
    collection_doi: Union[str, None] = None
    data_doi: Union[str, None] = None
    sha1: Union[str, None] = None

    @classmethod
    def to_csv(cls, name, items, output_dir):
        pd.DataFrame([asdict(item) for item in items]).to_csv(
            os.path.join(output_dir, name),
            encoding="utf-8",
            index=True,
            sep=";")
        return

def load_yaml(file: str) -> dict:
    """Load a YAML file and return its content as a dictionary.

    :param file: path to the YAML file
    :type file: str
    :return: content of the YAML file
    :rtype: dict
    """
    return yaml.load(open(file, "r"), Loader=yaml.FullLoader)


def write_yaml(yml_path: str,
               yml_out: str) -> None:
    """Write a YAML string to a file.

    :param yml_path: path to the output YAML file
    :type yml_path: str
    :param yml_out: YAML string to write
    :type yml_out: str
    :return: None
    :rtype: None
    """
    with open(yml_path, "w") as f:
        f.write(yml_out)

def rewrite_metadata_config_with_collection_ids(metadata_config: dict,
                                                metadata_path: str) -> None:
    """Rewrite the metadata configuration with the collection DOI.
    :param metadata_config: the metadata configuration
    :type metadata_config: dict
    :param metadata_path: the path to the metadata file
    :type metadata_path: str
    :return: None
    :rtype: None
    """
    # Convert all string values to DoubleQuotedStr
    def convert_to_double_quoted(value):
        if isinstance(value, dict):
            return {k: convert_to_double_quoted(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [convert_to_double_quoted(v) for v in value]
        elif isinstance(value, str):
            return DoubleQuotedStr(value)
        else:
            return value

    metadata_config = convert_to_double_quoted(metadata_config)

    with open(metadata_path, 'w', encoding='utf-8') as file:
        yaml.dump(metadata_config, file, allow_unicode=True, default_flow_style=False, sort_keys=False)

def load_csv(file: str) -> pd.DataFrame:
    """Load a CSV file and return its content as a DataFrame.

    :param file: path to the CSV file
    :type file: str
    :return: content of the CSV file
    :rtype: pd.DataFrame
    """
    return pd.read_csv(file, sep=";")

def merge_df_reports(sorted_reports: list, collection_doi: str, output_dir: str, remove: bool = False) -> None:
    """Merge the reports into a single CSV file.
    :param sorted_reports: a list of reports to merge
    :type sorted_reports: list
    :param collection_doi: the DOI of the collection
    :type collection_doi: str
    :param output_dir: the output directory to save the merged CSV file
    :type output_dir: str
    :return: None
    :rtype: None
    """
    df = None
    for report in sorted_reports:
        if report == sorted_reports[0]:
            df = load_csv(os.path.join(output_dir, report))
        else:
            df = pd.concat([df, pd.read_csv(os.path.join(output_dir, report), sep=";")])
        if remove:
            os.remove(os.path.join(output_dir, report))
    df.to_csv(os.path.join(output_dir, f"merge_{collection_doi}_mapping_ids_all.csv"), sep="\t", index=False)


