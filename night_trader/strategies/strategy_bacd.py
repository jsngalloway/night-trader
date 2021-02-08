from strategy import Strategy

import numpy as np


# Profit per 15sec: 0.004029776597783674
class StrategyBacd(Strategy):
  def __init__(self):
    Strategy.__init__(self, use_stop_loss=False, use_trailing_stop=False, trailing_stop_percent=-0.5, stoploss_percent_value=-5, use_roi=False)

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

    dataframe['macd'] = macd
    dataframe['signal'] = signal

    return dataframe

  def adviseSell(self, dataframe, i, bought_at_index):
    return (dataframe['macd'].iat[i] > dataframe['signal'].iat[i]) and (dataframe['macd'].iat[i-1] < dataframe['signal'].iat[i-1])

  def adviseBuy(self, dataframe, i):
    return (dataframe['macd'].iat[i] < dataframe['signal'].iat[i]) and (dataframe['macd'].iat[i-1] > dataframe['signal'].iat[i-1])