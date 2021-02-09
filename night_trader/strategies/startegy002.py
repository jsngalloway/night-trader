from strategy import Strategy

import ta
import numpy as np

# Profit per 15sec: -0.00043279124581832465


class Strategy002(Strategy):
    def __init__(self):
        Strategy.__init__(
            self,
            use_stop_loss=False,
            use_trailing_stop=False,
            trailing_stop_percent=-0.5,
            stoploss_percent_value=-5,
            use_roi=False,
        )

    def generateIndicators(self, dataframe):
        print("generating indicators")
        # Stoch
        stoch = ta.momentum.StochasticOscillator(
            dataframe.high, dataframe.low, dataframe.close
        ).stoch()
        dataframe["slowk"] = stoch

        # RSI
        dataframe["rsi"] = ta.momentum.rsi(dataframe.close)

        # Inverse Fisher transform on RSI, values [-1.0, 1.0] (https://goo.gl/2JGGoy)
        rsi = 0.1 * (dataframe["rsi"] - 50)
        dataframe["fisher_rsi"] = (np.exp(2 * rsi) - 1) / (np.exp(2 * rsi) + 1)

        # Bollinger bands
        bollinger = ta.volatility.BollingerBands(dataframe.close)
        dataframe["bb_lowerband"] = bollinger.bollinger_lband()

        # SAR Parabol
        dataframe["sar"] = ta.trend.PSARIndicator(
            dataframe.high, dataframe.low, dataframe.close
        ).psar()

        return dataframe

    def adviseSell(self, dataframe, i, bought_at_index):
        row = dataframe.iloc[i]
        if (row["sar"] > row["close"]) and (row["fisher_rsi"] > 0.3):
            return True
        else:
            return False

    def adviseBuy(self, dataframe, i):
        row = dataframe.iloc[i]
        if (
            (row["rsi"] < 30)
            and (row["slowk"] < 20)
            and (row["bb_lowerband"] > row["close"])
        ):
            return True
        else:
            return False
