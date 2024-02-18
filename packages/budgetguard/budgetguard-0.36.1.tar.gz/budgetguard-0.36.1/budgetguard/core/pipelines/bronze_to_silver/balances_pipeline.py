import sys
import os
from loguru import logger
from pyspark.sql import DataFrame as SparkDataFrame
import pyspark.sql.functions as F
from typing import Tuple

here = os.path.dirname(__file__)

sys.path.append(os.path.join(here, ".."))

from .bronze_to_silver_pipeline import BronzeToSilverPipeline  # noqa: E402


class BronzeToSilverBalancesPipeline(BronzeToSilverPipeline):
    INPUT_DATA_LOADER = "spark_s3"
    OUTPUT_DATA_LOADER = "spark_s3"
    INPUT_LAYER = "bronze"
    OUTPUT_LAYER = "silver"
    INPUT_KEY = "balances"
    OUTPUT_KEY = "balances"

    def read_source_exchange_rates(self) -> SparkDataFrame:
        """
        Reads the exchange rates from the data sources.

        :return: The exchange rates from the data sources.
        """
        logger.info("Reading exchange rates from datalake.")
        exchange_rates_df = self.input_loader.read(
            self.datalake["master"]["exchange_rates"],
            {"partition_id": self.partition_id},
        )
        return exchange_rates_df

    def read_sources(self) -> Tuple[SparkDataFrame, SparkDataFrame]:
        """
        Reads the data from the data sources.

        :return: The data from the data sources.
        """
        logger.info("Reading data from datalake.")
        source_df = self.input_loader.read(
            self.datalake[self.INPUT_LAYER][self.INPUT_KEY],
            {
                "partition_id": self.partition_id,
            },
        )
        currency_rates_df = self.read_source_exchange_rates()
        return source_df, currency_rates_df

    def transform(
        self, source_df: SparkDataFrame, currency_rates_df: SparkDataFrame
    ) -> SparkDataFrame:
        """
        Transforms the data.

        :param source_df: The data to transform.
        :return: The transformed data.
        """
        logger.info("Transforming data.")
        transformed_df = self.convert_currencies(source_df, currency_rates_df)
        transformed_df = transformed_df.toDF(
            *[
                "amount",
                "currency",
                "type",
                "partition_id",
                "account_id",
                "amount_PLN",
            ]
        )
        return transformed_df

    def convert_currencies(
        self,
        source_df: SparkDataFrame,
        currency_rates: SparkDataFrame,
        base_currency: str = "PLN",
    ) -> SparkDataFrame:
        """
        Converts currencies.

        :param source_df: The data to transform.
        :param currency_rates: The currency rates.
        :return: The transformed data.
        """
        logger.info("Converting currencies.")
        transformed_df = (
            source_df.join(
                currency_rates,
                source_df.balance_currency == currency_rates.currency,
                "left",
            )
            .withColumn(
                f"amount_{base_currency}",
                F.round(source_df.balance_amount / currency_rates.rate, 2),
            )
            .drop("rate", "currency")
        )
        return transformed_df

    def run(self):
        """
        Runs the pipeline.
        """
        logger.info("Running the bronze to silver pipeline...")
        source_df, currency_rates_df = self.read_sources()
        transformed_df = self.transform(source_df, currency_rates_df)
        self.write_sources(transformed_df)
