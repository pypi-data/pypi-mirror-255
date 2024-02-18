import time
import logging
import json
import requests

from collections import abc
from typing import Iterable, Optional, Any, Union, Dict
from dataclasses import dataclass
from datetime import datetime

from singer import Schema
from singer_sdk import RESTStream as MeltanoRestStream
from singer_sdk.authenticators import APIAuthenticatorBase

from jefferson_street_singer_ingest.services.stream.base_tap_stream import BaseTapStream


@dataclass(frozen=True)
class Prop:
    type: str = "string"

    def to_dict(self):
        return {"type": self.type}


ValidRecordValueType = Union[str, int, float, complex, bool]
Record = Dict[str, ValidRecordValueType]


class RESTStream(BaseTapStream, MeltanoRestStream):
    def __init__(
        self,
        url: str,
        name: str,
        path: str = "",
        project_id: str = "",
        pipeline_name: str = "",
        authenticator: APIAuthenticatorBase = None,
        request_delay: Optional[float] = None,
    ):
        super().__init__(name=name, project_id=project_id, pipeline_name=pipeline_name)

        self.request_delay = request_delay
        self._authenticator = authenticator
        self._url_base = url
        self.path = path
        self.avro_schemas = {}

        self._found_schema: Optional[Dict[str, Any]] = None
        self._found_schema_object: Optional[Schema] = None

    @property
    def url_base(self) -> str:
        return self._url_base

    @property
    def authenticator(self) -> Optional[APIAuthenticatorBase]:
        if self._authenticator:
            return self._authenticator
        return super().authenticator

    @authenticator.setter
    def authenticator(self, val: Optional[APIAuthenticatorBase]) -> None:
        self._authenticator = val

    @property
    def _schema(self) -> Dict[str, Any]:
        """
        Injects schema generation into the base object to meld them
        """
        if not self._found_schema:
            schema_obj = self.get_schema()

            for prop in schema_obj.properties:
                if not hasattr(schema_obj.properties[prop], "to_dict"):
                    schema_obj.properties[prop] = Prop(
                        schema_obj.properties[prop]["type"]
                    )
            self._found_schema = schema_obj.to_dict()

        if self._found_schema:
            return self._found_schema
        raise RuntimeError("Couldn't find schema")

    @_schema.setter
    def _schema(self, val: Schema) -> None:
        if val:
            raise ValueError("Attempted to set schema with a value!")

    def flatten_object(self, arg: Any) -> Record:
        """
        Flatten nested objects.
        """
        dic = dict(arg)
        res = {}
        for key in dic:
            val = dic[key]
            if isinstance(val, abc.Mapping):
                sub_dic = self.flatten_object(val)
                for sub_key in sub_dic:
                    res[f"{key}_{sub_key}"] = sub_dic[sub_key]
            else:
                res[key] = val

        return res

    """ Implement bookmarking for API. """

    def get_records(self, partition: Optional[dict] = None) -> Iterable[Dict[str, Any]]:
        if self.request_delay:
            time.sleep(self.request_delay)

        try:
            for row in self.request_records(partition):
                row = self.post_process(row)
                flat = self.flatten_object(row)
                yield flat
                
            self.bookmark_service.write_bookmark_to_state(self.get_url(partition))
        except Exception as e:
            logging.error(e)
            raise

    def get_schema(self) -> Schema:
        first = None
        if not self._found_schema_object:
            for rec in self.get_records():
                first = rec
                break

            """ Translate to a schema. """
            props = {}
            if first:
                for key in first:
                    if isinstance(first[key], int):
                        props[key] = Prop("integer")
                    else:
                        props[key] = Prop()
            self._found_schema_object = Schema(properties=props)

        return self._found_schema_object

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        resp_json = response.json()
        if isinstance(resp_json, dict):
            yield resp_json
        else:
            for row in resp_json:
                yield row

    def post_process(
        self, row: Dict[str, Any], partition: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        cleaned_row = {}
        for key, val in row.items():
            if isinstance(val, (dict, list)):
                val = json.dumps(val)
            cleaned_row[self.clean_key(str(key))] = str(val)

        cleaned_row[
            "jefferson_street_ingest_datetime"
        ] = f"{datetime.strftime(datetime.now(), '%Y%m%d%H%m')}"
        cleaned_row["jefferson_street_ingest_name"] = self.name
        return cleaned_row

    @staticmethod
    def clean_key(key: str) -> str:
        return (
            key.lower()
            .replace("-", "_")
            .replace(",", "_")
            .replace(" ", "_")
            .replace(".", "_")
            .replace("(", "")
            .replace(")", "")
            .replace("/_", "")
        )
