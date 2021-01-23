import numpy as np
from data_sourcer import DataSourcer
from data_manager import DataManager
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
import time

class LSTM():
    
    prices: pd.DataFrame = pd.DataFrame({'price' : []})
    dataManager: DataManager

    def __init__(self, dataSourcer):
        self.dataManager = DataManager(dataSourcer, 1000)
        while (len(self.dataManager.get()[1]) < 100):
            time.sleep(1)
            print('LSTM Loading: gathered ' + str(len(self.dataManager.get()[1])) + '/100 prices')


    def predict(self):
        
        is_new, price_list = self.dataManager.get()
        if not is_new:
            return None
        df = pd.DataFrame(price_list)

        print(len(df))
        data = df.iloc[:, 0]

        hist = []
        target = []
        length = 90


        for i in range(len(data)-length):
            x = data[i:i+length]
            y = data[i+length]
            hist.append(x)
            target.append(y)

        #convert list to array
        hist = np.array(hist)
        target = np.array(target)
        target = target.reshape(-1,1)

        sc = MinMaxScaler()
        hist_scaled = sc.fit_transform(hist)
        target_scaled = sc.fit_transform(target)

        #Reshape the input
        hist_scaled = hist_scaled.reshape((len(hist_scaled), length, 1))
        print(hist_scaled.shape)

        pred = model.predict(hist_scaled)

        pred_transformed = sc.inverse_transform(pred)
        y_test_transformed = sc.inverse_transform(target_scaled)

        #plt.figure(figsize=(24,8))
        #plt.plot(y_test_transformed, color='blue', label='Real')
        #plt.plot(pred_transformed, color='red', label='Prediction')
        #plt.title('ETH Price Prediction')
        #plt.legend()
        #plt.show()
        if

        if ((macd.iat[-1, 0] > signal.iat[-1, 0]) and (macd.iat[-2, 0] <= signal.iat[-2, 0])):
            return "buy"
        elif ((macd.iat[-1, 0] < signal.iat[-1, 0]) and (macd.iat[-2, 0] >= signal.iat[-2, 0])):
            return "sell"
        else:
            return None
