import pandas as pd
import xgboost as xgb


class PredictProbaWrapper(object):

    def __init__(self, model):
        self.model = model

    def predict(self, df):
        return pd.DataFrame(
            self.model.predict_proba(df, validate_features=False),
            columns=self.model.classes_
        )

    def get_model(self):
        return self.model


def _load_model_from_local_file(path):
    model = xgb.XGBClassifier()
    model.load_model(path)
    return PredictProbaWrapper(model)


def _load_pyfunc(path):
    return _load_model_from_local_file(path)
