from datetime import datetime
import pandas as pd
import robin_stocks as r


ETH_ID = "76637d50-c702-4ed1-bcb5-5b0732a81f48"

class LstmDataManager:

    data: pd.DataFrame = None

    def __init__(self):

        print("Loading data from dump file...")
        old_data = pd.read_csv("data/dump.csv")

        old_data.columns = ['time', 'price']

        self.data = old_data

    @staticmethod
    def appendFromApi(current_list):

        def getHourlyHistory() -> dict:
            url = r.urls.crypto_historical(ETH_ID)
            payload = {'interval': "15second",
                        'span': "hour",
                        'bounds': "24_7"}
            data = r.helper.request_get(url, 'regular', payload)
            return data['data_points']

        # raw_data = r.crypto.get_crypto_historicals("ETH", interval='15second', span='hour', bounds='24_7', info=None)
        raw_data = getHourlyHistory()
        df = pd.DataFrame(raw_data)[["begins_at", "open_price"]]
        df = df.rename(columns={"begins_at":"time", "open_price":"price"})

        #it comes in as a string, so convert to numbers
        df['price'] = pd.to_numeric(df['price'])
        
        sum_data = pd.concat([current_list, df])
        sum_data = sum_data[~sum_data[["time"]].duplicated(keep='first')]
        return sum_data

    def updateBulk(self):
        self.data = self.appendFromApi(self.data)

    def getQuoteAndAddToData(self) -> dict:

        def getDataNow() -> dict:
            # return r.crypto.get_crypto_quote("ETH")[["ask_price", "mark_price", "bid_price"]]
            url = ('https://api.robinhood.com/marketdata/forex/quotes/{0}/').format(ETH_ID)
            data = r.helper.request_get(url, dataType='regular', payload=None, jsonify_data=True)
            return data

        new_data_dict = getDataNow()
        price = float(new_data_dict['mark_price'])
        self.data = self.data.append({'time': datetime.now(), 'price':price}, ignore_index=True)
        return new_data_dict


    def getData(self, tail=90, subsampling=4):
        return (self.data[['price']][::subsampling]).tail(tail)
    
    # @staticmethod
    # def getRightNowValue() -> float:
    #     return float(r.crypto.get_crypto_quote("ETH", info=None)["mark_price"])