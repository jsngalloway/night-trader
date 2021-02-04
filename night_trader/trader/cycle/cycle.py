from trader.cycle.trade.buy import Buy
from trader.cycle.trade.sell import Sell
import logging

log = logging.getLogger(__name__)

class Cycle:

  buy: Buy
  sell: Sell
  complete: bool
  profit: float

  def __init__(self, buy_id: str, will_pay: float, quantity: float):
    self.buy = Buy(buy_id, will_pay, quantity)
    self.complete = False
    self.profit = 0.0
    self.sell = None
  
  def saleStarted(self, sell_id: str, sell_price: float, quantity: float):
    self.sell = Sell(sell_id, sell_price, quantity)
  
  def checkAndComplete(self):
    if self.sell and not self.sell.open:
      self.complete = True
      if self.sell.fill_price:
        self.profit = (self.sell.fill_price * self.sell.quantity) - (self.buy.fill_price * self.buy.quantity)
        log.info("Completed cycle with profit of: ", self.profit)

  def cancelCycle(self):
    log.warning("Cancelling trade cycle")
    if self.buy.open:
      log.warning(f"Cancelling buy, ID: {self.buy.id}")
      self.buy.cancel()
    if self.sell and self.sell.open:
      log.warning(f"Cancelling sell, ID: {self.buy.id}")
      self.sell.cancel()
