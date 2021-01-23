import robin_stocks as r
import time
import threading
from data_sourcer import DataSourcer
from data_manager import DataManager
from predictors.wma import Wma
from predictors.mac_daddy import MacDaddy

class NightTrader():

    login: dict
    predictor = None
    predictorMacDaddy = None
    dataSourcer: DataSourcer
    bought = (False, 0.0)
    boughtMacDaddy = (False, 0.0)
    sumwin = 0
    sumwinMacDaddy = 0

    def __init__(self):
        print("---------------------------------- Night Trader ----------------------------------")
        # Load and read username and password env files
        usernameFile = open("env/username", "r")
        username = usernameFile.read()
        passwordFile = open("env/password", "r")
        password = passwordFile.read()

        print("Logging in...", end='')
        self.login = r.login(username, password)
        if not self.login["access_token"]:
            print("FAILURE")
            print("system exiting.")
            r.authentication.logout()
            exit()
        print("done")

        # Initialize and execute the data sourcer, it's a singleton
        self.dataSourcer = DataSourcer.getInstance()
        self.dataSourcer.run(r)

        self.predictor = Wma(self.dataSourcer)
        self.predictorMacDaddy = MacDaddy(self.dataSourcer)

    def logout(self):
        # print(r.crypto.get_crypto_positions())
        # log out of robinhood at the end of the session
        r.authentication.logout()
    
    def run(self):
        # self.data_source.printPriceHistory()
        # if len(self.data_source.getData()) > 15:
        action = self.predictor.predict()
        if action:
            current_price = self.dataSourcer.justGetMostRecentPrice()
            if action == "buy" and not self.bought[0]:
                self.bought = (True, current_price)
            elif action == "sell" and self.bought[0]:
                profit = float(current_price) - float(self.bought[1], )
                self.sumwin = self.sumwin + current_price - self.bought[1]
                print("WMA: Bought at:", float(self.bought[1]), "Selling at",current_price, " for Profit: ", profit, " TOTAL: ", self.sumwin)
                self.bought = (False, 0)
        
        action = self.predictorMacDaddy.predict()
        if action:
            current_price = self.dataSourcer.justGetMostRecentPrice()
            if action == "buy" and not self.boughtMacDaddy[0]:
                self.boughtMacDaddy = (True, current_price)
            elif action == "sell" and self.boughtMacDaddy[0]:
                profit = float(current_price) - float(self.boughtMacDaddy[1], )
                self.sumwinMacDaddy = self.sumwinMacDaddy + current_price - self.boughtMacDaddy[1]
                print("MacDaddy: Bought at:", float(self.boughtMacDaddy[1]), "Selling at",current_price, " for Profit: ", profit, " TOTAL: ", self.sumwinMacDaddy)
                self.boughtMacDaddy = (False, 0)


if __name__ == "__main__":
    # execute only if run as a script
    nt = NightTrader()
    while(True):
        nt.run()
        time.sleep(0.02)
    nt.logout()