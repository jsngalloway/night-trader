import time
from typing import Tuple
import numpy as np
from datetime import datetime
import robin_stocks as r
import logging
from trade import Trade

# A transaction can be:
# filled
# cancelled
# open
# partially-filled?

log = logging.getLogger(__name__)
EXCH_QUANT = 0.05
SYMBOL = "ETH"
class Trader:

  # This will serve as a list of ids for orders we're working on
  buys: list
  sells: list

  def __init__(self):

    self.buys = []
    self.sells = []

  # def checkForOpenOrders(self) -> Tuple(list, list):
  #   open_buys = []
  #   open_sells = []
  #   all_opens_orders = r.get_all_open_crypto_orders()
  #   for order in all_opens_orders:
  #     if order['id'] in self.buys:
  #       open_buys.append(order['id'])
  #     if order['id'] in self.sells:
  #       open_sells.append(order['id'])
  #   print("Open Crypto Orders I've placed (buys/sells)", open_buys, open_sells)
  #   return (open_buys, open_sells)

  def buy(self, max_buy_price):
      self.cancelOpenSells()

      will_pay = round(max_buy_price, 2)
      buy_info = r.orders.order_buy_crypto_limit(SYMBOL, EXCH_QUANT, will_pay)
      trade = Trade('buy', buy_info["id"], will_pay, EXCH_QUANT)
      self.buys.append(trade)

  def sell(self, min_sell_price):
      self.cancelOpenSells()
      
      will_get = round(min_sell_price, 2)
      buy_info = r.orders.order_sell_crypto_limit(SYMBOL, EXCH_QUANT, will_get)
      trade = Trade('sell', buy_info["id"], will_get, EXCH_QUANT)
      self.sells.append(trade)

  def cancelOpenBuys(self):
    open_buys = []
    for buy in self.buys:
      if buy.open:
        open_buys.append(buy)
    log.warning(f"Cancelling buy orders ({len(open_buys)})")
    for trade in open_buys:
      trade.cancel()

  def cancelOpenSells(self):
    open_sells = []
    for trade in self.sells:
      if trade.open:
        open_sells.append(trade)
    log.warning(f"Cancelling sell orders ({len(open_sells)})")
    for trade in open_sells:
      trade.cancel()
