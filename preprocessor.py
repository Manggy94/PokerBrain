from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OrdinalEncoder, StandardScaler
from sklearn.compose import make_column_selector, make_column_transformer
from converter import *


class Preprocessor:

    def __init__(self):
        self.conv = HandConverter()
        self.streets = ["pf", "flop", "turn", "river"]
        self.labels = ["seat", "move", "value"]
        self.useless_columns = ["hand", "hand_id", "tour_id", "table_id"]
        self.combo_cols = [f"P{i}_combo" for i in range(9)]
        self.stack_cols = [f"P{i}_stack" for i in range(9)]
        self.street_val_cols = [f"{s}_action_{k}_value" for s in self.streets for k in range(24)]
        self.num_features = make_column_selector(dtype_include=np.number)
        self.num_pipeline = make_pipeline(StandardScaler())
        self.cat_features = make_column_selector(dtype_exclude=np.number)
        self.cat_pipeline = make_pipeline(
            OrdinalEncoder(),
            StandardScaler()
        )
        self.X_transformer = make_column_transformer(
            (self.num_pipeline, self.num_features),
            (self.cat_pipeline, self.cat_features)
        )

    def drop_useless(self, df: pd.DataFrame):
        df = df.drop(self.useless_columns, axis=1)
        df = df.drop(self.combo_cols, axis=1)
        return df

    def get_combos(self, df: pd.DataFrame):
        return df[self.combo_cols]

    def create_vector(self, df: pd.DataFrame, index: int):
        features = df.drop(self.useless_columns, axis=1)
        features = features.drop(self.combo_cols, axis=1)
        seat = self.conv.get_player_seat(df["hand"], index)
        features["target"] = seat
        y = df[f"P{index}_combo"]
        return features, y
