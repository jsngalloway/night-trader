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

        log.debug(f"Loading data from dump file...")
        old_data = pd.read_csv("data/dump.csv")

        old_data.columns = ["time", "price"]

        self.data = old_data
        log.debug(f"Load data complete.")

        if simulation_mode:
            self.end_index = 0

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
        df = pd.DataFrame(raw_data)[["begins_at", "open_price"]]
        df = df.rename(columns={"begins_at": "time", "open_price": "price"})

        # it comes in as a string, so convert to numbers
        df["price"] = pd.to_numeric(df["price"])
        log.debug(f"Loaded: {len(current_list)} rows from file")
        log.debug(f"Got: {len(df)} rows from the api just now")
        sum_data = pd.concat([current_list, df])
        log.debug(f"Appended to get: {len(sum_data)} rows")
        sum_data = sum_data[~sum_data[["time"]].duplicated(keep="first")]
        log.info(f"Removing dupes got us: {len(sum_data)} rows")
        return sum_data

    def updateBulk(self):
        self.data = self.appendFromApi(self.data)
        log.debug("Bulk update complete")

    def getQuoteAndAddToData(self) -> dict:
        def getDataNow() -> dict:
            # return r.crypto.get_crypto_quote("ETH")[["ask_price", "mark_price", "bid_price"]]
            url = ("https://api.robinhood.com/marketdata/forex/quotes/{0}/").format(
                ETH_ID
            )
            data = r.helper.request_get(
                url, dataType="regular", payload=None, jsonify_data=True
            )

            if (data == None) or (not type(data) is dict):
              log.error("Unable to fetch data from robinhood")
              log.error(data)
              return None

            return data

        new_data_dict = getDataNow()
        price = float(new_data_dict["mark_price"])
        self.data = self.data.append(
            {"time": datetime.now(), "price": price}, ignore_index=True
        )
        return new_data_dict

    def getData(self, tail, subsampling):
        if self.end_index != None:
            return (self.data[["price"]][: self.end_index : subsampling]).tail(tail)
        else:
            return (self.data[["price"]][::subsampling]).tail(tail)

    def incrementEndIndex(self):
        assert self.end_index != None
        self.end_index += 1
