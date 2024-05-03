# --*-- coding: utf-8 --*--
"""This module contains the consistency tests functions for ensuring the integrity of the data sent to Nakala"""

from termcolor import colored
import pandas as pd
import json


def __check_total_images(files_received: list,
                         total_org_images: int) -> None:
    """Check if the total number of files received is equal to the total number of original images"""
    assert len(files_received) == total_org_images, print(colored("❌ \tMissing files", "red"))
    print(colored("✅ \tAll files are present in Nakala", "green"))


def __check_order_images(files_received: list,
                         sorted_org_images: list) -> None:
    """Check if the order of the files received is the same as the order of the original images"""
    try:
        for file_received, file_org in zip(files_received, sorted_org_images):
            assert file_received == file_org, print(colored("❓\tOrder files are not the same. "
                                                            "Don't worry, this happens when you use method "
                                                            "'hard' or you have retried requests."
                                                            "You can always reorder them in Nakala frontend", "yellow")
                                                    )
            print(colored("✅ \tfiles are in good order", "green"))
    except AssertionError:
        pass


def __check_sha1_consistency(csv_file: str, api_files: list) -> None:
    """Check if the SHA1 in the CSV are the same as the SHA1 in the API response"""
    df = pd.read_csv(csv_file, sep=";")

    # check if the CSV has a column named 'sha1' and if it values are not null
    assert not df['sha1'].isnull().any(), colored("❌ \tSHA1 is missing in the CSV", "red")

    # compare original_name and sha1 in the CSV with the API response
    for index, row in df.iterrows():
        original_name = row['original_name']
        sha1_csv = row['sha1']
        api_file = next(
            (file for file in api_files if file['name'] == original_name),
            None)
        assert api_file is not None, colored(f"❌ \tFile {original_name} not found in the API response", "red")
        assert api_file['sha1'] == sha1_csv, colored(
            f"❌ \tSHA1 for file {original_name} is different in the API response", "red")

    # check if the number of files in the CSV is the same as the number of files in the API response
    # (same as __check_total_images())
    assert len(df) == len(api_files), colored("❌ \tSome files are missing in the API response", "red")

    # check if all the files in the CSV are in the API response (not less, not more)
    df_copy = df.copy()
    for file in api_files:
        api_file = file
        df_copy = df_copy[df_copy['original_name'] != api_file['name']]
    assert len(df_copy) == 0, colored("❌ \tSome files are missing in the CSV", "red")

    print(colored("✅ \tSHA1 are consistent", "green"))


if __name__ == "__main__":
    csv = ""
    response = ""
    parse_response = json.load(open(response, "r"))['files']
    __check_sha1_consistency(csv, parse_response)

