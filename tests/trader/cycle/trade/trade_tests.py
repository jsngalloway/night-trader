import unittest
from night_trader.trader.cycle.trade.buy import Buy
from night_trader.trader.cycle.trade.sell import Sell

class TestTrade(unittest.TestCase):
    # # either 'buy' or 'sell'
    # type: str

    # # the id assigned by robinhood
    # id: str

    # # if the transaction is complete/cancelled or is still somehow pending
    # open: bool

    # # the limit price at which to execute
    # price: float

    # # How much to transact
    # quantity: float

    # # How much it actually went though for
    # fill_price: float

  def test_buy_init(self):
    buy = Buy("123abc", 123.456, 1.0)
    self.assertEqual(buy.type, "buy")
    self.assertEqual(buy.id, "123abc")
    self.assertTrue(buy.open)
    self.assertEqual(buy.price, 123.456)
    self.assertEqual(buy.quantity, 1.0)
    self.assertIsNone(buy.fill_price)

    buy.close(11.0)
    self.assertEqual(buy.fill_price, 11.0)
    self.assertFalse(buy.open)

  def test_sell_init(self):
    sell = Sell("123abc", 123.456, 1.0)
    self.assertEqual(sell.type, "sell")
    self.assertEqual(sell.id, "123abc")
    self.assertTrue(sell.open)
    self.assertEqual(sell.price, 123.456)
    self.assertEqual(sell.quantity, 1.0)
    self.assertIsNone(sell.fill_price)

    sell.close(22)
    self.assertEqual(sell.fill_price, 22)
    self.assertFalse(sell.open)

if __name__ == '__main__':
    unittest.main()