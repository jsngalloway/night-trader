from predictors.bac_daddy import BacDaddy
from predictors.lstm_predictor import Lstm
from predictors.lstm.lstm_data_manager import LstmDataManager


class NightTrader:
    predictor = None
    bought = (False, 0.0)
    sumwin = 0
    CRYPTO = "ETH"
    dataManager: LstmDataManager

    def __init__(self):
        print(
            "---------------------------------- Night Trader ----------------------------------"
        )

        self.dataManager = LstmDataManager(simulation_mode=True)
        self.predictor = Lstm(self.dataManager, 3)
        # self.predictor = BacDaddy(self.dataManager)

    def run(self):
        self.dataManager.incrementEndIndex()

        latest_data = self.updateDataManager()

        self.run_predictor(latest_data)

    def updateDataManager(self) -> dict:
        data = self.dataManager.getData(tail=1, subsampling=1)
        price = data["price"].iloc[-1]
        latest_data = {
            "mark_price": price,
            "ask_price": price + 1,
            "bid_price": price - 1,
        }
        return latest_data

    def run_predictor(self, latest_data: dict):
        current_price = float(latest_data["mark_price"])
        buyable_price = float(latest_data["ask_price"])
        sellable_price = float(latest_data["bid_price"])

        action = self.predictor.predict(current_price)

        if action == "buy":
            if not self.bought[0]:
                self.bought = (True, buyable_price)
        elif action == "sell":
            if self.bought[0]:
                # we have bought and now we should sell
                # sell_success, sell_price = sellAndWait(r)
                sell_success = True
                sell_price = sellable_price
                if sell_success:
                    profit = sell_price - self.bought[1]
                    self.sumwin = self.sumwin + sell_price - self.bought[1]
                    print(
                        "BAC_DADDY: Bought at:",
                        self.bought[1],
                        "Selling at",
                        sell_price,
                        "for Profit:",
                        profit,
                        "TOTAL:",
                        self.sumwin,
                        flush=True,
                    )
                    self.bought = (False, 0)


if __name__ == "__main__":
    # execute only if run as a script
    nt = NightTrader()
    while True:
        nt.run()
