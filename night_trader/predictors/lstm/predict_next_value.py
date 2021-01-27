from typing import List, Tuple
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras import layers, optimizers
from sklearn.preprocessing import MinMaxScaler

def predict_next(model: tf.keras.Model, recent_data: pd.DataFrame):
  # For example, if we just want to predict the next timestep in the dataset we can prepare it as such:

  # 2. convert to numpy array 
  most_recent_period = np.array(recent_data)

  # 3. normalize data
  scaler = MinMaxScaler()
  most_recent_period_scaled = scaler.fit_transform(most_recent_period)

  # 4. reshape to the 3D tensor we expected (1, length, 1)
  most_recent_period_scaled_shaped = most_recent_period_scaled.reshape((1, len(recent_data), 1))

  # 5. Predict
  prediction = model.predict(most_recent_period_scaled_shaped)

  # 6. Un-normalize the data
  result = scaler.inverse_transform(prediction)

  # print(f"${result[0][0]}")

  return result[0][0]

def load_x_from_file(path: str, x: int):
  df = pd.read_csv(path)[['price']]
  return df.tail(x)


