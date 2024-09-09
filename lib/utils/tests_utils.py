# --*-- coding: utf-8 --*--

"""A test series to check :
    - data integrity
    - data order
    - sha1 consistency
"""

from lib.utils.cli_utils import cli_log
from lib.utils.io_utils import load_csv

def check_total_files(files_received: list,
                       total_org_files: int) -> None:
    """Check if the total number of files received is equal to the total number of original files

    :param files_received: the files received from Nakala
    :type files_received: list
    :param total_org_images: the total number of original files
    :type total_org_images: int
    :return: None
    :rtype: None
    """
    assert len(files_received) == total_org_files, cli_log("Missing files on Nakala", "error")
    cli_log("Check total files on Nakala OK", "success")

def check_order_files(files_received: list,
                       sorted_org_files: list) -> None:
    """Check if the order of the files received is the same as the order of the original files

    :param files_received: the files received from Nakala
    :type files_received: list
    :param sorted_org_images: the sorted original files
    :type sorted_org_images: list
    :return: None
    :rtype: None
    """
    try:
        for file_received, file_org in zip(files_received, sorted_org_files):
            assert file_received['name'] == file_org, cli_log("Order files are not the same. "
                                                        "Don't worry, this happens when you use method "
                                                        "'hard' or you have retried requests."
                                                        "You can always reorder them in Nakala frontend", "warning")
        cli_log("Check files order on Nakala OK", "success")
    except AssertionError:
        cli_log("Cannot check the order of the files", "error")
    except KeyError:
        cli_log("Cannot check the order of the files", "error")

def check_sha1_consistency(csv_path: str, api_files: list) -> None:
    """Check if the SHA1 in the CSV are the same as the SHA1 in the API response

    :param csv_path: the path to the CSV file
    :type csv_path: str
    :param api_files: the files received from the API
    :type api_files: list
    :return: None
    :rtype: None
    """
    df = load_csv(csv_path)

    # check if the CSV has a column named 'sha1' and if it values are not null
    assert not df['sha1'].isnull().any(), cli_log("SHA1 is missing in the CSV", "error")

    # compare original_name and sha1 in the CSV with the API response
    for index, row in df.iterrows():
        original_name = row['original_name']
        sha1_csv = row['sha1']
        api_file = next(
            (file for file in api_files if file['name'] == original_name),
            None)
        assert api_file is not None, cli_log(f"File {original_name} not found in the API response", "error")
        assert api_file['sha1'] == sha1_csv, cli_log(
            f"SHA1 for file {original_name} is different in the API response", "error")

    # check if the number of files in the CSV is the same as the number of files in the API response
    # (same as __check_total_images())
    assert len(df) == len(api_files), cli_log("Some files are missing in the API response", "error")

    # check if all the files in the CSV are in the API response (not less, not more)
    df_copy = df.copy()
    for file in api_files:
        api_file = file
        df_copy = df_copy[df_copy['original_name'] != api_file['name']]
    assert len(df_copy) == 0, cli_log("Some files are missing in the CSV", "error")

    cli_log("check files with SHA1 on Nakala OK", "success")