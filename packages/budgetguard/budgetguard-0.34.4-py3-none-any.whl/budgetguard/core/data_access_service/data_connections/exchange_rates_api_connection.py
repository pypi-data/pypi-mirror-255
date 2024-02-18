from .connection import Connection
from forex_python.converter import CurrencyRates


class ExchangeRatesAPIConnection(Connection):
    def __init__(self) -> None:
        super().__init__()
        self.connection: CurrencyRates = self.connect()

    def connect(self):
        return CurrencyRates()
