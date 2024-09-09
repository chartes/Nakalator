#!/usr/bin/env python3
# -- coding: utf-8 --

"""nakalator.py

Main entry point. Launcher for the Nakalator CLI.
"""

import os
import shutil
import subprocess
import sys

from typer import Typer
from typer import main as t_main

from lib.Nakalator import Nakalator
from lib.utils.cli_utils import (banner,
                                 prompt_select,
                                 prompt_confirm,
                                 cli_log)
from lib.templates import (credentials_to_yaml,
                           metadata_to_yaml,
                           workspace_info_init)
from lib.utils.io_utils import write_yaml
from lib.constants import (base_dir_create,
                           data_dir_create,
                           metadatas_dir_create,
                           output_dir_create,
                           metadatas_dir)

app = Typer()

@app.command()
def init() -> None:
    """Initialize the project file structure.
    the user needs to launch this command the first time they use the CLI."""
    # Test if the project structure already exists
    if os.path.exists("nakalator_workspace"):
        cli_log("Project structure already exists.", "warning")
        if not prompt_confirm("Do you want to overwrite it?", default=False):
            sys.exit(0)
        shutil.rmtree("nakalator_workspace")

    # Create the project structure
    for path in [base_dir_create,
                 data_dir_create,
                 metadatas_dir_create,
                 output_dir_create]:
        path.mkdir(parents=True, exist_ok=True)

    # Create the credentials.yml and metadata_example.yml files
    for file, content in [(base_dir_create / "credentials.yml", credentials_to_yaml),
                          (metadatas_dir_create / "metadata_example.yml", metadata_to_yaml)]:
        write_yaml(base_dir_create / file, content)

    cli_log(f"Nakalator project structure initialized at {base_dir_create}", "success")
    print(workspace_info_init(base_dir_create))
    cli_log("Recreate the project structure overwrites the existing one. Be careful! Use only if it is necessary.", "warning")
    cli_log("For more information, see the README.md file in https://github.com/chartes/Nakalator.", "info")


@app.command()
def main() -> None:
    """Main function for the Nakalator CLI."""
    banner()

    # Test if the project structure exists and if the user is in the right directory
    if not os.getcwd().endswith("nakalator_workspace"):
        cli_log(
                "You are not in the nakalator_workspace/ directory. cd into it or create "
                "it with 'nakalator init' if not exist before restart.", "info")
        sys.exit(1)

    # Select Nkl env where data are send? (prod / test)
    environment_opt_selected = prompt_select("Which Nakala environment do you want to use to send your data?",
                                             choices=['test', 'production'],
                                             default="test"
                                             )

    # Sending multiple data to Nkl? (yes / no)
    multiple_data_opt_selected = prompt_confirm("Do you want create mutliple data in Nakala?",
                                                default=False
                                                )

    # Select the metadata file or the directory containing the metadata files
    metadata_opt_selected = prompt_select(
        "Which directory contains the metadata files?",
        choices=[d for d in os.listdir(metadatas_dir) if os.path.isdir(os.path.join(metadatas_dir, d))]
    , default=os.listdir(metadatas_dir)[0]) if bool(multiple_data_opt_selected) else prompt_select(
        "Which metadata file do you want to use?",
        choices=[f for f in os.listdir(metadatas_dir) if f.endswith(".yml")],
        default=os.listdir(metadatas_dir)[0]
    )

    # Are the data attached to a collection? (yes / no)
    collection_attached_opt_selected = prompt_confirm("Are the data attached to a collection?", default=False)

    # If the data are attached to a collection, are they all attached to the same collection?
    if bool(multiple_data_opt_selected) and bool(collection_attached_opt_selected):
        same_batch_collection = prompt_confirm("Are all the data attached to the same collection?", default=False)
    else:
        same_batch_collection = False

    if prompt_confirm("Are you ready to send to Nakala?", default=False):
        nklor = Nakalator(
            env=environment_opt_selected,
            batch=multiple_data_opt_selected,
            metadata_loc=metadata_opt_selected,
            collection_confirm=collection_attached_opt_selected,
            same_collection_batch=same_batch_collection
        )
        nklor.run_data()

    sys.exit(0)


if __name__ == "__main__":
    """Launch the CLI.
    `show_completion` and `install_completion` are hidden commands to show and install shell completions.
    """
    cli = t_main.get_command(app)
    cli.params = [
        param
        for param in cli.params
        if param.name != "show_completion" and param.name != "install_completion"
    ]
    cli()
