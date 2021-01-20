import robin_stocks as r
import time
import threading
from data_sourcer import DataSourcer
from predictors.wma import Wma

class NightTrader():

    login: dict
    predictor = None
    dataSourcer: DataSourcer
    bought = (False, 0.0)
    sumwin = 0

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


        self.dataSourcer = DataSourcer(r)
        self.dataSourcer.run(r)

        self.predictor = Wma(self.dataSourcer)        

    def logout(self):
        # print(r.crypto.get_crypto_positions())
        # log out of robinhood at the end of the session
        r.authentication.logout()
    
    def run(self):
        # self.data_source.printPriceHistory()
        # if len(self.data_source.getData()) > 15:
        slope = self.predictor.predict()
        current_price = self.dataSourcer.justGetMostRecentPrice()
        if slope > 0.005 and not self.bought[0]:
            self.bought = (True, current_price)
            print("bought at", current_price)

        # sell if going down or have lost $10 already
        if (slope < -0.001 and self.bought[0]) or (self.bought[1] - current_price > 10):
            profit = float(current_price) - float(self.bought[1])
            print("Selling at",current_price, " for Profit: ", profit)
            self.sumwin = self.sumwin + current_price - self.bought[1]
            self.bought = (False, 0)
            print("Total profit:", self.sumwin)


if __name__ == "__main__":
    # execute only if run as a script
    nt = NightTrader()
    while(True):
        nt.run()
        time.sleep(5)
    nt.logout()