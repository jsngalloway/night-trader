import pandas as pd
from datetime import datetime
from predictors.lstm.lstm_data_manager import LstmDataManager
import logging

log = logging.getLogger(__name__)

class BacDaddy:

    prices: pd.DataFrame = pd.DataFrame({"price": []})
    dataManager: LstmDataManager
    
    bacd_params = (12, 26, 9)
    period_multiplier = 5  # 25 or 111

    def __init__(self, dataSourcer: LstmDataManager):
        self.dataManager = dataSourcer
        log.info("Bac daddy predictor initialized")
        log.debug(f"Parameters: {self.bacd_params}")
        log.debug(f"Period multiplier: {self.period_multiplier}")

    def predict(self, latest_price):
        prices = self.dataManager.getData(tail=5000, subsampling=1)

        # Calculate MACD and signal lines
        exp1 = prices.ewm(span=self.bacd_params[0] * self.period_multiplier, adjust=False).mean()
        exp2 = prices.ewm(span=self.bacd_params[1] * self.period_multiplier, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=self.bacd_params[2] * self.period_multiplier, adjust=False).mean()

        # using the opposite of conventional logic...
        if (macd.iat[-1, 0] < signal.iat[-1, 0]) and (
            macd.iat[-2, 0] >= signal.iat[-2, 0]
        ):
            log.debug(f"Got buying signal at ${latest_price:.2f}")
            return "buy"
        elif (macd.iat[-1, 0] > signal.iat[-1, 0]) and (
            macd.iat[-2, 0] <= signal.iat[-2, 0]
        ):
            log.debug(f"Got Selling signal at ${latest_price:.2f}")
            return "sell"
        else:
            return None
