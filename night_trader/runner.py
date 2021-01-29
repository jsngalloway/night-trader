from predictors.bac_daddy import BacDaddy
import robin_stocks as r
import time
from predictors.wma import Wma
from predictors.lstm_predictor import Lstm
from trader import buyAndWait, sellAndWait
from predictors.lstm.lstm_data_manager import LstmDataManager
import sys


class NightTrader:

    login: dict
    predictor = None
    bought = (False, 0.0)
    sumwin = 0
    CRYPTO = "ETH"
    dataManager: LstmDataManager
    simulation_mode: bool

    def __init__(self, simulation=False):
        print(
            "------------------------------ Night Trader ------------------------------"
        )
        self.simulation_mode = simulation
        if self.simulation_mode:
            print(
                "RUNNING IN SIMULATION MODE. OLD DATA WILL BE USED AND NO TRADES WILL EXECUTE"
            )
        else:
            # Load and read username and password env files
            usernameFile = open("env/username", "r")
            username = usernameFile.read()
            passwordFile = open("env/password", "r")
            password = passwordFile.read()

            print("Logging in...", end="")
            self.login = r.login(username, password)
            if not self.login["access_token"]:
                print("FAILURE")
                print("system exiting.")
                r.authentication.logout()
                exit()
            print("done")

        self.dataManager = LstmDataManager(simulation_mode=self.simulation_mode)

        if not self.simulation_mode:
            self.dataManager.updateBulk()

        # self.predictor = Lstm(self.dataManager, 3)
        self.predictor = BacDaddy(self.dataManager)

    def logout(self):
        # log out of robinhood at the end of the session
        r.authentication.logout()

    def run(self):
        if self.simulation_mode:
            self.dataManager.incrementEndIndex()

        latest_data = self.updateDataManager()

        self.run_predictor(latest_data)

    def updateDataManager(self) -> dict:
        if self.simulation_mode:
            data = self.dataManager.getData(tail=1, subsampling=1)
            price = data["price"].iloc[-1]
            latest_data = {
                "mark_price": price,
                "ask_price": price + 1,
                "bid_price": price - 1,
            }
            return latest_data
        else:
            data = self.dataManager.getQuoteAndAddToData()
            return data

    def run_predictor(self, latest_data: dict):
        current_price = float(latest_data["mark_price"])
        buyable_price = float(latest_data["ask_price"])
        sellable_price = float(latest_data["bid_price"])

        action = self.predictor.predict(current_price)

        if action == "buy":
            if not self.bought[0]:
                # self.bought = buyAndWait(r)
                self.bought = (True, buyable_price)
            else:
                # have already bought: hold
                return
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
    # run with the argument --sim to run in simulation mode
    sim = len(sys.argv) and str(sys.argv[1]) == "--sim"

    nt = NightTrader(simulation=sim)
    while True:
        nt.run()
        if not sim:
            time.sleep(15)

    nt.logout()
