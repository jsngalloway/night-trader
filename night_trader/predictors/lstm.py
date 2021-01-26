import numpy as np
from data_sourcer import DataSourcer
from data_manager import DataManager
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import time
from tqdm import tqdm

class LSTM():
    
    prices: pd.DataFrame = pd.DataFrame({'price' : []})
    dataManager: DataManager

    def __init__(self, dataSourcer):
        self.dataManager = DataManager(dataSourcer, 100)
        for i in tqdm(range(0, 260)):
            i = len(self.dataManager.get()[1])
            time.sleep(1)
            # print('MAC Daddie Loading: gathered ' + str(len(self.dataManager.get()[1])) + '/260 prices')


    def predict(self):
        