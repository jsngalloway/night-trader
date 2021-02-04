import unittest
from night_trader.trader.cycle.cycle import Cycle

class CycleTest(unittest.TestCase):

  def test_init(self):
    c = Cycle("123abc", 45, 10)
    self.assertIsNone(c.sell)
    self.assertEqual(c.buy.id, "123abc")
    self.assertEqual(c.profit, 0)
    self.assertFalse(c.complete)
    c.completeCycle("lol", 345, 10)
    self.assertEqual(c.sell.id, "lol")
    self.assertEqual(c.profit, 300)
    self.assertTrue(c.complete)


if __name__ == '__main__':
    unittest.main()