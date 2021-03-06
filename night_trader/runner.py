from typing import Union

from predictors.bac_daddy import BacDaddy
from predictors.mac_daddy import MacDaddy

from predictors.strategy_wrapper import StrategyWrapper
from strategies.strategy_waiting_game import StrategyWaiter

import robin_stocks as r
import time
from predictors.lstm_predictor import Lstm
from trader.trader import Trader
from sim_trader import SimTrader
from predictors.lstm.lstm_data_manager import LstmDataManager
import sys
import logging
import threading

# Set up logging format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("debug.log"), logging.StreamHandler()],
)

log = logging.getLogger(__name__)


class NightTrader:

    predictor = None
    bought = (False, 0.0, None)
    sumwin = 0
    CRYPTO = "ETH"
    dataManager: LstmDataManager
    simulation_mode: bool
    trader: Union[Trader, SimTrader]

    def __init__(self, simulation=False):
        log.info(
            "------------------------------ Night Trader ------------------------------"
        )
        log.info(f"Initializing night-trader. Simulation mode: {simulation}")

        self.simulation_mode = simulation
        if self.simulation_mode:
            log.warning(
                "RUNNING IN SIMULATION MODE. OLD DATA WILL BE USED AND NO TRADES WILL EXECUTE"
            )
        else:
            # Load and read username and password env files
            log.info("Loading username and password from files")
            usernameFile = open("env/username", "r")
            username = usernameFile.read()
            passwordFile = open("env/password", "r")
            password = passwordFile.read()

            log.info("Authenticating with robinhood...")
            login = r.login(username, password)
            if (not login) or (not isinstance(login, dict)) or (not login["access_token"]):
                log.error("Unable to authenticate, exiting.")
                r.authentication.logout()
                exit()
            log.info("Authentication complete.")

        self.dataManager = LstmDataManager(simulation_mode=self.simulation_mode)

        if not self.simulation_mode:
            self.dataManager.updateBulk()
            self.trader = Trader(self.CRYPTO, 0.05)
        else:
            self.trader = SimTrader(self.CRYPTO, 0.05)

        # self.predictor = Lstm(self.dataManager, 3)
        # self.predictor = BacDaddy(self.dataManager)
        # self.predictor = MacDaddy(self.dataManager)
        self.predictor = StrategyWrapper(self.dataManager, StrategyWaiter())

    def logout(self):
        # log out of robinhood at the end of the session
        r.authentication.logout()

    def run(self):
        if self.simulation_mode:
            self.dataManager.incrementEndIndex()

        latest_data = self.updateDataManager()

        if latest_data == None:
            log.error("No data was received, skipping prediction iteration")
            return
        else:
            self.run_predictor(latest_data)

    def updateDataManager(self) -> dict:
        if self.simulation_mode:
            data = self.dataManager.getData(tail=1, subsampling=1)
            price = data['price'].iat[-1]
            time = str(data[["time"]].iloc[-1, 0])
            latest_data = {
                "mark_price": price,
                "ask_price": price + 1,
                "bid_price": price - 1,
                "time": time,
            }
            return latest_data
        else:
            # Watch out, this can return None if the request failed (3:30 bug)
            data = self.dataManager.getQuoteAndAddToData()
            return data

    def run_predictor(self, latest_data: dict):
        current_price = float(latest_data["mark_price"])
        buyable_price = float(latest_data["ask_price"])
        sellable_price = float(latest_data["bid_price"])
        current_time = latest_data["time"]

        # action = self.predictor.predict(current_price)

        if (not self.bought[0]) and self.predictor.buy():
            # self.trader.buy(buyable_price)
            self.trader.buy(current_price)
            self.bought = (True, buyable_price, current_time)

        elif self.bought[0] and self.predictor.sell(current_price, self.bought[1], current_time, self.bought[2]):
            # self.trader.sell(sellable_price)
            self.trader.sell(current_price)
            self.bought = (False, 0, None)

        if (
            (not self.bought[0])
            and self.trader.getProfit()
            and self.sumwin != self.trader.getProfit()
        ):
            new_profits = self.trader.getProfit()
            log.info(
                f"Current profits: {(new_profits - self.sumwin):+.2f} Total: {new_profits} ({len(self.trader.cycles)} cycles)"
            )
            self.sumwin = new_profits


if __name__ == "__main__":
    # run with the argument --sim to run in simulation mode
    sim = len(sys.argv) == 2 and str(sys.argv[1]) == "--sim"

    nt = NightTrader(simulation=sim)
    # schedule.every(15).seconds.do(nt.run)
    while True:
        nt.run()
        # schedule.run_pending()
        if not sim:
            time.sleep(15)

    # nt.logout()
