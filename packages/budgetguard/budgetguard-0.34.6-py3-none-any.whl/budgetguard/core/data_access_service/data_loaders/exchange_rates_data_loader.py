import sys
import os
from loguru import logger
from datetime import datetime
from typing import Dict, List, Union

here = os.path.dirname(__file__)

sys.path.append(os.path.join(here, ".."))

from .data_loader import DataLoader  # noqa: E402
from ..data_connections import connect  # noqa: E402


class ExchangeRatesDataLoader(DataLoader):
    NAME: str = "exchange_rates"

    def __init__(self):
        """
        Constructor for ExchangeRatesDataLoader class.
        """
        self.currency_rates_api_connection = connect(self.NAME).connection

    def read(
        self, partition_id: str = None, base_currency: str = "PLN"
    ) -> List[Dict[str, Union[str, float]]]:
        """
        Method for reading data from the exchange rates API.
        """
        logger.info("Reading data from exchange rates API...")
        output = {}
        if partition_id:
            partition_id = datetime(
                int(partition_id[:4]),
                int(partition_id[4:6]),
                int(partition_id[6:]),
            )
        currencies = self.currency_rates_api_connection.get_rates(
            base_currency, date_obj=partition_id
        )
        output = []
        for currency, rate in currencies.items():
            currency_map = {
                "currency": currency,
                "rate": rate,
            }
            output.append(currency_map)
        output.append(
            {
                "currency": base_currency,
                "rate": 1,
            }
        )
        logger.info("Finished reading {0} exchange rates!".format(len(output)))
        return output

    def write(self):
        """
        Method for writing data to the exchange rates API.
        """
        raise NotImplementedError(
            "Exchange rates data loader doesn't support writing data."
        )
