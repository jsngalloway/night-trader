from night_trader.strategies.strategy import Strategy
import pandas as pd
import logging

# Profit per 15sec: 0.006893096632211284

log = logging.getLogger(__name__)

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
            # minutes : percent return
            "120": 1,
            "60": 2,
            "30": 5,
            "15": 8,
            "0": 10,
        }

        log.info("StrategyWaiter Initialized")
        log.info("---------------------")
        log.info("Idea: buy at a decent time (BACD) and wait for (diminishing) return on investment")
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

        # I'm pretty sure this is a safe operation, pandas just doesn't like it
        pd.set_option('mode.chained_assignment', None)
        augmented_df["macd"] = macd
        augmented_df["signal"] = signal
        pd.set_option('mode.chained_assignment', 'raise')

        return augmented_df

    def adviseSell(self, dataframe: pd.DataFrame, i, bought_at_index) -> bool:
      # In this strategy we rely solely on the ROI
      return False

    def adviseBuy(self, dataframe: pd.DataFrame, current_timestamp: pd.Timestamp) -> bool:
      return (dataframe.at[current_timestamp, "macd"] < dataframe.at[current_timestamp, "signal"])
