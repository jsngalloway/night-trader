from abc import ABC, abstractmethod


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
            # cycles (15sec) : percent return
            "240": 0.01,
            "120": 0.1,
            "60": 0.2,
            "0": 0.25,
        }

    def getRoiPeriod(self, i: int):
        for timestep_limit, roi in self.minimal_roi.items():
            if i > int(timestep_limit):
                return float(roi)

    def shouldSell(self, dataframe, i, bought_at_index):
        current_price = dataframe["average"][i]
        bought_price = dataframe["average"][bought_at_index]
        timesteps = i - bought_at_index

        if (not self.trailing_stop_value) or current_price > self.trailing_stop_value:
            self.trailing_stop_value = current_price

        if self.use_stop_loss and (
            current_price < ((100 + self.stoploss_percent_value) / 100) * bought_price
        ):
            print("Hit hard stoploss")
            return True

        if self.use_trailing_stop and (
            current_price
            < ((100 + self.trailing_stop_percent) / 100) * self.trailing_stop_value
        ):
            print("Hit trailing stoploss")
            return True

        # dataframe = self.generateIndicators(dataframe)
        if self.adviseSell(dataframe, i, bought_at_index):
            print("strategy advised sell point")
            return True

        if self.use_roi:
            min_roi_percent = self.getRoiPeriod(i)
            current_roi_percent = (current_price - bought_price) / bought_price
            if current_roi_percent > min_roi_percent:
                print("hit return on investment")
                return True

        return False

    def shouldBuy(self, dataframe, i):
        self.trailing_stop_value = None
        # dataframe = self.generateIndicators(dataframe)
        return self.adviseBuy(dataframe, i)

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
