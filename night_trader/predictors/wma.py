import numpy as np
from data_sourcer import DataSourcer
from data_manager import DataManager
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
import time


class Wma:
    weights = np.arange(1, 11)

    prices: pd.DataFrame = pd.DataFrame({"price": []})
    dataManager: DataManager

    def __init__(self, dataSourcer):
        self.dataManager = DataManager(dataSourcer, 20)
        while len(self.dataManager.get()[1]) < 20:
            time.sleep(1)
            print(
                "WMA Loading: gathered "
                + str(len(self.dataManager.get()[1]))
                + "/20 prices"
            )

    def predict(self):
        is_new, price_list = self.dataManager.get()
        if not is_new:
            return None
        prices = pd.DataFrame(price_list)

        ewa = prices.ewm(span=20, adjust=True).mean()
        slope = ewa.diff()
        slope_array = np.array(slope)
        last_slope = slope_array[-1]

        if last_slope > 0.007:  # .005
            return "buy"
        elif last_slope < -0.0015:  # -.001
            return "sell"
        else:
            return None
