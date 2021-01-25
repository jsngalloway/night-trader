from typing import List, Tuple
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras import layers, optimizers
from sklearn.preprocessing import MinMaxScaler

def scaleData(paths_to_datasets: List[str]) -> Tuple[List[pd.DataFrame], MinMaxScaler]:
    scaler = MinMaxScaler()
    datasets = []
    for path in paths_to_datasets:
        # perform partial fits on all datasets
        datasets.append(pd.read_csv(path)[['price']])
        scaler = scaler.partial_fit(datasets[-1])
    for i in range(len(datasets)):
        # once all partial fits have been performed, transform every file
        datasets[i] = scaler.transform(datasets[i])
    return (datasets, scaler)

def createNewModel(lookback_length) -> tf.keras.Model:
  model = tf.keras.Sequential()
  model.add(layers.LSTM(units=32, return_sequences=True, input_shape=(lookback_length,1), dropout=0.2))
  model.add(layers.LSTM(units=32, return_sequences=True, dropout=0.2))
  model.add(layers.LSTM(units=32, dropout=0.2))
  model.add(layers.Dense(units=1))
  optimizer = optimizers.Adam()
  model.compile(optimizer=optimizer, loss='mean_squared_error')
  return model

def preprocessData(data: pd.DataFrame, length) -> Tuple[np.ndarray, np.ndarray]:
    hist = []
    target = []

    for i in range(len(data)-length):
        x = data[i:i+length]
        y = data[i+length]
        hist.append(x)
        target.append(y)
    
    # Convert into numpy arrays and shape correctly (len(dataset), length) and (len(dataset), 1) respectively
    hist = np.array(hist)
    target = np.array(target)
    target = target.reshape(-1,1)

    #Reshape the input into (len(dataset), length, 1)
    hist = hist.reshape((len(hist), length, 1))

    return(hist, target)

def trainModel(datasets, length, model) -> tf.keras.Model:
    for dataset in datasets:
        X_train, y_train = preprocessData(dataset, length)

        # Perform training
        model.fit(X_train, y_train, epochs=6, batch_size=32)

    return model

def createLstmModelFromDatasets(paths_to_datasets) -> tf.keras.Model:
  LENGTH = 90

  datasets, scaler = scaleData(paths_to_datasets)
  
  model = createNewModel(LENGTH)
  model = trainModel(datasets, LENGTH, model)
  return model