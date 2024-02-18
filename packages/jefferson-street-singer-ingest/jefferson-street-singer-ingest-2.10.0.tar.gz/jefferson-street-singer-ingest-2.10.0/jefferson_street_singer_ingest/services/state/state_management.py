import json
import logging

from mergedeep import merge
from datetime import datetime
from typing import Dict
from google.cloud import storage


from jefferson_street_singer_ingest.services.state.ingest_bookmark import IngestBookmark


class StateManagement:
    def __init__(self, project_id: str = "", pipeline_name: str = "") -> None:
        self.project_id = project_id
        self.pipeline_name = pipeline_name

        if project_id:
            storage_client = storage.Client()
            self.bucket = storage_client.bucket(project_id)

    def merge_state_and_bookmark(self, ingest_bookmark):
        most_recent_state_content = self.get_most_recent_state_content()
        updated_state_content = {}
        if most_recent_state_content:
            updated_state_content = {
                "bookmarks": merge(
                    most_recent_state_content["bookmarks"], ingest_bookmark.to_dict()
                )
            }
        else:
            updated_state_content = {"bookmarks": ingest_bookmark.to_dict()}

        return updated_state_content

    def write_bookmark_to_state(
        self,
        source_uri: str = "",
        timestamp: str = datetime.strftime(datetime.utcnow(), "%Y%m%d%H%M%S"),
        additional_data: Dict[str, str] = {},
    ):
        if not self.pipeline_name:
            logging.info(
                f"pipeline_name not set for state management, skipping writing bookmark to state."
            )
            return

        state_file_name = f"state_{timestamp}"
        cloud_storage_destination = f"ingest_states/raw/{state_file_name}.json"

        updated_state_content = self.merge_state_and_bookmark(
            ingest_bookmark=IngestBookmark(
                pipeline_name=self.pipeline_name,
                source_uri=source_uri,
                timestamp=timestamp,
                additional_data=additional_data,
            )
        )

        blob = self.bucket.blob(cloud_storage_destination)
        blob.upload_from_string(json.dumps(updated_state_content))

        logging.info(
            f"State for pipeline_name {self.pipeline_name} updated for project_id {self.project_id}."
        )

    def get_most_recent_state_content(self) -> Dict:
        state_files = self.bucket.list_blobs(prefix="ingest_states/raw/state_")

        first = True
        most_recent_state_file_date = None
        most_recent_state_file = None
        for state_file in state_files:
            state_file_date = state_file.name.split("_")[-1].split(".")[0]

            if first:
                most_recent_state_file_date = state_file_date
                most_recent_state_file = state_file
                first = False
            else:
                if state_file_date > most_recent_state_file_date:
                    most_recent_state_file_date = state_file_date
                    most_recent_state_file = state_file

        if most_recent_state_file:
            with most_recent_state_file.open("r") as f:
                most_recent_state_file_content = json.loads(f.read())

            return most_recent_state_file_content
        else:
            return {}
