import pandas as pd
from predictors.lstm.lstm_data_manager import LstmDataManager
import logging
from strategies.strategy import Strategy

log = logging.getLogger(__name__)

class StrategyWrapper:

    dataManager: LstmDataManager
    strategy: Strategy

    def __init__(self, dataSourcer: LstmDataManager, strategy: Strategy):
        self.dataManager = dataSourcer
        self.strategy = strategy
        log.info("Strategy wrapper predictor initialized")

    def buy(self):
      data = self.dataManager.getData(tail=5000, subsampling=1)
      last_index = data.index[-1]
      return self.strategy.shouldBuy(data, last_index)

    def sell(self, current_price, bought_at_price, current_time, bought_at_time):
      data = self.dataManager.getData(tail=5000, subsampling=1)
      return self.strategy.shouldSell(data, current_price, bought_at_price, current_time, bought_at_time)