import sys
import os
from loguru import logger
from pyspark.sql import DataFrame as SparkDataFrame

here = os.path.dirname(__file__)

sys.path.append(os.path.join(here, ".."))

from .bronze_to_silver_pipeline import BronzeToSilverPipeline  # noqa: E402


class BronzeToSilverDetailsPipeline(BronzeToSilverPipeline):
    INPUT_DATA_LOADER = "spark_s3"
    OUTPUT_DATA_LOADER = "spark_s3"
    INPUT_LAYER = "bronze"
    OUTPUT_LAYER = "silver"
    INPUT_KEY = "details"
    OUTPUT_KEY = "details"

    def transform(self, source_df: SparkDataFrame) -> SparkDataFrame:
        """
        Transforms the data.

        :param source_df: The data to transform.
        :return: The transformed data.
        """
        logger.info("Transforming data.")
        transformed_df = source_df
        return transformed_df
