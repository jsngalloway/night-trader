from typing import List, Tuple
from datetime import datetime
import robin_stocks as r
import logging
from trader.cycle.cycle import Cycle

# A transaction can be:
# filled
# cancelled
# open
# partially-filled?

log = logging.getLogger(__name__)


class Trader:

    EXCH_QUANT: float
    SYMBOL: str
    cycles: list

    def __init__(self, symbol: str, exch_quantity: float):
        self.cycles = []
        self.SYMBOL = symbol
        self.EXCH_QUANT = exch_quantity

    def getProfit(self):
        profit = 0
        for c in self.cycles:
            if not c.complete:
                c.checkAndComplete()  # Forces cycles to be updated with sales
            profit += c.profit
        return profit

    def buy(self, max_buy_price):
        if self.cycles and not self.cycles[-1].complete:
            # If the list has content and the most recent one is not finished, we need to cancel that cycle
            self.cycles[-1].cancelCycle()

        will_pay = round(max_buy_price, 2)

        # TODO this should be a try catch probably
        buy_info = r.orders.order_buy_crypto_limit(
            self.SYMBOL, self.EXCH_QUANT, will_pay
        )

        if buy_info and ("id" in buy_info):
            cycle = Cycle(buy_info["id"], will_pay, self.EXCH_QUANT)
            self.cycles.append(cycle)
        else:
            log.error("Unknown return on buy attempt")
            log.error(buy_info)

    def sell(self, min_sell_price):
        if not self.cycles:
            # If the cycles list is empty this is an issue
            log.error("Attempting to sell when nothing has been bought. Aborting sale.")
            return

        current_cycle = self.cycles[-1]

        # If the buy is still open just cancel that, otherwise sell
        if current_cycle.buy.open:
            current_cycle.cancelCycle()
        else:
            will_get = round(min_sell_price, 2)
            # TODO should be in a try catch
            buy_info = r.orders.order_sell_crypto_limit(
                self.SYMBOL, self.EXCH_QUANT, will_get
            )

            if buy_info and ("id" in buy_info):
                current_cycle.saleStarted(buy_info["id"], will_get, self.EXCH_QUANT)
            else:
                log.error("Unknown return on sell attempt")
                log.error(buy_info)
