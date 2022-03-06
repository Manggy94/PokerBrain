import os
import pandas as pd
import numpy as np
from API.listings import str_combos, str_hands, str_positions
from converter import HandConverter
from sklearn.compose import make_column_selector, make_column_transformer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OrdinalEncoder, LabelBinarizer, LabelEncoder, StandardScaler
from tracker import PlayerHistory


class Preprocessor:

    def __init__(self):
        self.conv = HandConverter()
        self.streets = ["pf", "flop", "turn", "river"]
        self.labels = ["seat", "move", "value"]
        self.useless_columns = ["hand", "hand_id", "tour_id", "table_id"]
        self.num_features = make_column_selector(dtype_include=np.number)
        self.num_pipeline = make_pipeline(StandardScaler())
        self.cat_features = make_column_selector(dtype_exclude=np.number)
        self.cat_pipeline = make_pipeline(
            OrdinalEncoder(handle_unknown="use_encoded_value",
                           unknown_value=int(1e5)), StandardScaler()
        )
        self.X_transformer = make_column_transformer(
            (self.num_pipeline, self.num_features),
            (self.cat_pipeline, self.cat_features)
        )
        self.Y_transformer = LabelEncoder()
        self.Z_transformer = LabelEncoder()
        self.y_transformer = LabelBinarizer()
        self.z_transformer = LabelBinarizer()
        features = pd.read_csv(f"{os.getcwd()}/Data/features_tab.csv", index_col=0)
        self.X_transformer.fit(features)
        self.Y_transformer.fit(str_combos)
        self.Z_transformer.fit(str_hands)
        self.y_transformer.fit(str_combos)
        self.z_transformer.fit(str_hands)

    def drop_useless(self, df: pd.DataFrame):
        df = df.drop(self.useless_columns, axis=1)
        return df

