import os
import sys
import json
import logging

from typing import Any, List
from google.cloud import storage

from jefferson_street_singer_ingest.services.target.avro_generator import (
    build_avro_file,
    build_avro_schema,
)  # noqa: E402


class BaseGoogleCloudStorageTarget:
    def __init__(self, config) -> None:
        self.current_avro_schema: Any = None
        self.current_name: str = ""
        self.avro_files: List = []
        self.config_values = self.load_config(config)

        self.run()

    def run(self):
        self.parse_tap()

        for avro_file in self.avro_files:
            if os.path.exists(avro_file):
                self.upload_avro_to_gcs(
                    bucket_name=self.config_values["project_id"], source_file_name=avro_file
                )
            else:
                logging.info(f"WARNING - Skipping avro file {avro_file} upload, no records written.")

    """ Finished adding error checking for config file. """

    def load_config(self, config):
        with open(config) as fil:
            return json.load(fil)

    def parse_tap(self):
        for line in sys.stdin:
            json_line = json.loads(line)

            if json_line["type"] == "SCHEMA":
                self.current_name = json_line["stream"]
                self.current_fields = json_line["schema"]["properties"].keys()
                self.current_avro_schema = build_avro_schema(
                    self.current_fields, self.current_name
                )

                self.avro_files.append(f"{self.current_name}.avro")
            if json_line["type"] == "RECORD":
                build_avro_file(
                    self.current_name, self.current_avro_schema, [json_line["record"]]
                )

    def upload_avro_to_gcs(self, bucket_name, source_file_name):
        """
        Google Cloud Storage Convention:
        project_id/bq_external_data/raw/file_name
        """
        destination_blob_name = f"bq_external_data/raw/{source_file_name}"

        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        blob.upload_from_filename(source_file_name)
        logging.info(f"File {source_file_name} uploaded to {destination_blob_name}.")
