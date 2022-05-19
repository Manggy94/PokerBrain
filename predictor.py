import pandas as pd
import numpy as np
import sklearn.preprocessing

from preprocessor import Preprocessor
from API.Table import CombosRange
from API.hand import Combo
import datetime
import tensorflow as tf
import os


class Predictor:

    def __init__(self):
        self.model_path = f"{os.getcwd()}/Models"
        self.prep = Preprocessor()
        self.indexes = self.prep.y_transformer.inverse_transform(np.eye(1326))
        if "test" in self.model_path:
            self.model_path = f"{os.path.abspath(os.path.join(os.getcwd(), os.pardir))}/Models"
        self.date = f"{datetime.date.today()}"
        try:
            self.model = tf.keras.models.load_model(f"{self.model_path}/{self.date}")
        except OSError:
            models_list = os.listdir(self.model_path)
            self.model = tf.keras.models.load_model(f"{self.model_path}/{models_list.pop()}")
        self.model.summary()

    @staticmethod
    def reshape(label):
        lbl = np.array(label)
        lbl = lbl.reshape(1, label.shape[0])
        return lbl

    def predict_combos(self, X: pd.DataFrame):
        feature = self.reshape(X)
        predictions = self.model.predict(feature).astype("float16").T
        cr = pd.DataFrame(index=self.indexes, data=predictions, columns=["p"])
        combos_range = CombosRange()
        combos_range["p"] = cr["p"]
        return combos_range

    @staticmethod
    def dead_cards(x):
        combo = Combo(x["hero_combo"])
        hero = [f"{combo.first}", f"{combo.second}"]
        cards = [x[f"Card_{i}"] for i in range(5)]
        dead = cards + hero
        return np.array(dead)
