import xgboost as xgb


class PredictWrapper(object):

    def __init__(self, model):
        self.model = model

    def predict(self, df):
        return self.model.predict(df, validate_features=False)

    def get_model(self):
        return self.model


def _load_model_from_local_file(path):
    model = xgb.XGBRegressor()
    model.load_model(path)
    return PredictWrapper(model)


def _load_pyfunc(path):
    return _load_model_from_local_file(path)
