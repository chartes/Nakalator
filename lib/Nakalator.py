# -*- coding: utf-8 -*-

"""Nakalator.py
"""
import sys
import os
import time
import datetime


from lib.NakalatorAPIRequest import NakalaAPIRequestBuilder
from lib.utils.cli_utils import (
    prompt_confirm,
    cli_log,
    msg
)
from lib.utils.io_utils import (
    custom_sort,
    load_yaml,
    NakalaItem,
    merge_df_reports,
    rewrite_metadata_config_with_collection_ids
)
from lib.utils.tests_utils import (
    check_total_files,
    check_order_files,
    check_sha1_consistency
)
from lib.constants import (
    metadatas_dir,
    output_dir
)
from lib.bridge.nkl_gotils import process_nkl_files_with_go


class Nakalator:
    """Class to manage the Nakalator process.

    :param env: the environment to use (default: "test")
    :type env: str, optional
    :param batch: if the process is in batch mode (default: False)
    :type batch: bool, optional
    :param metadata_loc: the location of the metadata files
    :type metadata_loc: str
    :param collection_confirm: if the collections must be confirmed (default: False)
    :type collection_confirm: bool, optional
    :param same_collection_batch: if the same collection must be used for all the batch (default: False)
    :type same_collection_batch: bool, optional
    """
    def __init__(self,
                 env: str = "test",
                 batch: bool = False,
                 metadata_loc: str = None,
                 collection_confirm: bool = False,
                 same_collection_batch: bool = False
                 ) -> None:
        """Initialize the Nakalator class.
        :attr _environment: the environment to use
        :type _environment: str
        :attr _batch: if the process is in batch mode
        :type _batch: bool
        :attr _metadata_loc: the location of the metadata files
        :type _metadata_loc: str
        :attr _collection_confirm: if the collections must be confirmed
        :type _collection_confirm: bool
        :attr _same_collection_batch: if the same collection must be used for all the batch
        :type _same_collection_batch: bool
        :attr nakala_sender: the NakalaAPIRequestBuilder instance
        :type nakala_sender: NakalaAPIRequestBuilder
        :attr metadata_files: the metadata files
        :type metadata_files: list
        :attr metadata_files_cache: the cached metadata files
        :type metadata_files_cache: list
        :attr collection_created: the created collections
        :type collection_created: list
        """
        self._environment = env
        self._batch = batch
        self._metadata_loc = metadata_loc
        self._collection_confirm = collection_confirm
        self._same_collection_batch = same_collection_batch

        self.nakala_sender = NakalaAPIRequestBuilder(env=self._environment)

        # assemble metadatas files
        self.metadata_files = self.assemble_metadata_files()
        # cache metadata
        self.metadata_files_cache = self.cache_metadata()
        # create collections
        if self._collection_confirm:
            self.collection_created = self.create_collections()
        else:
            self.collection_created = []

    @staticmethod
    def prepare_files(path_dir_files: str) -> list:
        """Prepare files to be sent to Nakala.

        :param path_dir_files: the path to the images
        :type path_dir_files: str
        :return: the sorted list of images
        :rtype: list
        """
        return sorted([os.path.join(path_dir_files, f) for f in os.listdir(path_dir_files)])

    @staticmethod
    def format_id(doi: str) -> str:
        """Format the DOI.

        :param doi: the DOI to format
        :type doi: str
        :return: the formatted DOI
        :rtype: str
        """
        return doi.replace("/", "_")

    def create_collections(self) -> list:
        """Create collections on Nakala.

        :return: the created collections
        :rtype: list
        """
        collections_created = []
        turn = 0
        total = len(self.metadata_files_cache)
        already_checked = []
        for f, m in self.metadata_files_cache:
            turn += 1
            if total > 1 and turn >= 2 and self._same_collection_batch:
                # attach all data to the same collection
                m["collectionIds"] = collections_created[0][1]
                rewrite_metadata_config_with_collection_ids(m, f)
                cli_log(f"Collection: {collections_created[0][0]} attached to {f}, continue...", "info")
                collections_created.append((collections_created[0][0], collections_created[0][1]))
            else:
                # check if ["collectionsIds"] is empty or not
                if m["collectionIds"] in ["", None]:
                    filename = os.path.basename(f)
                    new_collection = True
                    if ((m["collectionTitle"] in ["", None]) or
                            (m["collectionDescription"] in ["", None])):
                        cli_log(f"'collectionTitle' or 'collectionDescription' fields are empty: If you want to create a new collection and attach data to this new collection, please fill the required fields in file: {f} and restart process.", "error")
                        sys.exit(1)
                    else:
                        cli_log(
                            f"Collection: '{m['collectionTitle']}' not exist for {filename} in Nakala, I  start by creating it...",
                            "info")
                        metadata_collection = {
                            "collectionTitle": m["collectionTitle"],
                            "collectionDescription": m["collectionDescription"],
                            "collectionStatus": m["collectionStatus"],
                        }
                    if metadata_collection["collectionTitle"] in [c[0] for c in collections_created]:
                        # ask to user if he want to use the existing collection that detected
                        cli_log(
                            f"Collection: {metadata_collection['collectionTitle']} already exist, do you want to use it?", "info")
                        use_existing_collection = prompt_confirm("Do you want to use the existing collection?")
                        if use_existing_collection:
                            collection_id = \
                                [c[1] for c in collections_created if c[0] == metadata_collection['collectionTitle']][0]
                            cli_log(
                                f"Collection: {metadata_collection['collectionTitle']} with id: {collection_id} OK.", "success")
                            m["collectionIds"] = collection_id
                            rewrite_metadata_config_with_collection_ids(m, f)
                            new_collection = False
                            collections_created.append((metadata_collection['collectionTitle'], collection_id))

                    if new_collection:
                        if ((metadata_collection["collectionTitle"] in ["", None]) or
                                (metadata_collection["collectionDescription"] in ["", None])):
                            cli_log(f"collectionTitle or collectionDescription is empty, please fill it for {f}", "error")
                            sys.exit(1)
                        if metadata_collection["collectionStatus"] in ["", None]:
                            cli_log(f"collectionStatus is empty, by default it will be 'private' for {f}, you can change this later in Nakala.", "info")
                            m["collectionStatus"] = "private"
                            metadata_collection["collectionStatus"] = "private"
                            rewrite_metadata_config_with_collection_ids(m, f)
                            # rewrite metadata file with collectionIds
                        # create collection
                        collection_title, collection_id = self.nakala_sender.initialize_nakala_collection(m)
                        collections_created.append((collection_title, collection_id))
                        # rewrite metadata file with collectionIds
                        m["collectionIds"] = collection_id
                        rewrite_metadata_config_with_collection_ids(m, f)
                        cli_log(f"Collection: {collection_title} created for {filename} with id : {collection_id} on Nakala.", "success")
                else:
                    if m["collectionIds"] in [c[1] for c in already_checked]:
                        cli_log(f"Collection: {m['collectionIds']} already checked and is OK for {os.path.basename(f)}.", "info")
                        # find collection title from collection id
                        collection_title = [c[0] for c in already_checked if c[1] == m["collectionIds"]][0]
                        collections_created.append((collection_title, m["collectionIds"]))
                    else:
                        cli_log(f"Collection: {m['collectionIds']} already exist for {f}, check it...", "info")
                        collection_title = self.nakala_sender.check_nakala_collection_exists(m["collectionIds"])
                        collections_created.append((collection_title, m["collectionIds"]))
                        cli_log(f"Check collection: '{collection_title}' with id: {m['collectionIds']} is OK.", "success")
                        already_checked.append((collection_title, m["collectionIds"]))
        return collections_created

    def cache_metadata(self) -> list:
        """Cache metadata files.

        :return: the cached metadata files
        :rtype: list
        """
        return [(f, load_yaml(f)) for f in sorted(self.metadata_files, key=custom_sort)[::-1]]

    def assemble_metadata_files(self) -> list:
        """Assemble and sorted metadata files to prepare data/collection creation.

        :return: the sorted list of metadata files
        :rtype: list
        """
        return sorted(
            [ os.path.join(metadatas_dir,self._metadata_loc,f) for f in os.listdir(
                os.path.join(
                    metadatas_dir,
                    self._metadata_loc
                )
            ) if f.endswith(".yml")],
            key=custom_sort)[::-1] if self._batch else [
            os.path.join(
                metadatas_dir,
                self._metadata_loc
            )]

    def run_data(self) -> None:
        """Run the data creation process.

        :return: None
        :rtype: None
        """
        reports = []
        results_objects = []
        count = 0
        start_all_process = time.time()
        for f, m in self.metadata_files_cache:
            count += 1
            cli_log(f"{count}/{len(self.metadata_files_cache)} Processing metadata file > nkl data: {os.path.basename(f)}", "info")
            # prepare images
            files_to_send = self.prepare_files(m["data"]["path"])
            # try if path data contains dir "data"
            if "data" not in m["data"]["path"]:
                cli_log(f"Files to send must be in 'data' directory, please check in {os.path.basename(f)}", "error")
                sys.exit(1)
            # retrieve collection id and title
            collection_id = m["collectionIds"]
            start_process_files = time.time()
            sha1s = process_nkl_files_with_go(
                    url=f'{self.nakala_sender._api_url}/datas/uploads',
                    api_key=self.nakala_sender._api_key,
                    file_paths=files_to_send
                )
            cli_log("⏳\tTime elapsed to process files on Nakala: {:.2f} seconds".format(time.time() - start_process_files), "info")
            results_objects = [NakalaItem(sha1=sha1['sha1'], original_name=sha1['name']) for sha1 in sha1s]
            # create data repository
            handle_data_id = self.nakala_sender.initialize_nakala_data(sha1s=sha1s, metadata_config=m)
            # update objects with data_doi and collection_doi
            for obj in results_objects:
                obj.data_doi = handle_data_id
                obj.collection_doi = collection_id

            with msg.loading("Saving report..."):
                # create an output dir if not exist based on m['name']
                try:
                    name_project = m["name"]
                except:
                    name_project = "project"
                output_dir_project = os.path.join(output_dir, name_project)
                if not os.path.exists(output_dir_project):
                    os.makedirs(output_dir_project)
                try:
                    if collection_id in ["", None]:
                        name_report_csv = f"data_{count}_{self.format_id(handle_data_id)}_mapping_ids_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                    else:
                        name_report_csv = f"data_{count}_{self.format_id(collection_id)}_{self.format_id(handle_data_id)}_mapping_ids_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                    NakalaItem.to_csv(name_report_csv, results_objects, output_dir_project)
                    reports.append(name_report_csv)
                except Exception as e:
                   cli_log(f"Error when saving report: {e}", "error")

            # run tests
            with msg.loading("Running tests..."):
                files = self.nakala_sender.check_data_files_exist(
                data_id=handle_data_id
                )
                if len(files) > 0:
                    cli_log("🔍Results tests session: ")
                    check_total_files(files, len(sorted(files_to_send)))
                    check_order_files(files, sorted([os.path.basename(f) for f in files_to_send]))
                    check_sha1_consistency(os.path.join(output_dir_project, name_report_csv), files)
                    print("-" * 50)
                else:
                    cli_log("Cannot run tests for the moment, please check manually in Nakala", "warning")


            # save report
            cli_log(f"Data: {handle_data_id} created with success on Nakala. check output report: {name_report_csv}", "success")

            # if not the last metadata file wait 2 secs before next
            if f != self.metadata_files_cache[-1][0]:
                time.sleep(2)

        if len(reports) > 1 and self._same_collection_batch:
            collection_doi = self.format_id(results_objects[0].collection_doi)
            merge_df_reports(sorted_reports=sorted(reports)[::-1],
                             collection_doi=collection_doi,
                             output_dir=output_dir_project)
            cli_log(f"Reports merged in one file: merge_{collection_doi}_mapping_ids_all.csv", "success")

        # time elapsed for all process
        cli_log("⏳\tTime elapsed for all process: {:.2f} seconds".format(time.time() - start_all_process), "info")
        cli_log(f"All process done! See you soon.", "success")
        sys.exit(0)
