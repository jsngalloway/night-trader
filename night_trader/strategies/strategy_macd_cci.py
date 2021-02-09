from strategy import Strategy

import numpy as np
import ta


# Profit per 15sec: 0.002728082958054552
class StrategyMacdCci(Strategy):
    def __init__(self):
        Strategy.__init__(
            self,
            use_stop_loss=False,
            use_trailing_stop=True,
            trailing_stop_percent=-3,
            stoploss_percent_value=-4,
            use_roi=True,
        )

        self.minimal_roi = {
            # cycles (15sec) : percent return
            "240": 0.02,
            "120": 0.1,
            "60": 0.15,
            "0": 0.2,
        }

    def generateIndicators(self, dataframe):
        print("generating indicators")

        # Calculate MACD and signal lines
        bacd_params = (12, 26, 9)
        period_multiplier = 49  # 175  # 25 or 111

        exp1 = (
            dataframe[["average"]]
            .ewm(span=bacd_params[0] * period_multiplier, adjust=False)
            .mean()
        )
        exp2 = (
            dataframe[["average"]]
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

        dataframe["cci"] = ta.trend.cci(dataframe.high, dataframe.low, dataframe.close)
        return dataframe

    def adviseSell(self, dataframe, i, bought_at_index):
        return (dataframe["macd"].iat[i] < dataframe["signal"].iat[i]) and (dataframe["cci"].iat[i] >= 100.0*3)

    def adviseBuy(self, dataframe, i):
        return (dataframe["macd"].iat[i] > dataframe["signal"].iat[i]) and (dataframe["cci"].iat[i] <= -50.0*3)
