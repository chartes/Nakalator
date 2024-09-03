# -*- coding: utf-8 -*-
"""This module contains the NakalaAPIRequestBuilder class to build requests to the Nakala API."""

import requests
import sys
import time

from lib.constants import (
    NAKALA_ROUTES,
    API_NAKALA_KEY_PROD,
    API_NAKALA_KEY_TEST,
    METADATA_AUTO
)
from lib.utils.cli_utils import (
    cli_log,
    msg
)


class NakalaAPIRequestBuilder:
    """Class to build requests to the Nakala API.

    :param env: the environment to use (default: "test")
    :type env: str, optional
    """
    def __init__(self,
                 env: str = "test"):
        """Initialize the NakalaAPIRequestBuilder class.
        :attr _api_key: the API key to use
        :type _api_key: str
        :attr _headers: the headers to use
        :type _headers: dict
        :attr _base_url: the base URL to use
        :type _base_url: str
        :attr _api_url: the API URL to use
        :type _api_url: str
        """
        self._api_key = API_NAKALA_KEY_PROD if env == "production" else API_NAKALA_KEY_TEST
        self._headers = {
            "X-API-KEY": self._api_key,
            "accept": "application/json"
        }
        self._base_url, self._api_url = NAKALA_ROUTES[env].values()


    @staticmethod
    def prepare_payload_collection(collection_meta_from_user: dict = None) -> dict:
        """Prepare the payload for the collection creation.
        :param collection_meta_from_user: the metadata from the user
        :type collection_meta_from_user: dict, optional
        :return: the payload for the collection creation
        :rtype: dict
        """
        if collection_meta_from_user is None:
            collection_meta_from_user = {}
        return {
            "status": collection_meta_from_user["collectionStatus"],
            "metas": [{
                "propertyUri": "http://nakala.fr/terms#title",
                "value": collection_meta_from_user["collectionTitle"],
                "lang": "fr",
                "typeUri": "http://www.w3.org/2001/XMLSchema#string"
            },
                {
                    "propertyUri": "http://purl.org/dc/terms/description",
                    "value": collection_meta_from_user["collectionDescription"],
                    "lang": "fr",
                    "typeUri": "http://www.w3.org/2001/XMLSchema#string"
                },
            ],
            "datas": [],
            "rights": []

        }


    @staticmethod
    def prepare_payload_data(metadata_config: dict, files: list) -> dict:
        """Prepare the payload for the data creation.
        :param metadata_config: the metadata configuration
        :type metadata_config: dict
        :param files: list of files already uploaded (with their sha1)
        :type files: list
        :return: the payload for the data creation
        :rtype: dict
        """
        try:
            metadata_config = dict(metadata_config)
            metadata = {
                "status": metadata_config["data"]["status"],
                "files": files,
                "metas": [{**v, "propertyUri": k} for k, v in metadata_config["metadata"].items() if
                          k != "http://nakala.fr/terms#creator"]
            }


            property_uris = [dic["propertyUri"] for dic in METADATA_AUTO]

            for k, v in metadata_config["metadata"].items():
                if k in property_uris:
                    for dic in METADATA_AUTO:
                        if dic["propertyUri"] == k:
                            METADATA_AUTO.remove(dic)

            if "http://nakala.fr/terms#creator" in metadata_config["metadata"].keys():
                # TODO: test if the creator is an ORCID
                metadata_config["metadata"]["http://nakala.fr/terms#creator"]["value"]["orcid"] = ""
                creator = {
                    "value": metadata_config["metadata"]["http://nakala.fr/terms#creator"]["value"],
                    "propertyUri": "http://nakala.fr/terms#creator",
                }
                metadata["metas"].append(creator)


            if metadata_config["collectionIds"] not in ["", None]:
                metadata["collectionsIds"] = [metadata_config["collectionIds"]]

            # Ajouter les métadonnées auto-générées
            metadata["metas"].extend(METADATA_AUTO)

            return metadata
        except Exception as e:
            cli_log(f"Error: {e} - Cannot create data", "error")
            sys.exit(1)


    def post_builder(self, endpoint: str, data: dict, files: dict = None) -> requests.Response:
        """Build a POST request to the Nakala API.
        :param endpoint: the endpoint to use
        :type endpoint: str
        :param data: the data to send
        :type data: dict
        :param files: the files to send
        :type files: dict
        :return: the response from the API
        :rtype: requests.Response
        """
        return requests.post(
            f"{self._api_url}/{endpoint}",
            json=data,
            files=files,
            headers=self._headers
        )

    def get_builder(self, endpoint: str) -> requests.Response:
        """Build a GET request to the Nakala API.
        :param endpoint: the endpoint to use
        :type endpoint: str
        :return: the response from the API
        :rtype: requests.Response
        """
        return requests.get(
            f"{self._api_url}/{endpoint}",
            headers=self._headers
        )

    def initialize_nakala_data(self, sha1s: list, metadata_config: dict = None) -> str:
        """Initialize the data creation on Nakala.
        :param sha1s: list of sha1s
        :type sha1s: list
        :param metadata_config: the metadata configuration
        :type metadata_config: dict
        :return: the DOI of the data
        :rtype: str
        """
        if metadata_config is None:
            metadata_config = {}
        data_payload = self.prepare_payload_data(metadata_config=metadata_config,
                                                 files=sha1s)
        handle_data = self.post_builder("datas",
                                        data=data_payload,
                                        files=None)
        if handle_data.status_code == 201:
            return handle_data.json()['payload']['id']
        else:
            cli_log(f"Error when creating data: {handle_data.status_code} - {handle_data.text}", "error")
            cli_log("Goodbye! check and try again.", "info")
            sys.exit(1)

    def initialize_nakala_collection(self, collection_meta_from_user: dict = None) -> tuple:
        """Initialize the collection creation on Nakala.

        :param collection_meta_from_user: the metadata from the user
        :type collection_meta_from_user: dict, optional
        :return: the title and the DOI of the collection
        :rtype: tuple
        """
        if collection_meta_from_user is None:
            collection_meta_from_user = {}
        with msg.loading(f"Creating collection: '{collection_meta_from_user['collectionTitle']}'..."):
            time.sleep(1)
            payload = self.prepare_payload_collection(collection_meta_from_user)
            response = self.post_builder("collections", data=payload, files=None)
        if response.status_code == 201:
            return collection_meta_from_user['collectionTitle'], response.json()['payload']['id']
        else:
            cli_log(f"Error when creating collection: '{collection_meta_from_user['collectionTitle']}'"
                    f": {response.status_code} - {response.text}", "error")
            cli_log("Goodbye! check and try again.", "info")
            sys.exit(1)

    def check_data_files_exist(self, data_id: str) -> list:
        response = self.get_builder(f"datas/{data_id}")
        if response.status_code == 200:
            return response.json()['files']
        else:
            return []

    def check_nakala_collection_exists(self, collection_id: str) -> str:
        """Check if a collection exists on Nakala.

        :param collection_id: the ID of the collection
        :type collection_id: str
        :return: the title of the collection
        :rtype: str
        """
        with msg.loading(f"Checking on Nakala for {collection_id}..."):
            time.sleep(1)
            response = self.get_builder(f"collections/{collection_id}")
        if response.status_code == 200:
            return response.json()['metas'][0]['value']
        else:
            if response.status_code == 404:
                cli_log(f"Error: Collection with id: '{collection_id}' not found on Nakala", "error")
            else:
                cli_log(f"Error: {response.status_code} - {response.text}", "error")
            sys.exit(1)
