import pandas as pd
from datetime import datetime
from predictors.lstm.lstm_data_manager import LstmDataManager


class BacDaddy:

    prices: pd.DataFrame = pd.DataFrame({"price": []})
    dataManager: LstmDataManager

    def __init__(self, dataSourcer: LstmDataManager):
        self.dataManager = dataSourcer
        print("Bac daddy loaded")

    def predict(self, latest_price):
        prices = self.dataManager.getData(tail=5000, subsampling=1)

        # Calculate MACD and signal lines
        bacd_params = (12, 26, 9)
        bacd_multiplier = 5  # 25 or 111
        exp1 = prices.ewm(span=bacd_params[0] * bacd_multiplier, adjust=False).mean()
        exp2 = prices.ewm(span=bacd_params[1] * bacd_multiplier, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=bacd_params[2] * bacd_multiplier, adjust=False).mean()

        # using the opposite of conventional logic...
        if (macd.iat[-1, 0] < signal.iat[-1, 0]) and (
            macd.iat[-2, 0] >= signal.iat[-2, 0]
        ):
            print(
                f"[{datetime.now().strftime('%H:%M:%S')}] Got buying signal at ${latest_price:.2f}"
            )
            return "buy"
        elif (macd.iat[-1, 0] > signal.iat[-1, 0]) and (
            macd.iat[-2, 0] <= signal.iat[-2, 0]
        ):
            print(
                f"[{datetime.now().strftime('%H:%M:%S')}] Got Selling signal at ${latest_price:.2f}"
            )
            return "sell"
        else:
            return None
