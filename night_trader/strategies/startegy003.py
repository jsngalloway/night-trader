from strategy import Strategy
import qtpylib_indicators as qtpylib

import ta
import numpy as np

# Profit per 15sec:


class Strategy002(Strategy):
    def __init__(self):
        Strategy.__init__(
            self,
            use_stop_loss=False,
            use_trailing_stop=False,
            trailing_stop_percent=-0.25,
            stoploss_percent_value=-5,
            use_roi=False,
        )

    def generateIndicators(self, dataframe):
        print("generating indicators")

        return dataframe

    def adviseSell(self, dataframe, i, bought_at_index):
        pass

    def adviseBuy(self, dataframe, i):
        if (
            (dataframe["rsi"] < 28)
            and (dataframe["rsi"] > 0)
            and (dataframe["close"] < dataframe["sma"])
            and (dataframe["fisher_rsi"] < -0.94)
            and (
                (dataframe["ema50"] > dataframe["ema100"])
                or (qtpylib.crossed_above(dataframe["ema5"], dataframe["ema10"]))
            )
            and (dataframe["fastd"] > dataframe["fastk"])
            and (dataframe["fastd"] > 0)
        ):
            return True
        return False
