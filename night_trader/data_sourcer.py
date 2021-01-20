import csv
import pandas as pd
import threading


class DataSourcer:

    CRYPTO = 'ETH' #ETH, BTC, or LTC?

    eth_history = {}
    quotes = pd.DataFrame(columns=['time', 'price'])
    last_get_index = 0

    def __init__(self, r):
        # self.login = r
        # self.eth_history = self.getHistory(self.CRYPTO, r)
        # if not self.eth_history:
        #     print("no history, exiting")
        #     exit()
        
        # with open('test.csv', 'w', encoding='utf8', newline='') as output_file:
        #     fc = csv.DictWriter(output_file, fieldnames=self.eth_history[0].keys())
        #     fc.writeheader()
        #     fc.writerows(self.eth_history)
        # return
        pass

    # def getHistory(self, crypto_symbol, r) -> list:
    #     print("Gathering historical data...", end='')
    #     history_list = r.crypto.get_crypto_historicals(crypto_symbol, interval='5minute', span='week', bounds='24_7', info=None) #TODO change to 15second

    #     if not history_list:
    #         print("Error in loading history data, system exiting.")
    #         return []
    #     else:
    #         print("done")
    #         return history_list

    def pullNewPrice(self, r):
        new_data_point = {'time': pd.Timestamp.now(), 'price':float(r.crypto.get_crypto_quote(self.CRYPTO, info='mark_price'))}
        self.quotes = self.quotes.append(new_data_point, ignore_index=True)
        print("ETH:", new_data_point['price'])

    def getNewQuotes(self) -> pd.DataFrame:
        to_return = self.quotes[self.last_get_index:]
        self.last_get_index = len(self.quotes)
        return to_return

    def isNewQuotes(self) -> bool:
        return len(self.quotes) > self.last_get_index

    def run(self, r):
        self.pullNewPrice(r)
        threading.Timer(1.0, self.run, [r]).start()
    
    def justGetMostRecentPrice(self) -> float:
        return self.quotes['price'].iloc[-1]
        


