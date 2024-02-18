from collections import UserDict
import yaml
import os
from pathlib import Path
from typing import Dict, List
import pyspark.sql.types as T


def build_layer_path(layer_name: str) -> str:
    """
    Method for building the path to the layer.

    :param layer_name: The name of the layer.
    :return: The path to the layer.
    """
    return (
        Path(__file__)
        .parent.joinpath("layers")
        .joinpath(layer_name)
        .absolute()
        .as_posix()
    )


# noqa


class Datalake(UserDict):
    INGEST_LAYER_PATH = build_layer_path("ingest")
    BRONZE_LAYER_PATH = build_layer_path("bronze")
    SILVER_LAYER_PATH = build_layer_path("silver")
    GOLD_LAYER_PATH = build_layer_path("gold")
    MASTER_LAYER_PATH = build_layer_path("master")

    def __read_yaml_to_dict__(self, yaml_path):
        with open(yaml_path, "r") as yaml_file:
            yaml_dict = yaml.safe_load(yaml_file)
        return yaml_dict

    def __dict_to_spark_schema__(self, schema: List[Dict[str, str]]):
        """
        Converts a dictionary to a spark schema.

        :param schema: The schema to convert.
        :return: The spark schema.
        """
        spark_schema = T.StructType()
        for field in schema:
            spark_schema.add(field["name"], field["type"])
        return spark_schema

    def __parse_spark_options__(self, options: List[Dict[str, str]]):
        """
        Parses the spark options.

        :param options: The options to parse.
        :return: The parsed options.
        """
        result = {}
        for option in options:
            result[option["name"]] = option["value"]
        return result

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]

    def __repr__(self):
        return repr(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def __delitem__(self, key):
        del self.__dict__[key]

    def clear(self):
        return self.__dict__.clear()

    def copy(self):
        return self.__dict__.copy()

    def has_key(self, k):
        return k in self.__dict__

    def update(self, *args, **kwargs):
        return self.__dict__.update(*args, **kwargs)

    def keys(self):
        return self.__dict__.keys()

    def values(self):
        return self.__dict__.values()

    def items(self):
        return self.__dict__.items()

    def pop(self, *args):
        return self.__dict__.pop(*args)

    def __cmp__(self, dict_):
        return self.__cmp__(self.__dict__, dict_)

    def __contains__(self, item):
        return item in self.__dict__

    def __iter__(self):
        return iter(self.__dict__)

    def __init__(self):
        """
        Constructor for Datalake class.
        """
        result = {}
        for layer_name, layer_path in zip(
            ["ingest", "bronze", "silver", "gold", "master"],
            [
                self.INGEST_LAYER_PATH,
                self.BRONZE_LAYER_PATH,
                self.SILVER_LAYER_PATH,
                self.GOLD_LAYER_PATH,
                self.MASTER_LAYER_PATH,
            ],
        ):
            result[layer_name] = {}
            for file in os.listdir(layer_path):
                if file.endswith(".yaml") or file.endswith(".yml"):
                    loaded_file = self.__read_yaml_to_dict__(
                        os.path.join(layer_path, file)
                    )
                    loaded_file["datalake_layer"] = layer_name
                    result[layer_name][loaded_file["datalake_key"]] = {
                        "datalake_key": loaded_file["datalake_key"],
                        "datalake_bucket": loaded_file["datalake_bucket"],
                        "file_extension": loaded_file["file_extension"],
                    }
                    if loaded_file.get("schema"):
                        result[layer_name][loaded_file["datalake_key"]][
                            "spark_schema"
                        ] = self.__dict_to_spark_schema__(
                            loaded_file["schema"]
                        )
                    if loaded_file.get("options"):
                        result[layer_name][loaded_file["datalake_key"]][
                            "options"
                        ] = self.__parse_spark_options__(
                            loaded_file["options"]
                        )

        self.update(result)
