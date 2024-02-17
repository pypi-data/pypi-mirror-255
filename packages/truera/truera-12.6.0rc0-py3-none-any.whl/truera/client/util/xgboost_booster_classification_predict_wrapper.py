import numpy as np
import pandas as pd
from xgboost import DMatrix
import xgboost as xgb


class PredictProbaWrapper(object):

    def __init__(self, model):
        self.model = model

    def predict(self, df):
        preds = self.model.predict(DMatrix(df.values), validate_features=False)
        return pd.DataFrame(
            data=np.column_stack([1 - preds, preds]), columns=[0, 1]
        )

    def get_model(self):
        return self.model


def _load_model_from_local_file(path):
    model = xgb.Booster()
    model.load_model(path)
    return PredictProbaWrapper(model)


def _load_pyfunc(path):
    return _load_model_from_local_file(path)
