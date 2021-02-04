from typing import Tuple
import numpy as np
from datetime import datetime
import robin_stocks as r
import logging

# A transaction can be:
# filled
# cancelled
# open
# partially-filled?

log = logging.getLogger(__name__)


class SimTrader:

    profits: float
    pending: float

    def __init__(self, symbol: str, exch_quantity: float):

        self.profits = 0
        self.pending = 0

    def getProfit(self):
        return self.profits

    def buy(self, max_buy_price):
        log.info(f"Sim BUY at {max_buy_price}")
        self.pending = max_buy_price

    def sell(self, min_sell_price):
        log.info(f"Sim SELL at {min_sell_price}")
        self.profits += min_sell_price - self.pending
