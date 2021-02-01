from typing import List, Tuple
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras import layers, optimizers
from sklearn.preprocessing import MinMaxScaler


def scaleData(
    paths_to_datasets: List[str], sub_sampling
) -> Tuple[List[pd.DataFrame], MinMaxScaler]:
    scaler = MinMaxScaler()
    datasets = []
    for path in paths_to_datasets:
        # perform partial fits on all datasets
        from_csv = pd.read_csv(path)
        new_df = pd.DataFrame()
        new_df["price"] = from_csv[["high_price","low_price"]].mean(axis=1)
        datasets.append(new_df[::sub_sampling])
        scaler = scaler.partial_fit(datasets[-1])
    for i in range(len(datasets)):
        # once all partial fits have been performed, transform every file
        datasets[i] = scaler.transform(datasets[i])
    return (datasets, scaler)


def createNewModel(lookback_length) -> tf.keras.Model:
    model = tf.keras.Sequential()
    model.add(
        layers.LSTM(
            units=32,
            return_sequences=True,
            input_shape=(lookback_length, 1),
            dropout=0.2,
        )
    )
    model.add(layers.LSTM(units=32, return_sequences=True, dropout=0.2))
    model.add(layers.LSTM(units=32, dropout=0.2))
    model.add(layers.Dense(units=1))
    model.compile(optimizer="adam", loss="mean_squared_error")
    return model


def preprocessData(data: pd.DataFrame, length) -> Tuple[np.ndarray, np.ndarray]:
    hist = []
    target = []

    for i in range(len(data) - length):
        x = data[i : i + length]
        y = data[i + length]
        hist.append(x)
        target.append(y)

    # Convert into numpy arrays and shape correctly (len(dataset), length) and (len(dataset), 1) respectively
    hist = np.array(hist)
    target = np.array(target)
    target = target.reshape(-1, 1)

    # Reshape the input into (len(dataset), length, 1)
    hist = hist.reshape((len(hist), length, 1))

    return (hist, target)


def trainModel(
    datasets, length, model: tf.keras.Model, epochs, batch_size
) -> tf.keras.Model:
    for dataset in datasets:
        X_train, y_train = preprocessData(dataset, length)

        # Perform training
        model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size)

    return model


def createLstmModelFromDatasets(
    paths_to_datasets, lookback_length=90, sub_sampling=1, epochs=6, batch_size=32
) -> tf.keras.Model:

    datasets, scaler = scaleData(paths_to_datasets, sub_sampling)

    model = createNewModel(lookback_length)
    model = trainModel(datasets, lookback_length, model, epochs, batch_size)
    return model
