#!/usr/bin/env python3
# -- coding: utf-8 --

"""Nakalator
Script to upload data to Nakala.

Last update: 2024
"""
import os
from typing import Union
import sys
from dataclasses import dataclass, asdict
import datetime
from time import sleep, time
from concurrent.futures import ThreadPoolExecutor
import json

import typer
from tqdm import tqdm

import pandas as pd

import requests

from lib.constants import (NAKALA_ROUTES,
                           data_dir,
                           metadatas_dir,
                           output_dir,
                           API_NAKALA_KEY)
from lib.io_utils import (load_yaml)
from lib.cli_utils import (cli_log,
                           banner,
                           valid_method,
                           prompt_select,
                           prompt_confirm)
from lib.requests_utils import (add_file,
                                initialize_data,
                                process_images_with_go)
from lib.tests import (
    __check_total_images,
    __check_order_images,
    __check_sha1_consistency
)


@dataclass
class NakalaItem:
    original_name: Union[str, None] = None
    collection_doi: Union[str, None] = None
    data_doi: Union[str, None] = None
    sha1: Union[str, None] = None

    @classmethod
    def to_csv(cls, name, items):
        pd.DataFrame([asdict(item) for item in items]).to_csv(
            os.path.join(output_dir, name),
            encoding="utf-8",
            index=True,
            sep=";")
        return


def process(components, images, api_url, method, progress=None):
    sha1s = []
    results_objects = []
    empty_sha1 = []
    if method in ["hard", "soft"]:
        for i, item in enumerate(components):
            handle_sha1 = item.result() if method == "hard" else add_file(api_url, item)
            if handle_sha1 != {}:
                sha1s.append(handle_sha1)
                results_objects.append(NakalaItem(sha1=handle_sha1['sha1'], original_name=handle_sha1['name']))
            else:
                empty_sha1.append(images[i])
            progress.set_description(f"Processing {os.path.basename(images[i])}...")
            progress.update(1)

    return sha1s, results_objects, empty_sha1


def work_with_accumulator(images, method, api_url):
    def process_images(images_to_process, accumulated_results=None, accumulated_sha1s=None,
                       accumulated_empty_sha1s=None):
        if accumulated_results is None:
            accumulated_results = []
        if accumulated_sha1s is None:
            accumulated_sha1s = []
        if accumulated_empty_sha1s is None:
            accumulated_empty_sha1s = []

        if method in ["hard", "soft"]:
            with tqdm(total=len(images_to_process)) as progress:
                if method.lower() == "hard":
                    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
                        sha1s, results_objects, empty_sha1s = process(
                        components=[executor.submit(add_file, api_url, img_cur) for img_cur in images_to_process],
                        images=images,
                        api_url=api_url,
                        method=method,
                        progress=progress)
                if method.lower() == "soft":
                    sha1s, results_objects, empty_sha1s = process(components=images_to_process,
                                                              images=images,
                                                              api_url=api_url,
                                                              method=method,
                                                              progress=progress)

        accumulated_results.extend(results_objects)
        accumulated_sha1s.extend(sha1s)
        accumulated_empty_sha1s.extend(empty_sha1s)

        if empty_sha1s:
            typer.echo(
                cli_log(f"Retry for {len(empty_sha1s)} failed uploads. Please wait 5 seconds before started new loop..",
                        "warning", "timer"))
            sleep(5)
            process_images([image for image in empty_sha1s],
                           accumulated_results,
                           accumulated_sha1s,
                           [])

        return accumulated_sha1s, accumulated_results, accumulated_empty_sha1s

    return process_images(images)


app = typer.Typer()


@app.command()
def main(method: str = typer.Option("soft", "--method", "-m", help="Method to send data to Nakala: 'hard' | 'soft'")):
    banner()
    valid_method(method)
    # select an environment: test or production
    environment = prompt_select("Which Nakala environment do you want to use to send your data?",
                                choices=['test', 'production'],
                                default="test"
                                )
    # select a metadata file
    metadatas_yaml = prompt_select("Which metadata file do you want to use?",
                                   choices=[m for m in os.listdir(metadatas_dir) if m.endswith(".yml")]
                                   )

    # load metadata
    metadata_config = load_yaml(os.path.join(metadatas_dir, metadatas_yaml))

    base_url, api_url = NAKALA_ROUTES[environment].values()

    dir_images = metadata_config["data"]["path"]

    # retrieve all images from the directory with absolute path
    images = sorted([os.path.join(dir_images, f) for f in os.listdir(os.path.join(data_dir, dir_images))])

    if prompt_confirm(
            f"Are you sure you want to create a data repository with {len(images)} images to Nakala {environment}?",
            default=False):
        typer.echo(cli_log(
            f"Start sending data from {os.path.basename(dir_images)}/ to Nakala {environment} with '{method}' mode...",
            "info", "info"))
        # start timer to measure execution time
        start = time()
        # process images
        if method.lower() == "go":
            typer.echo("Using Go to process images")
            images = [image for image in images]
            sha1s = process_images_with_go(api_url, API_NAKALA_KEY, images)
            results_objects = [NakalaItem(sha1=sha1['sha1'], original_name=sha1['name']) for sha1 in sha1s]
        else:
            sha1s, results_objects, empty_sha1s = work_with_accumulator(images, method, api_url)
        sleep(0.5)
        # create data repository
        handle_data_id = initialize_data(api_url, sha1s, metadata_config)
        try:
            typer.echo(
                cli_log(f"Data repository created on Nakala with DOI: {handle_data_id['payload']['id']}", "success",
                        "pkg"))
        except Exception as e:
            typer.echo(cli_log(f"Error: {e} - Cannot create data", "error", "error"))
            sys.exit(1)
        # update NakalaItem with data DOI and collection DOI (if exists)
        for obj in results_objects:
            obj.data_doi = handle_data_id['payload']['id']
            obj.collection_doi = metadata_config["collectionsIds"]

        # save report
        typer.echo(cli_log("Saving report...", "info", "info"))
        try:
            name_csv = f"{metadata_config['name']}_mapping_ids_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            NakalaItem.to_csv(name_csv, sorted(results_objects, key=lambda x: x.original_name))
        except Exception as e:
            name_csv = None
            typer.echo(cli_log(f"Error: {e} - Cannot save report", "error", "error"))
        # end timer
        end = time()
        typer.echo(cli_log(f"Total time: {end - start} seconds", "info", "time"))
        run_tests = True
        files = None
        # run tests
        try:
            response = requests.get(f"{api_url}/datas/{handle_data_id['payload']['id']}", headers={
                "X-API-KEY": API_NAKALA_KEY,
                "accept": "application/json",
            })
            files = response.json()['files']
        except:
            typer.echo(cli_log("Cannot run tests for the moment", "info", "info"))
            run_tests = False
            response = None

        if run_tests:
            typer.echo(cli_log("Running tests...", "info", "look"))
            __check_total_images(files, len(sorted(images)))
            __check_order_images(files, sorted([os.path.basename(image) for image in images]))
            if name_csv is not None:
                __check_sha1_consistency(f"{output_dir}/{name_csv}", response.json()['files'])
            else:
                typer.echo(cli_log("Cannot check sha1 consistency because the report is missing", "warning", "warning"))

        typer.echo(cli_log(
            f"Finished with success! Data handle: {handle_data_id['payload']['id']}, show report {name_csv}.csv in "
            f"output folder\nDon't forget to reorder images in Nakala frontend.",
            "success",
            "good"))
    else:
        sys.exit()


if __name__ == '__main__':
    cli = typer.main.get_command(app)
    cli.params = [
        param
        for param in cli.params
        if param.name != "show_completion" and param.name != "install_completion"
    ]
    cli()
