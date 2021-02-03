import logging
import robin_stocks as r
import threading

log = logging.getLogger(__name__)

class Trade:

  # either 'buy' or 'sell'
  type: str
  
  # the id assigned by robinhood
  id: str

  # if the transaction is complete/cancelled or is still somehow pending
  open: bool

  # the limit price at which to execute
  price: float

  # How much to transact
  quantity: float

  # How much it actually went though for
  fill_price: float

  def __init__(self, type: str, id: str, price: float, quantity: float):
    self.type = type
    self.id = id
    self.price = price
    self.quantity = quantity
    self.open = True
    self.fill_price = None
    log.info(f"Trade Opened. Type: {self.type}, Id: {self.id}, Limit price: {self.price}")
    # Check if order has been completed in 1 seconds
    threading.Timer(1.0, self.checkStatus).start()

  def close(self, fill_price):
    self.open = False
    self.fill_price = fill_price
    log.info(f"Trade Closed. Type: {self.type}, Id: {self.id}, Filled at: {self.fill_price}")

  def checkStatus(self):
    order_info = r.orders.get_crypto_order_info(self.id)
    if order_info:
      if order_info["state"] == "filled":
        self.close(float(order_info["average_price"]))
      elif order_info["state"] == "canceled":
        # If the order is cancelled, we has no fill_price
        self.close(None)
      else:
        # Schedule another check in 5 seconds
        threading.Timer(5.0, self.checkStatus).start()
    else:
      # Bad response from robinhood, try again
      threading.Timer(5.0, self.checkStatus).start()

  def cancel(self):
    log.warn(f"Cancelling {self.type} order {self.id}")
    self.checkStatus()
    if self.open:
      r.orders.cancel_crypto_order(self.id)
    else:
      log.warn(f"Aborting cancel, order {self.id} closed at ${self.fill_price}")
