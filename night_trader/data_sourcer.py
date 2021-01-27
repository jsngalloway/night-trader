import csv
import pandas as pd
import threading

from robin_stocks.urls import quotes


class DataSourcer:

    CRYPTO = "ETH"  # ETH, BTC, or LTC?

    eth_history = {}
    quotes = pd.DataFrame(columns=["time", "price"])

    __instance = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if DataSourcer.__instance == None:
            DataSourcer()
        return DataSourcer.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if DataSourcer.__instance != None:
            raise Exception("There can only be one DataSourcer, use getInstance!")
        else:
            DataSourcer.__instance = self

    def pullNewPrice(self, r):
        try:
            query_result = r.crypto.get_crypto_quote(self.CRYPTO, info=None)
        except:
            print("Failed to log")
        else:
            new_data_point = {
                "time": pd.Timestamp.now(),
                "price": float(
                    r.crypto.get_crypto_quote(self.CRYPTO, info=None)["mark_price"]
                ),
            }
            self.quotes = self.quotes.append(new_data_point, ignore_index=True)

    def getFromIndex(self, index: int) -> tuple:
        """returns a list from the requested index to the last index and the newest last index"""
        return (list(self.quotes["price"][index:]), len(self.quotes))

    def getMostRecent(self, how_many: int) -> tuple:
        """the most recent x points"""
        return self.quotes.tail(how_many)

    def run(self, r):
        new_data = self.pullNewPrice(r)
        threading.Timer(15.0, self.run, [r]).start()

    def justGetMostRecentPrice(self) -> float:
        return self.quotes["price"].iloc[-1]

    # def saveQuotesToCsv(self, name_of_file: str):
    #     path = name_of_file + ".csv"
    #     with open('my_csv.csv', 'a') as f:
    #         self.quotes.to_csv(f, header=False, index=False)

    # def appendToCsv(self, name_of_file: str, data_to_append):
    #     path = name_of_file + ".csv"
    #     with open(path, 'a') as f:
    #         self.quotes.to_csv(f, header=False, index=False, line_terminator='', mode='a')
