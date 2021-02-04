from trader.cycle.trade.trade import Trade


class Buy(Trade):
    def __init__(self, id: str, price: float, quantity: float):
        Trade.__init__(self, "buy", id, price, quantity)
