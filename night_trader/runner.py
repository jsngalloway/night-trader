import robin_stocks as r
import time
import threading
from data_sourcer import DataSourcer
from data_manager import DataManager
from predictors.wma import Wma
from predictors.lstm_predictor import Lstm
from predictors.mac_daddy import MacDaddy
from trader import buyAndWait, sellAndWait
from predictors.lstm.lstm_data_manager import LstmDataManager
from tqdm import tqdm


class NightTrader:

    login: dict
    predictor = None
    # predictorMacDaddy = None
    # dataSourcer: DataSourcer
    bought = (False, 0.0)
    # boughtMacDaddy = (False, 0.0)
    sumwin = 0
    # sumwinMacDaddy = 0
    CRYPTO = "ETH"
    dataManager: LstmDataManager

    run_count = 0
    model_interval = 3 # 3*15 seconds between samples

    def __init__(self):
        print(
            "---------------------------------- Night Trader ----------------------------------"
        )
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

        # buying_power = r.profiles.load_account_profile(info="crypto_buying_power")
        # print("Crypto Buying Power: ", buying_power)

        self.dataManager = LstmDataManager()
        self.predictor = Lstm(self.dataManager)
        self.dataManager.updateBulk()

    def logout(self):
        # print(r.crypto.get_crypto_positions())
        # log out of robinhood at the end of the session
        r.authentication.logout()

    def run(self):
        self.run_count = self.run_count + 1

        latest_data = self.updateDataManager()

        if self.run_count % self.model_interval == 0:
            self.run_predictor(latest_data)

    def updateDataManager(self) -> dict:
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
        else:
            if self.bought[0]:
                # we have bought and now we should sell
                # sell_success, sell_price = sellAndWait(r)
                sell_success = True
                sell_price = sellable_price
                if sell_success:
                    profit = sell_price - self.bought[1]
                    self.sumwin = self.sumwin + sell_price - self.bought[1]
                    print(
                        "LSTM: Bought at:",
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
            else:
                return


if __name__ == "__main__":
    # execute only if run as a script
    nt = NightTrader()
    while True:
        nt.run()
        time.sleep(15)

    nt.logout()
