import sys
from functools import lru_cache

import requests
from requests.exceptions import RequestException
import backoff

import json
import typer

from lib.constants import API_NAKALA_KEY, METADATA_AUTO
from lib.cli_utils import cli_log
from lib.io_utils import create_file_cur


@backoff.on_exception(backoff.expo, RequestException, max_time=60)
def post(endpoint, data, files=None):
    if files is not None:
        response = requests.post(endpoint, files=files, headers={
            "X-API-KEY": API_NAKALA_KEY,
            "accept": "application/json",
        })
    else:
        response = requests.post(endpoint, data=data, headers={
            "X-API-KEY": API_NAKALA_KEY,
            "accept": "application/json",
            "Content-Type": "application/json",
        })

    if response.status_code not in [200, 201]:
        if response.status_code == 401:
            typer.echo(cli_log("Unauthorized. Please check your credentials", "error", "noway"))
            sys.exit(1)
        else:
            typer.echo(cli_log("retrying with backoff...", "info", "retry"))
    return json.loads(response.text)


def intialize_data(url, files, metadata_config):
    try:
        metadata = {"status": metadata_config["data"]["status"],
                    "files": files,
                    "metas": [
                        {**v,
                         "propertyUri": k,
                         }
                        for k, v in metadata_config["metadata"].items()
                    ]}

        if metadata_config["collectionsIds"] != "":
            collectionsID = {"collectionsIds": [metadata_config["collectionsIds"]]}
            metadata.update(collectionsID)

        # add autogenerated metadata
        metadata["metas"] += METADATA_AUTO

        handle_data = post(endpoint=f"{url}/datas", data=json.dumps(metadata))
        return handle_data
    except Exception as e:
        typer.echo(cli_log(f"Error: {e} - Cannot create data", "error", "error"))
        sys.exit(1)


def add_file(url, files):
    image = create_file_cur(files)
    handle_sha1 = post(endpoint=f"{url}/datas/uploads", data=None, files=image)
    image['file'].close()
    try:
        handle_sha1['sha1']
    except:
        return {}
    return handle_sha1