import pandas as pd
from xgboost import DMatrix
import xgboost as xgb


class PredictWrapper(object):

    def __init__(self, model):
        self.model = model

    def predict(self, df):
        return pd.Series(
            self.model.predict(DMatrix(df.values), validate_features=False),
            name="Result"
        )

    def get_model(self):
        return self.model


def _load_model_from_local_file(path):
    model = xgb.Booster()
    model.load_model(path)
    return PredictWrapper(model)


def _load_pyfunc(path):
    return _load_model_from_local_file(path)
