import pandas as pd
import tensorflow as tf
from datetime import datetime
import logging

from predictors.lstm.lstm_creator import createLstmModelFromDatasets
from predictors.lstm.predict_next_value import predict_next, load_x_from_file
from predictors.lstm.lstm_data_manager import LstmDataManager

log = logging.getLogger(__name__)


class Lstm:

    prices: pd.DataFrame = pd.DataFrame({"price": []})
    dataManager: LstmDataManager
    model: tf.keras.Model
    points_needed: int
    last_value: float = None
    last_predicted_value: float = None
    last_last_predicted_value: float = None

    # Lookback length: determined on creation of model: how many previous points we'll reference for each prediction
    model_lookback_length: int

    # Model Subsampling: data is recorded every 15 seconds, what interval of those should be samples (e.g. 4 = one point per minute)
    model_interval: int

    predict_call_count: int

    def __init__(self, dataManager, model_interval):
        self.model_interval = model_interval
        self.dataManager = dataManager

        path_to_model = "models/dump_model_2_ll20_xth3"
        log.info(f"Loading model from file: {path_to_model}")
        self.model = tf.keras.models.load_model(path_to_model)
        log.info("model loaded.")

        self.model_lookback_length = self.model.input_shape[1]

        self.predict_call_count = 0

        # print("Creating model...")
        # paths = ["data/MorningTest.csv", "data/MorningTest5.csv", "data/MorningTest6.csv", "data/MorningTest10.csv"]
        # self.model = createLstmModelFromDatasets(paths, lookback_length=90, sub_sampling=60)
        # print("Model successfully created.")

        # data = self.dataManager.getData(
        #     tail=self.model_lookback_length, subsampling=self.model_interval
        # )
        # self.last_predicted_value = predict_next(self.model, data)
        # self.last_last_predicted_value = self.last_predicted_value
        # self.last_value = None

    def predict(self, current_price):
        self.predict_call_count += 1
        if self.predict_call_count % self.model_interval != 0:
            # The model is only designed to predict every (model_interval) seconds * 15
            return

        data = self.dataManager.getData(
            tail=self.model_lookback_length, subsampling=self.model_interval
        )
        next_value = predict_next(self.model, data)

        current_value = current_price

        # The first time it's run we're not ready to make a prediction
        if not self.last_predicted_value:
            print("Preparing to predict")
            self.last_predicted_value = next_value
            self.last_last_predicted_value = next_value
            self.last_value = current_value
            return None

        current_projected_error = (
            abs(
                (current_value - self.last_value)
                - (self.last_predicted_value - self.last_last_predicted_value)
            )
            / abs(current_value - self.last_value)
            * 100
        )
        action = None

        if (next_value - self.last_predicted_value) > 1.0:
            log.info(
                f"Got buy signal, predicted change is ({next_value-self.last_predicted_value:+.2f})"
            )
            action = "buy"
        else:
            action = "sell"

        log.info(
            f"Real: [Last/Now: ${self.last_value:.2f}, ${current_value:.2f} ({current_value-self.last_value:+.2f})] Model: [Last/Now/Next: ${self.last_last_predicted_value:.2f}, ${self.last_predicted_value:.2f}, ${next_value:.2f} ({next_value-self.last_predicted_value:+.2f})] Error: {current_projected_error:4.0f}% Action: {action}"
        )
        self.last_value = current_value
        self.last_last_predicted_value = self.last_predicted_value
        self.last_predicted_value = next_value
        return action
