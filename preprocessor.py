from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OrdinalEncoder, LabelBinarizer, StandardScaler
from sklearn.compose import make_column_selector, make_column_transformer
from converter import *


class Preprocessor:

    def __init__(self):
        self.conv = HandConverter()
        self.streets = ["pf", "flop", "turn", "river"]
        self.labels = ["seat", "move", "value"]
        self.useless_columns = ["hand", "hand_id", "tour_id", "table_id"]
        self.combo_cols = [f"P{i}_combo" for i in range(9)]
        self.hand_cols = [f"P{i}_hand" for i in range(9)]
        self.stack_cols = [f"P{i}_stack" for i in range(9)]
        self.street_val_cols = [f"{s}_action_{k}_value" for s in self.streets for k in range(24)]
        self.num_features = make_column_selector(dtype_include=np.number)
        self.num_pipeline = make_pipeline(StandardScaler())
        self.cat_features = make_column_selector(dtype_exclude=np.number)
        self.cat_pipeline = make_pipeline(OrdinalEncoder(), StandardScaler())
        self.X_transformer = make_column_transformer(
            (self.num_pipeline, self.num_features),
            (self.cat_pipeline, self.cat_features)
        )
        self.y_transformer = LabelBinarizer()

    def drop_useless(self, df: pd.DataFrame):
        df = df.drop(self.useless_columns, axis=1)
        df = df.drop(self.combo_cols, axis=1)
        df = df.drop(self.hand_cols, axis=1)
        return df

    def get_combos(self, df: pd.DataFrame):
        return df[self.combo_cols]

    def create_vector(self, df: pd.DataFrame, index: int, training: bool = True, labels: str = "hand"):
        if training:
            df = df.where(df[f"P{index}_combo"] != "None").dropna()
        y = df[f"P{index}_{labels}"]
        vfunc = np.vectorize(self.conv.get_player_seat)
        df["target"] = vfunc(df["hand"], index)
        features = self.drop_useless(df)
        return features, y

    def create_feature_tab(self, df: pd.DataFrame, index: int, training: bool = True, labels: str = "hand"):
        return self.create_vector(df=df, index=index, training=training, labels=labels)[0]

    def create_label_tab(self, df: pd.DataFrame, index: int, training: bool = True, labels: str = "hand"):
        return self.create_vector(df=df, index=index, training=training, labels=labels)[1]

    def create_features(self, df: pd.DataFrame, training: bool = True, labels: str = "hand"):
        return pd.concat([self.create_feature_tab(df, i, training, labels) for i in range(9)]).reset_index(drop=True)

    def create_labels(self, df: pd.DataFrame, training: bool = True, labels: str = "hand"):
        return pd.concat([self.create_label_tab(df, i, training, labels) for i in range(9)]).reset_index(drop=True)

    def create_vectors(self, df: pd.DataFrame, training: bool = True, labels: str = "hand"):
        return self.create_features(df, training, labels), self.create_labels(df, training, labels)
