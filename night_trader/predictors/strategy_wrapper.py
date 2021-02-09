import pandas as pd
from datetime import datetime
from predictors.lstm.lstm_data_manager import LstmDataManager
import logging
from strategies.strategy import Strategy
# import matplotlib.pyplot as plt

log = logging.getLogger(__name__)


class StrategyWrapper:

    # TODO REMOVE
    # plt.style.use("seaborn-darkgrid")
    # plt.ioff()
    # fig = None
    # axs = None
    # ############################

    # prices: pd.DataFrame = pd.DataFrame({"price": []})
    dataManager: LstmDataManager
    strategy: Strategy

    def __init__(self, dataSourcer: LstmDataManager, strategy: Strategy):
        self.dataManager = dataSourcer
        self.strategy = strategy
        log.info("Strategy wrapper predictor initialized")

    def buy(self):
      data = self.dataManager.getData(tail=5000, subsampling=1)
      return self.strategy.shouldBuy(data, None)

    def sell(self, current_time, bought_at_time):
      data = self.dataManager.getData(tail=5000, subsampling=1)
      return self.strategy.shouldSell(data, current_time, bought_at_time)