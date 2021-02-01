import pandas as pd
from datetime import datetime
from predictors.lstm.lstm_data_manager import LstmDataManager
import logging

import matplotlib.pyplot as plt

plt.style.use('seaborn-darkgrid')

log = logging.getLogger(__name__)

# TODO REMOVE
plt.ion()
fig, axs = plt.subplots(2, figsize=(12.2, 7.5), sharex=True)
plt.xticks(rotation=45)
# Set common labels
axs[0].set_xlabel('Time')
axs[1].set_xlabel('Time')
axs[0].set_ylabel('ETH in USD')
plt.tight_layout()

# ############################

class BacDaddy:

    prices: pd.DataFrame = pd.DataFrame({"price": []})
    dataManager: LstmDataManager
    
    bacd_params = (12, 26, 9)
    period_multiplier = 175  #175  # 25 or 111

    def __init__(self, dataSourcer: LstmDataManager):
        self.dataManager = dataSourcer
        log.info("Bac daddy predictor initialized")
        log.info(f"Parameters: {self.bacd_params}")
        log.info(f"Period multiplier: {self.period_multiplier}")

    def predict(self, latest_price):
        data = self.dataManager.getData(tail=5000, subsampling=1)
        latest_time = str(data.time.iloc[-1])
        latest_price = data.price.iloc[-1]

        # Calculate MACD and signal lines
        exp1 = data[["price"]].ewm(span=self.bacd_params[0] * self.period_multiplier, adjust=False).mean()
        exp2 = data[["price"]].ewm(span=self.bacd_params[1] * self.period_multiplier, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=self.bacd_params[2] * self.period_multiplier, adjust=False).mean()

        data = data.set_index(pd.DatetimeIndex(pd.to_datetime(data['time'].values, utc=True))).tz_convert(tz='US/Eastern')
        macd = macd.set_index(pd.DatetimeIndex(pd.to_datetime(data['time'].values, utc=True))).tz_convert(tz='US/Eastern')
        signal = signal.set_index(pd.DatetimeIndex(pd.to_datetime(data['time'].values, utc=True))).tz_convert(tz='US/Eastern')

        
        # TODO Remove plotting
        plt.rcParams['timezone'] = data.index.tz.zone
        axs[0].clear()
        axs[1].clear()
        axs[0].plot(data.price.tail(1000), label='Price', linewidth=2)
        axs[1].plot(macd.tail(1000), label='ETH MACD', color = 'red', linewidth=1)
        axs[1].plot(signal.tail(1000), label='Signal Line', color='blue', linewidth=1)
        axs[0].grid(b=True, which='both', axis='both')
        plt.draw()
        plt.pause(.001)
        # --------------------------------------

        log.debug(f"Using data ({data.time.iat[0]} {data.time.iat[-1]} : {len(data)})macd is at: {macd.price.iat[-1]} signal is at: {signal.price.iat[-1]}")

        # using the opposite of conventional logic...
        if (macd.price.iat[-1] < signal.price.iat[-1]) and (
            macd.price.iat[-2] >= signal.price.iat[-2]
        ):
            log.info(f"Got BUY signal at [{latest_time}] ${latest_price:.2f}")
            # wanna_buy = data.price.tail(5).mean() + ((data.price.tail(5).mean() - data.price.tail(5).min()) * 0.5)
            # log.info(f"Will attempt to buy at: {wanna_buy}")
            return "buy"
        elif (macd.price.iat[-1] > signal.price.iat[-1]) and (
            macd.price.iat[-2] <= signal.price.iat[-2]
        ):
            log.info(f"Got SELL signal at [{latest_time}] ${latest_price:.2f}")
            # wanna_sell = data.price.tail(5).mean() - ((data.price.tail(5).mean() - data.price.tail(5).max()) * 0.5)
            # log.info(f"Will attempt to sell at: {wanna_sell}")
            return "sell"
        else:
            return None
