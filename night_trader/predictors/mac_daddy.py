import numpy as np
from data_sourcer import DataSourcer
from data_manager import DataManager
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
import time
from tqdm import tqdm

class MacDaddy():
    
    prices: pd.DataFrame = pd.DataFrame({'price' : []})
    dataManager: DataManager

    def __init__(self, dataSourcer):
        self.dataManager = DataManager(dataSourcer, 400)
        for i in tqdm(range(0, 260)):
        # while (len(self.dataManager.get()[1]) < 260):
            i = len(self.dataManager.get()[1])
            time.sleep(1)
            # print('MAC Daddie Loading: gathered ' + str(len(self.dataManager.get()[1])) + '/260 prices')


    def predict(self):
        
        is_new, price_list = self.dataManager.get()
        if not is_new:
            return None
        prices = pd.DataFrame(price_list)

        exp1 = prices.ewm(span=117, adjust=False).mean() #12
        exp2 = prices.ewm(span=254, adjust=False).mean() #26
        macd = exp1 - exp2
        signal = macd.ewm(span=88, adjust=False).mean() #9

        if (macd.iat[-1, 0] > signal.iat[-1, 0]):
            return "buy"
        elif (macd.iat[-1, 0] < signal.iat[-1, 0]):
            return "sell"
        else:
            return None
