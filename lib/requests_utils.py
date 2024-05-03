# --*-- coding: utf-8 --*--
"""This module contains functions to send requests to the Nakala API"""

import sys
import ctypes
import os

import requests
from requests.exceptions import RequestException
import backoff

import json
import typer

from lib.constants import API_NAKALA_KEY, METADATA_AUTO
from lib.cli_utils import cli_log
from lib.io_utils import create_file_cur


def process_images_with_go(url, api_key, file_paths):
    so_file = os.path.join(os.path.dirname(__file__), "go_scripts/nakala_request.so")
    lib = ctypes.CDLL(so_file)

    lib.UploadFiles.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_char_p), ctypes.c_int]
    lib.UploadFiles.restype = ctypes.c_char_p

    url = f"{url}/datas/uploads"

    url_c = ctypes.c_char_p(url.encode('utf-8'))
    api_key_c = ctypes.c_char_p(api_key.encode('utf-8'))
    file_paths_c = (ctypes.c_char_p * len(file_paths))(*[p.encode('utf-8') for p in file_paths])

    response = lib.UploadFiles(url_c, api_key_c, file_paths_c, len(file_paths))
    json_response = response.decode('utf-8')

    result = json.loads(json_response)
    return result


@backoff.on_exception(backoff.expo, RequestException, max_time=60)
def post(endpoint: str,
         data: str = None,
         files: dict = None) -> dict:
    """Send a POST request to the Nakala API.

    :param endpoint: url to send the request
    :type endpoint: str
    :param data: data to send in the request (default: None)
    :type data: str, optional
    :param files: files to send in the request (default: None)
    :type files: dict, optional
    :return: response from the API
    :rtype: dict
    """
    headers = {
        "X-API-KEY": API_NAKALA_KEY,
        "accept": "application/json",
    }
    if files is not None:
        response = requests.post(endpoint, files=files, headers=headers)
    else:
        headers["Content-Type"] = "application/json"
        response = requests.post(endpoint, data=data, headers=headers)

    if response.status_code not in [200, 201]:
        if response.status_code == 401:
            typer.echo(cli_log("Unauthorized. Please check your credentials", "error", "noway"))
            sys.exit()

        else:
            typer.echo(cli_log("retrying with backoff...", "info", "retry"))
    return json.loads(response.text)


def initialize_data(url: str,
                    files: list,
                    metadata_config: dict) -> dict:
    """ Initialize data in Nakala (this process is activated at the end of image upload).

    :param url: url of the Nakala API (test or prod)
    :type url: str
    :param files: list of files already uploaded (with their sha1)
    :type files: list
    :param metadata_config: metadata configuration
    :type metadata_config: dict
    :return: response from the API (DOI of the data)
    :rtype: dict
    """
    try:
        metadata = {
            "status": metadata_config["data"]["status"],
            "files": files,
            "metas": [{**v, "propertyUri": k} for k, v in metadata_config["metadata"].items()]
        }

        if metadata_config["collectionsIds"]:
            metadata["collectionsIds"] = [metadata_config["collectionsIds"]]

        # Ajouter les métadonnées auto-générées
        metadata["metas"].extend(METADATA_AUTO)

        # Envoyer la requête POST pour créer les données
        handle_data = post(endpoint=f"{url}/datas", data=json.dumps(metadata))
        return handle_data
    except Exception as e:
        typer.echo(cli_log(f"Error: {e} - Cannot create data", "error", "error"))
        sys.exit(1)


def add_file(url: str,
             files: str) -> dict:
    """Add a file to Nakala.

    :param url: url of the Nakala API (test or prod)
    :type url: str
    :param files: list of files to add
    :type files: list
    :return: response from the API (sha1 of the file)
    :rtype: dict
    """
    image = create_file_cur(files)
    handle_sha1 = post(endpoint=f"{url}/datas/uploads", data=None, files=image)
    image['file'].close()
    try:
        handle_sha1['sha1']
    except KeyError:
        return {}
    return handle_sha1
