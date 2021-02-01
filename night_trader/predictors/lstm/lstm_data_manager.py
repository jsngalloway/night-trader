from datetime import datetime
import pandas as pd
import robin_stocks as r
import time
import logging

ETH_ID = "76637d50-c702-4ed1-bcb5-5b0732a81f48"

log = logging.getLogger(__name__)

class LstmDataManager:

    data: pd.DataFrame = None

    # Used for simulation only
    end_index = None

    def __init__(self, simulation_mode=False):
        log.info(f"Initializing LstmDataManager. Simulation mode: {simulation_mode}")

        log.info(f"Loading data from dump file...")
        old_data = pd.read_csv("data/ETH.csv")

        # old_data.columns = ["time", "price"]
        self.data = self.averageAndRename(old_data)



        # self.data = old_data
        log.info(f"Load data complete: {len(self.data)} rows loaded. Latest row time: {self.data.time.iat[-1]}")

        if simulation_mode:
            self.end_index = 500 #start with 500 samples

    @staticmethod
    def averageAndRename(begin_high_low_dataFrame: pd.DataFrame):
        new_dataFrame = pd.DataFrame()
        new_dataFrame['price'] = begin_high_low_dataFrame[['high_price','low_price']].mean(axis=1)
        new_dataFrame['time'] = begin_high_low_dataFrame['begins_at']
        new_dataFrame = new_dataFrame.set_index(pd.DatetimeIndex(begin_high_low_dataFrame['begins_at'].values))
        return new_dataFrame

    @staticmethod
    def appendFromApi(current_list):
        
        def getHourlyHistory() -> dict:
            url = r.urls.crypto_historical(ETH_ID)
            payload = {"interval": "15second", "span": "hour", "bounds": "24_7"}
            data = r.helper.request_get(url, "regular", payload)

            if (
                (not data)
                or (not type(data) is dict)
                or (data.get("data_points") == None)
            ):
                log.error(f"Invalid response, trying again in 60 seconds.")
                time.sleep(60)
                return getHourlyHistory()

            return data["data_points"]

        # raw_data = r.crypto.get_crypto_historicals("ETH", interval='15second', span='hour', bounds='24_7', info=None)
        log.info("Getting past hourly data...")
        raw_data = getHourlyHistory()

        data = pd.DataFrame(raw_data)
        data["high_price"] = pd.to_numeric(data['high_price'])
        data["low_price"] = pd.to_numeric(data['low_price'])
        data["begins_at"] = pd.to_datetime(data['begins_at'])
        
        df = LstmDataManager.averageAndRename(data)
        # df = pd.DataFrame(raw_data)[["begins_at", "open_price"]]
        # df = df.rename(columns={"begins_at": "time", "open_price": "price"})

        # it comes in as a string, so convert to numbers
        # df["price"] = pd.to_numeric(df["price"])
        log.info(f"Loaded: {len(current_list)} rows from file")
        log.info(f"Got: {len(df)} rows from the api just now")
        sum_data = pd.concat([current_list, df], ignore_index=True)
        log.info(f"Appended to get: {len(sum_data)} rows")
        sum_data = sum_data[~sum_data[["time"]].duplicated(keep="first")]
        log.info(f"Removing dupes got us: {len(sum_data)} rows")
        return sum_data

    def updateBulk(self):
        self.data = self.appendFromApi(self.data)
        log.info("Bulk update complete")
        # print(self.data.head(250))
        # print(self.data.tail(250))

    def getQuoteAndAddToData(self) -> dict:
        def getDataNow() -> dict:
            # return r.crypto.get_crypto_quote("ETH")[["ask_price", "mark_price", "bid_price"]]
            url = ("https://api.robinhood.com/marketdata/forex/quotes/{0}/").format(
                ETH_ID
            )
            data = r.helper.request_get(
                url, dataType="regular", payload=None, jsonify_data=True
            )
            time_string = (datetime.utcnow()).strftime("%Y-%m-%dT%H:%M:%SZ")
            data["time"] =  time_string

            if (data == None) or (not type(data) is dict):
              log.error("Unable to fetch data from robinhood")
              log.error(data)
              return None

            # print(self.data.tail(5))

            return data

        new_data_dict = getDataNow()
        price = float(new_data_dict["mark_price"])
        time_string = new_data_dict["time"]
        self.data = self.data.append(
            {"time": time_string, "price": price}, ignore_index=True
        )
        return new_data_dict

    def getData(self, tail, subsampling):
        if self.end_index != None:
            return (self.data.iloc[: self.end_index]).tail(tail)
        else:
            return (self.data).tail(tail)

    def incrementEndIndex(self):
        assert self.end_index != None
        self.end_index += 1
