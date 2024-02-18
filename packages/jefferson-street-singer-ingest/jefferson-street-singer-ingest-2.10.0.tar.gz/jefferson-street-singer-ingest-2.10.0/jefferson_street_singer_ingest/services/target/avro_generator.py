import logging
import fastavro

from fastavro import writer


def build_avro_schema(column_names, name: str) -> None:
    # if "cherre_file_row_number" not in column_names:
    #     raise ValueError("Column names must contain cherre_file_row_number")
    # if "cherre_file_name" not in column_names:
    #     raise ValueError("Column names must contain cherre_file_name")
    """Method to zip field names into Avro schema format."""
    logging.debug(f"Table name is set to {name}")
    avro_dict = {
        "namespace": "jeffersons_street_capital_advisors",
        "type": "record",
        "name": "source",
        "fields": [
            {"name": column_name, "type": "string", "default": ""}
            for column_name in column_names
        ],
    }
    return fastavro.parse_schema(avro_dict)


def build_avro_file(file_name, avro_schemas, processed_responses):
    if avro_schemas:
        with open(f"/files/{file_name}.avro", "a+b") as out:
            writer(out, avro_schemas, processed_responses)
