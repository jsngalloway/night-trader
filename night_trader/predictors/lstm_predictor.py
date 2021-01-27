import pandas as pd
import tensorflow as tf
from datetime import datetime

from tensorflow.python.platform.tf_logging import flush

from predictors.lstm.lstm_creator import createLstmModelFromDatasets
from predictors.lstm.predict_next_value import predict_next, load_x_from_file
from predictors.lstm.lstm_data_manager import LstmDataManager


class Lstm:

    prices: pd.DataFrame = pd.DataFrame({"price": []})
    dataManager: LstmDataManager
    model: tf.keras.Model
    points_needed: int
    last_predicted_value: int

    # Lookback length: determined on creation of model: how many previous points we'll reference for each prediction
    model_lookback_length = 90

    # Model Subsampling: data is recorded every 15 seconds, what interval of those should be samples (e.g. 4 = one point per minute)
    model_subsampling = 4

    def __init__(self, dataManager):
        self.dataManager = dataManager

        path_to_model = "models/dump_model_1"
        print("Loading model from file...", end="")
        self.model = tf.keras.models.load_model(path_to_model)
        print("done.", flush=True)

        # print("Creating model...")
        # paths = ["data/MorningTest.csv", "data/MorningTest5.csv", "data/MorningTest6.csv", "data/MorningTest10.csv"]
        # self.model = createLstmModelFromDatasets(paths, lookback_length=90, sub_sampling=60)
        # print("Model successfully created.")

        data = self.dataManager.getData(
            tail=self.model_lookback_length, subsampling=self.model_subsampling
        )
        self.last_predicted_value = predict_next(self.model, data)

    def predict(self, current_price):
        data = self.dataManager.getData(
            tail=self.model_lookback_length, subsampling=self.model_subsampling
        )
        next_value = predict_next(self.model, data)

        current_value = current_price

        current_projected_error = round(
            abs(current_value - self.last_predicted_value) / current_value * 100, 4
        )
        action = None

        if (next_value - self.last_predicted_value) > 1.0:
            action = "buy"

        print(
            f"[{datetime.now().strftime('%H:%M:%S')}] Current: ${current_value:.2f} Projected: ${self.last_predicted_value:.2f} (Error: {current_projected_error}%) Next: ${next_value:.2f} (${next_value-self.last_predicted_value:+.2f}) Action: {action}",
            flush=True,
        )
        self.last_predicted_value = next_value
        return action
