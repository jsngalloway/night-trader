from predictors.bac_daddy import BacDaddy
from predictors.mac_daddy import MacDaddy
import robin_stocks as r
import time
import schedule
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

    login: dict
    predictor = None
    bought = (False, 0.0)
    sumwin = 0
    CRYPTO = "ETH"
    dataManager: LstmDataManager
    simulation_mode: bool
    trader: Trader

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
            self.login = r.login(username, password)
            if not self.login["access_token"]:
                log.error("Unable to authenticate, exiting.")
                r.authentication.logout()
                exit()
            log.info("Authentication complete.")

        self.dataManager = LstmDataManager(simulation_mode=self.simulation_mode)

        if not self.simulation_mode:
            self.dataManager.updateBulk()

        self.trader = SimTrader(self.CRYPTO, 0.05)

        # self.predictor = Lstm(self.dataManager, 3)
        self.predictor = BacDaddy(self.dataManager)
        # self.predictor = MacDaddy(self.dataManager)

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
            price = data["price"].iloc[-1]
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

        action = self.predictor.predict(current_price)

        if action == "buy":
            if not self.bought[0]:
                self.trader.buy(buyable_price)
                self.bought = (True, buyable_price)
        elif action == "sell":
            if self.bought[0]:
                # we have bought and now we should sell
                self.trader.sell(sellable_price)
                # sell_success = True
                # sell_price = sellable_price
                # if sell_success:
                # profit = sell_price - self.bought[1]
                # self.sumwin = self.sumwin + sell_price - self.bought[1]
                # log.info(f"BAC_DADDY: {[current_time]} Bought at: {self.bought[1]:.3f} Selling at {sell_price:.3f} for Profit: {profit:.3f} TOTAL: {self.sumwin:.3f}")
                self.bought = (False, 0)

        if (
            (not self.bought[0])
            and self.trader.getProfit()
            and self.sumwin != self.trader.getProfit()
        ):
            new_profits = self.trader.getProfit()
            log.info(
                f"Current profits: {(new_profits - self.sumwin):+.2f} Total: {new_profits}"
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
          time.sleep( 15)

    # nt.logout()
