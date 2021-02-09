from strategies.strategy import Strategy

import ta
import numpy as np

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
    

    def generateIndicators(self, dataframe):
        # print("generating indicators")
        bacd_params = (12, 26, 9)
        period_multiplier = 30  # 175  # 25 or 111

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

        dataframe["macd"] = macd
        dataframe["signal"] = signal
        return dataframe

    def adviseSell(self, dataframe, i, bought_at_index):
      return False

    def adviseBuy(self, dataframe, i):
      if i == None:
        i = len(dataframe) - 1
      return (dataframe["macd"].iat[i] < dataframe["signal"].iat[i])
