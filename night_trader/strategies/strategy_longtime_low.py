from strategies.strategy import Strategy
import pandas as pd
import logging
import math

# Profit per 15sec: 0.

log = logging.getLogger(__name__)

class StrategyLongtimeLow(Strategy):
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
            # minutes : percent return
            "1200": 3,
            "600": 5,
            "300": 7,
            "150": 10,
            "0": 15,
        }

        log.info("Strategy Longtime Low Initialized")
        log.info("---------------------")
        log.info("Idea: buy at a daily(ish) low and wait for (diminishing) return on investment")
        log.info(f"Use Hard stoploss: {self.use_stop_loss}")
        log.info(f"Hard stoploss percent: {self.stoploss_percent_value}%")
        log.info(f"Use Trailing stoploss: {self.use_trailing_stop}")
        log.info(f"Trailing stoploss percent: {self.stoploss_percent_value}%")
        log.info(f"Use minimal ROI: {self.use_roi}")
        for k, v in self.minimal_roi.items():
          log.info(f"   After {k} min settle for {v}%")
        log.info("---------------------")
    

    def generateIndicators(self, dataframe) -> pd.DataFrame:
        log.debug("Generating indicators")

        # bacd_params = (12, 26, 9)
        # period_multiplier = 30  # 175  # 25 or 111
        # augmented_df = dataframe

        # exp1 = (
        #     dataframe[["price"]]
        #     .ewm(span=bacd_params[0] * period_multiplier, adjust=False)
        #     .mean()
        # )
        # exp2 = (
        #     dataframe[["price"]]
        #     .ewm(span=bacd_params[1] * period_multiplier, adjust=False)
        #     .mean()
        # )
        # macd = exp1 - exp2
        # signal = macd.ewm(
        #     span=bacd_params[2] * round(1 + period_multiplier * 0.25),
        #     adjust=False,
        # ).mean()

        # I'm pretty sure this is a safe operation, pandas just doesn't like it
        # pd.set_option('mode.chained_assignment', None)
        # augmented_df["macd"] = macd
        # augmented_df["signal"] = signal
        # pd.set_option('mode.chained_assignment', 'raise')

        return dataframe

    def adviseSell(self, dataframe: pd.DataFrame, i, bought_at_index) -> bool:
      # In this strategy we rely solely on the ROI
      return False

    def adviseBuy(self, dataframe: pd.DataFrame, current_timestamp: pd.Timestamp) -> bool:
        current_price = dataframe.at[current_timestamp, "price"]
        
        low = dataframe[:current_timestamp]["price"].tail(5000).min()
        buy = math.isclose(current_price, low, rel_tol=1e-09, abs_tol=0.0)
        if buy:
            print("Reccomending buy at ", current_timestamp, current_price, low)
        return buy
