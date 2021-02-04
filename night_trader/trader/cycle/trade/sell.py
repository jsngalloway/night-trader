from trader.cycle.trade.trade import Trade


class Sell(Trade):
    def __init__(self, id: str, price: float, quantity: float):
        Trade.__init__(self, "sell", id, price, quantity)
