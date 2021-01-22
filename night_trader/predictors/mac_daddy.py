import numpy as np
from data_sourcer import DataSourcer
from data_manager import DataManager
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
import time

class MacDaddy():
    
    prices: pd.DataFrame = pd.DataFrame({'price' : []})
    dataManager: DataManager

    def __init__(self, dataSourcer):
        self.dataManager = DataManager(dataSourcer, 200)
        while (len(self.dataManager.get()) < 30):
            time.sleep(1)
            print('MAC Daddie Loading: gathered ' + str(len(self.dataManager.get())) + '/30 prices')


    def predict(self):
        
        prices = pd.DataFrame(self.dataManager.get())
        exp1 = prices.ewm(span=12, adjust=False).mean()
        exp2 = prices.ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()

        if ((macd.iat[-1, 0] > signal.iat[-1, 0]) and (macd.iat[-2, 0] <= signal.iat[-2, 0])):
            return "buy"
        elif ((macd.iat[-1, 0] < signal.iat[-1, 0]) and (macd.iat[-2, 0] >= signal.iat[-2, 0])):
            return "sell"
        else:
            return None
