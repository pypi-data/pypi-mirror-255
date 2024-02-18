import sys
import os
from loguru import logger
from pyspark.sql import Row, DataFrame as SparkDataFrame
import pyspark.sql.functions as F

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

    def transform(self, source_df: SparkDataFrame) -> SparkDataFrame:
        """
        Transforms the data.

        :param source_df: The data to transform.
        :return: The transformed data.
        """
        logger.info("Transforming data.")
        currency_rates = self.__get_currency_rates__()
        currency_rates_df = self.input_loader.spark_s3_connection.spark_session.createDataFrame(  # noqa: E501
            Row(currency=currency, rate=rate)
            for currency, rate in currency_rates.items()
        )
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
                F.round(source_df.balance_amount * currency_rates.rate, 2),
            )
            .drop("rate", "currency")
        )
        return transformed_df
