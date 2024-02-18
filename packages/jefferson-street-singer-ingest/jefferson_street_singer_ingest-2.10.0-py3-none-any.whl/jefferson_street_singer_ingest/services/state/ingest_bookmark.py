from typing import Dict
from datetime import datetime
import json


class IngestBookmark:
    def __init__(
        self,
        pipeline_name: str = "",
        source_uri: str = "",
        timestamp: str = datetime.strftime(datetime.utcnow(), "%Y%m%d%H%M"),
        additional_data: Dict[str, str] = None,
    ):
        self.pipeline_name = pipeline_name
        self.source_uri = source_uri
        self.timestamp = timestamp
        self.additional_data = additional_data if additional_data else {}

    def to_dict(self):
        return {
            self.pipeline_name: {
                self.source_uri: {
                    "timestamp": self.timestamp,
                    "additional_data": self.additional_data,
                }
            }
        }

    def to_json(self) -> str:
        dict_ = self.to_dict()
        return json.dumps(dict_)
