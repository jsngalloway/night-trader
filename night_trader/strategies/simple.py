from strategy import Strategy

import ta
import numpy as np

# Profit per 15sec: 0.0015354321924858506


class SimpleStrategy(Strategy):
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

        # MACD
        macd = ta.trend.MACD(dataframe.close)
        dataframe['macd'] = macd.macd()
        dataframe['macdsignal'] = macd.macd_signal()
        dataframe['macdhist'] = macd.macd_diff()

        # RSI
        dataframe['rsi'] = ta.momentum.rsi(dataframe.close, window=7*2)

        # required for graphing
        bollinger = ta.volatility.BollingerBands(dataframe.close)
        dataframe['bb_lowerband'] = bollinger.bollinger_lband()
        dataframe['bb_upperband'] = bollinger.bollinger_hband()
        dataframe['bb_middleband'] = bollinger.bollinger_mavg()

        return dataframe

    def adviseSell(self, dataframe, i, bought_at_index):
        return dataframe.iloc[i]['rsi'] > 80

    def adviseBuy(self, dataframe, i):
        row = dataframe.iloc[i]

        return ((row['macd'] > 0)  # over 0
            & (row['macd'] > row['macdsignal'])  # over signal
            & (row['bb_upperband'] > dataframe.iloc[i+1]['bb_upperband'])  # pointed up
            & (row['rsi'] > 70))  # optional filter, need to investigate
