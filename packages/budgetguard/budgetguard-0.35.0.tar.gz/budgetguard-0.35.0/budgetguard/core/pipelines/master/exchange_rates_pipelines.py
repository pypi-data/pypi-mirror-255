import sys
import os
from typing import Dict, List, Union
from loguru import logger
import json

here = os.path.dirname(__file__)

sys.path.append(os.path.join(here, ".."))

from ..pipeline import Pipeline  # noqa: E402
from ...datalake import Datalake  # noqa: E402
from ...data_access_service.data_loaders import (  # noqa: E402
    create_data_loader,
)


class ExchangeRatesPipeline(Pipeline):
    INPUT_DATA_LOADER = "exchange_rates"
    OUTPUT_DATA_LOADER = "s3"
    OUTPUT_LAYER = "master"
    OUTPUT_KEY = "exchange_rates"

    def __init__(self, partition_id: str) -> None:
        self.datalake = Datalake()
        self.partition_id = partition_id
        self.input_loader = create_data_loader(self.INPUT_DATA_LOADER)
        self.output_loader = create_data_loader(self.OUTPUT_DATA_LOADER)

    def read_sources(self) -> List[Dict[str, Union[str, float]]]:
        """
        Reads the data from the data sources.

        :return: The data from the data sources.
        """
        logger.info("Reading data from datalake.")
        source_data = self.input_loader.read(self.partition_id)
        return source_data

    def write_sources(
        self, transformed_data: List[Dict[str, Union[str, float]]]
    ):
        """
        Writes the data to the data sources.

        :param transformed_df: The transformed data.
        """
        logger.info("Writing data to datalake.")
        self.output_loader.write(
            json.dumps(transformed_data),
            self.datalake[self.OUTPUT_LAYER][self.OUTPUT_KEY],
            {"partition_id": self.partition_id},
        )

    def transform(
        self, data: List[Dict[str, Union[str, float]]]
    ) -> List[Dict[str, Union[str, float]]]:
        """
        Transforms the data.

        :param data: The data to transform.
        :return: The transformed data.
        """
        logger.info("Transforming data.")
        return data

    def run(self):
        """
        Runs the pipeline.
        """
        data = self.read_sources()
        transformed_data = self.transform(data)
        self.write_sources(transformed_data)
