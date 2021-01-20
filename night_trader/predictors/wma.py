import numpy as np
from data_sourcer import DataSourcer
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
import time

class Wma():
    weights = np.arange(1,11)
    
    prices: pd.DataFrame = pd.DataFrame({'price' : []})
    dataSourcer: DataSourcer

    def __init__(self, dataSourcer):
        self.dataSourcer = dataSourcer
        while (len(self.prices) < 25):
            self.getNewPrice()
            time.sleep(1)
            print('Sleeping, gathered ' + str(len(self.prices)) + '/25 prices')
        pass
    
    def getNewPrice(self):
        if self.dataSourcer.isNewQuotes():
            new_data = self.dataSourcer.getNewQuotes()
            new_data = new_data.drop(['time'], axis=1)
            # self.prices = pd.concat([new_data, self.prices], ignore_index=True)
            self.prices = self.prices.append(new_data)


    def predict(self):
        self.getNewPrice()

        ewa = self.prices.ewm(span=20, adjust=True).mean()
        slope = ewa.diff()
        slope_array = np.array(slope)
        # sns.set(style="darkgrid", font_scale=1.5)
        # plt.figure(figsize=(12,8))
        # plt.plot(data, color='blue', label='open')
        # plt.plot(ewa, color='red', label='ewa')
        # plt.plot(slope, color='green', label='slope')
        # plt.legend()
        # plt.show()

        return slope_array[-1]
        # bought = False
        # sumwin = 0
        # for i, pt in enumerate(npslope[20:]):
        #     if pt > 0.005 and not bought:
        #         bought = price_list[20 + i]
        #         print("bought", i, pt)
        #     if pt < -0.001 and bought:
        #         print("Selling",i, pt)
        #         sumwin = sumwin + price_list[20 + i] - bought
        #         print(price_list[20 + i] - bought)
        #         bought = False
        # print("Total winning", sumwin)

        # wma10 = recent_data['price'].rolling(10).apply(lambda prices: np.dot(prices, self.weights)/self.weights.sum(), raw=True)

        # print(wma10.head(20))