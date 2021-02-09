from strategy import Strategy
import qtpylib_indicators as qtpylib

import ta
import numpy as np

# Profit per 15sec: 0.003218595109045257


class Strategy001(Strategy):
    def __init__(self):
        Strategy.__init__(
            self,
            use_stop_loss=False,
            use_trailing_stop=True,
            trailing_stop_percent=-2,
            stoploss_percent_value=-5,
            use_roi=False,
        )

    def generateIndicators(self, dataframe):
        print("generating indicators")

        period_multiplier = 1

        dataframe["ema20"] = ta.trend.ema_indicator(dataframe["close"], window=round(20*period_multiplier))
        dataframe["ema50"] = ta.trend.ema_indicator(dataframe["close"], window=round(50*period_multiplier))
        dataframe["ema100"] = ta.trend.ema_indicator(dataframe["close"], window=round(100*period_multiplier))

        heikinashi = qtpylib.heikinashi(dataframe)
        dataframe["ha_open"] = heikinashi["open"]
        dataframe["ha_close"] = heikinashi["close"]

        return dataframe

    def adviseSell(self, dataframe, i, bought_at_index):
        if i == 0:
            return False

        prev_row = dataframe.iloc[i - 1]
        row = dataframe.iloc[i]
        return (
            (
                (row["ema50"] > row["ema100"])
                and (prev_row["ema50"] < prev_row["ema100"])
            )
            and (row["ha_close"] < row["ema20"])
            # and (row["ha_open"] > row["ha_close"])
        )  # red bar

    def adviseBuy(self, dataframe, i):
        if i == 0:
            return False

        prev_row = dataframe.iloc[i - 1]
        row = dataframe.iloc[i]
        return (
            ((row["ema20"] > row["ema50"]) and (prev_row["ema20"] < prev_row["ema50"]))
            # and (row["ha_close"] > row["ema20"])
            # and (row["ha_open"] < row["ha_close"])
        )
