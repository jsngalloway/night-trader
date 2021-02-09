from abc import ABC, abstractmethod
import pandas as pd
import logging

log = logging.getLogger(__name__)

class Strategy(ABC):
    use_stop_loss: bool
    use_trailing_stop: bool

    trailing_stop_percent: float
    trailing_stop_value: float

    stoploss_percent_value: float

    minimal_roi: dict
    use_roi: bool

    def __init__(
        self,
        use_stop_loss=False,
        use_trailing_stop=False,
        trailing_stop_percent=-0.5,
        stoploss_percent_value=-1.2,
        use_roi=False,
    ):
        self.use_stop_loss = use_stop_loss
        self.use_trailing_stop = use_trailing_stop
        self.trailing_stop_percent = trailing_stop_percent
        self.stoploss_percent_value = stoploss_percent_value
        self.trailing_stop_value = None

        self.use_roi = use_roi
        self.minimal_roi = {
            # cycles minutes : percent return
            "60": 0.01,
            "30": 0.1,
            "15": 0.2,
            "0": 0.25,
        }

        log.info("Initialized Abstract Strategy class")

    def getRoiPeriod(self, delta_time):
        time_in_mins = delta_time.total_seconds()/60
        for timestep_limit, roi in self.minimal_roi.items():
            if time_in_mins > int(timestep_limit):
                return float(roi)

    def shouldSell(self, dataframe, current_price, bought_at_price, current_time, bought_at_time):
        # delta_time = pd.to_datetime(current_time) - pd.to_datetime(bought_at_time)

        # print(current_price, self.trailing_stop_value)
        if (self.trailing_stop_value == None) or current_price > self.trailing_stop_value:
            self.trailing_stop_value = current_price

        if self.use_stop_loss and (
            current_price < ((100 + self.stoploss_percent_value) / 100) * bought_at_price
        ):
            log.info(f"Sell signal: Hit hard stoploss of {self.stoploss_percent_value:.2f}% price at ${current_price}")
            return True

        if self.use_trailing_stop and (
            current_price
            < ((100 + self.trailing_stop_percent) / 100) * self.trailing_stop_value
        ):
            log.info(f"Sell signal: Hit trailing stoploss which was at ${self.trailing_stop_value:.2f} (current price at ${current_price})")
            return True

        dataframe = self.generateIndicators(dataframe)
        if self.adviseSell(dataframe, current_time, bought_at_time):
            log.info("Sell signal: Strategy has advised selling")
            return True

        if self.use_roi:
            min_roi_percent = self.getRoiPeriod(pd.to_datetime(current_time) - pd.to_datetime(bought_at_time))
            current_roi_percent = (current_price - bought_at_price) / bought_at_price
            if current_roi_percent > (min_roi_percent/100):
                log.info(f"Sell signal: Reached return on investment {current_roi_percent*100:.2f}% needed from {min_roi_percent} after {pd.to_datetime(current_time) - pd.to_datetime(bought_at_time)}")
                return True

        return False

    def shouldBuy(self, dataframe, i):
        self.trailing_stop_value = None
        dataframe = self.generateIndicators(dataframe)
        return_value = self.adviseBuy(dataframe, i)
        if return_value:
          log.info("Buy signal: Strategy has advised buying")
        return return_value

    # ABSTRACT METHODS:

    @abstractmethod
    def adviseBuy(self, dataframe, i):
        pass

    @abstractmethod
    def adviseSell(self, dataframe, i, bought_at_index):
        pass

    @abstractmethod
    def generateIndicators(self, dataframe):
        pass

# https://github.com/Haehnchen/crypto-trading-bot