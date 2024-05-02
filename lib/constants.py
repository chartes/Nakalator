import os
from datetime import datetime

from lib.io_utils import load_yaml

credentials = os.path.join(os.path.dirname(__file__), "..", "credentials.yml")

data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
metadatas_dir = os.path.join(os.path.dirname(__file__), "..", "metadatas")
output_dir = os.path.join(os.path.dirname(__file__), "..", "output")
API_NAKALA_KEY = load_yaml(credentials)["API_NAKALA_KEY"]

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
        "value": "CC-BY-SA-4.0",
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
        "value": "École nationale des chartes",
        "lang": "fr",
        "typeUri": "http://www.w3.org/2001/XMLSchema#string",
        "propertyUri": "http://purl.org/dc/terms/publisher"
    },
]
