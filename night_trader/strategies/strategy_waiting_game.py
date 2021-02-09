from strategies.strategy import Strategy

import ta
import numpy as np
import pandas as pd
# Profit per 15sec: 0.006893096632211284


class StrategyWaiter(Strategy):
    def __init__(self):

        Strategy.__init__(
            self,
            use_stop_loss=False,
            use_trailing_stop=False,
            trailing_stop_percent=-2.5,
            stoploss_percent_value=-5,
            use_roi=True,
        )
        self.minimal_roi = {
            # cycles (15sec) : percent return
            "120": 1,
            "60": 2,
            "30": 5,
            "15": 8,
            "0": 10,
        }
    

    def generateIndicators(self, dataframe) -> pd.DataFrame:
        # print("generating indicators")
        bacd_params = (12, 26, 9)
        period_multiplier = 30  # 175  # 25 or 111
        augmented_df = dataframe

        exp1 = (
            dataframe[["price"]]
            .ewm(span=bacd_params[0] * period_multiplier, adjust=False)
            .mean()
        )
        exp2 = (
            dataframe[["price"]]
            .ewm(span=bacd_params[1] * period_multiplier, adjust=False)
            .mean()
        )
        macd = exp1 - exp2
        signal = macd.ewm(
            span=bacd_params[2] * round(1 + period_multiplier * 0.25),
            adjust=False,
        ).mean()

        augmented_df["macd"] = macd
        augmented_df["signal"] = signal
        return augmented_df

    def adviseSell(self, dataframe: pd.DataFrame, i, bought_at_index) -> bool:
      # In this strategy we rely solely on the ROI
      return False

    def adviseBuy(self, dataframe: pd.DataFrame, current_timestamp: pd.Timestamp) -> bool:
      row = dataframe.loc[current_timestamp]

      return (row["macd"] < row["signal"])
