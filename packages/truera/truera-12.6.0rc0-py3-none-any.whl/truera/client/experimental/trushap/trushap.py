import logging
import random
import re
import string
from typing import Any, Mapping, Optional, Sequence

import pandas as pd
import pkg_resources

pkg_resources.require("shap>=0.42.1")
import shap
# pylint: disable=E0102
from shap import *

from truera.client.ingestion import ColumnSpec
from truera.client.ingestion import ModelOutputContext
from truera.client.truera_authentication import TokenAuthentication
from truera.client.truera_workspace import TrueraWorkspace


def _id_generator(
    size: int = 5,
    chars: Optional[str] = None,
) -> str:
    if chars is None:
        chars = string.ascii_lowercase + string.digits
    return "".join(random.choice(chars) for _ in range(size))


def _filter_kwargs(kwargs: Mapping[str, str],
                   extracted_kws: Sequence[str]) -> Mapping[str, str]:
    return {x: kwargs[x] for x in extracted_kws if x in kwargs}


def _infer_classification_or_regression(model: Any) -> bool:
    if hasattr(model, "predict_proba"):
        return "classification"
    if hasattr(model, "predict"):
        return "regression"
    raise ValueError(
        "Cannot discern if model is classifier or regressor! Pass in `score_type`!"
    )


class Explainer(shap.Explainer):

    def __init__(self, model: object, *args, **kwargs):
        """Construct a SHAP-style explainer that also uploads to your TruEra deployment if supplied.

        Notes: 
            Because this class is primarily a wrapper, a large number of kwargs (described below) are available.
            All kwargs are noted described below by the function they are passed to, either in SHAP or TruEra.
            Please refer to (https://shap.readthedocs.io) or TruEra (https://docs.truera.com) documentation respectively for full description of use.

        Args:
            model: model object
            **connection_string: URL of the TruEra deployment. Defaults to None.
            **token: Authentication token to connect to TruEra deployment. Defaults to None.
            **masker: Argument needed for SHAP `Explainer`
            **link: Argument needed for SHAP `Explainer`
            **algorithm: Argument needed for SHAP `Explainer`
            **output_names: Argument needed for SHAP `Explainer`
            **feature_names: Argument needed for SHAP `Explainer`
            **linearize_link: Argument needed for SHAP `Explainer`
            **seed: Argument needed for SHAP `Explainer`
            **input_type: Argument needed for `add_project`
            **num_default_influences: Argument needed for `add_project`
            **pre_to_post_feature_map: Argument needed for `add_data_collection`
            **provide_transform_with_model: Argument needed for `add_data_collection`
            **additional_pip_dependencies: Argument needed for 'add_python_model`
            **additional_modules: Argument needed for `add_python_model`
            **classification_threshhold: Argument needed for `add_python_model`
            **train_split_name: Argument needed for `add_python_model`
            **train_parameters: Argument needed for `add_python_model`
            **verify_model: Argument needed for `add_python_model`
            **compute_predictions: Argument needed for `add_python_model`
            **compute_feature_influences: Argument needed for `add_python_model`
            **compute_for_all_splits: Argument needed for `add_python_model`
        """

        # Get shap explainer.
        shap_explainer_kwargs = _filter_kwargs(
            kwargs, [
                "masker", "link", "algorithm", "output_names", "feature_names",
                "linearize_link", "seed"
            ]
        )
        self.shap_explainer = shap.Explainer(
            model, *args, **shap_explainer_kwargs
        )

        # Set up TruEra.
        self.connection_string = kwargs.get("connection_string", None)
        self.token = kwargs.get("token", None)
        if self.connection_string is None or self.token is None:
            logging.warning(
                "`connection_string` or `token` not specified. Contact TruEra for help (support.truera.com)."
            )
        else:
            logging.info(
                f"Access your TruEra application at: {self.connection_string}"
            )

            # Create TrueraWorkspace.
            self.tru = TrueraWorkspace(
                self.connection_string,
                TokenAuthentication(self.token),
                log_level=logging.ERROR
            )

            # Add project.
            project = kwargs.get("project", f"project_{_id_generator()}")
            influence_type = kwargs.get("influence_type", "shap")
            score_type = kwargs.get("score_type", None)
            if score_type is None:
                output_type = _infer_classification_or_regression(model)
                score_type = "probits" if output_type == "classification" else "regression"
            add_project_kwargs = _filter_kwargs(
                kwargs, ["input_type", "num_default_influences"]
            )
            if project in self.tru.get_projects():
                logging.info(
                    f"Project already exists, setting context to {project}"
                )
                self.tru.set_project(project)
            else:
                self.tru.add_project(
                    project=project,
                    score_type=score_type,
                    **add_project_kwargs
                )
                logging.info(f"Added project: {project}")

            self.tru.set_influence_type(influence_type)
            # Add data collection.
            data_collection_name = kwargs.get(
                "data_collection_name", f"data_collection_{_id_generator()}"
            )
            add_data_collection_kwargs = _filter_kwargs(
                kwargs,
                ["pre_to_post_feature_map", "provide_transform_with_model"]
            )
            if data_collection_name in self.tru.get_data_collections():
                logging.info(
                    f"Data Collection already exists, setting context to {data_collection_name}"
                )
                self.tru.set_data_collection(data_collection_name)
            else:
                self.tru.add_data_collection(
                    data_collection_name=data_collection_name,
                    **add_data_collection_kwargs
                )
                logging.info(f"Added data collection: {data_collection_name}")

            # Add model.
            model_name = kwargs.get("model_name", None)
            if model_name is None:
                model_name = re.split(
                    r'[`!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?~]', str(model)
                )[0] + str("_") + _id_generator()
            add_python_model_kwargs = _filter_kwargs(
                kwargs, [
                    "additional_pip_dependencies", "additional_modules",
                    "classification_threshhold", "train_split_name",
                    "train_parameters", "verify_model", "compute_predictions",
                    "compute_feature_influences", "compute_for_all_splits"
                ]
            )
            if model_name in self.tru.get_models():
                logging.info(
                    f"Model already exists, setting context to {model_name}"
                )
                self.tru.set_model(model_name)
            else:
                self.tru.add_python_model(
                    model_name=model_name,
                    model=model,
                    **add_python_model_kwargs
                )
            logging.info(f"Added model: {model_name}")

    def __call__(self, *args, **kwargs) -> pd.DataFrame:
        """Get the shap values for a list of parallel iterable datasets using the model agnostic explainer. Also upload the first dataset in the list to TruEra if connection supplied.

        Notes:
            Because this class is primarily a wrapper, a large number of kwargs (described below) are available.
            All kwargs are noted described below by the function they are passed to, either in SHAP or TruEra.
            Please refer to SHAP (https://shap.readthedocs.io) or TruEra (https://docs.truera.com) documentation respectively for full description of use.

            If you pass more than one dataset using *args, post_data, outputs/label_data, and extra_data_df will not be added to TruEra.

        Args:
            *args: a list of parallel iterable datasets
            **max_evals: Argument needed for SHAP `__call__`
            **main_effects: Argument needed for SHAP `__call__`
            **error_bounds: Argument needed for SHAP `__call__`
            **batch_size: Argument needed for SHAP `__call__`
            **outputs: Argument needed for SHAP `__call__`
            **silent: Argument needed for SHAP `__call__`
            **id_col_name: Column corresponding to unique id of each data point
            **timestamp_col_name: Column corresponding to timestamp of each data point
            **pre_data_col_names: Column(s) corresponding to feature data. If post_data_col_names are not provided, pre_data_col_names columns are assumed to be both human- and model-readable.
            **post_data_col_names: Column(s) corresponding to model-readable post-processed data; can be ignored if pre_data_col_names data is provided.
            **prediction_col_names: Column(s) corresponding to model predictions.
            **label_col_names: Column(s) corresponding to labels or ground truth data.
            **extra_data_col_names: Column(s) corresponding to features not used/consumed by the model, but which could be used for other analysis, such as defining segments.
            **feature_influence_col_names: Column(s) corresponding to feature influence data; can be suffixed with _truera-qii_influence or _shap_influence to prevent duplicate name issues.
            **tags_col_name: Column corresponding to tags attached to the data.

        """
        ret = []
        shap_explainer_shap_values_kwargs = _filter_kwargs(
            kwargs, [
                "max_evals", "main_effects", "error_bounds", "batch_size",
                "silent"
            ]
        )
        for data in args:
            data_for_model = data.copy()

            id_col_name = kwargs.get("id_col_name", None)
            if id_col_name:
                data_for_model.drop(id_col_name, axis=1, inplace=True)
            else:
                id_col_name = "id"

            prediction_col_names = kwargs.get("prediction_col_names", None)
            if prediction_col_names:
                data_for_model.drop(prediction_col_names, axis=1, inplace=True)

            label_col_names = kwargs.get("label_col_names", None)
            if label_col_names:
                data_for_model.drop(label_col_names, axis=1, inplace=True)

            post_data_col_names = kwargs.get("post_data_col_names", None)
            if post_data_col_names:
                data_for_model.drop(post_data_col_names, axis=1, inplace=True)

            extra_data_col_names = kwargs.get("extra_data_col_names", None)
            if extra_data_col_names:
                data_for_model.drop(extra_data_col_names, axis=1, inplace=True)

            feature_influence_col_names = kwargs.get(
                "feature_influence_col_names", None
            )
            if feature_influence_col_names:
                data_for_model.drop(
                    feature_influence_col_names, axis=1, inplace=True
                )

            tags_col_name = kwargs.get("tags_col_name", None)
            if tags_col_name:
                data_for_model.drop(tags_col_name, axis=1, inplace=True)

            ret.append(
                self.shap_explainer(
                    data_for_model, **shap_explainer_shap_values_kwargs
                )
            )
        ret = ret[0] if len(ret) == 1 else ret

        if self.connection_string is None or self.token is None:
            return ret

        # data split
        data_split_name = kwargs.get(
            "data_split_name", f"data_split_{_id_generator()}"
        )
        add_data_kwargs = _filter_kwargs(kwargs, ["model_output_context"])
        column_spec_kwargs = _filter_kwargs(
            kwargs, [
                "timestamp_col_name", "pre_data_col_names",
                "post_data_col_names", "prediction_col_names",
                "label_col_names", "extra_data_col_names",
                "feature_influence_col_names", "tags_col_names"
            ]
        )

        if data_split_name in self.tru.get_data_splits():
            logging.info(f"{data_split_name} already exists, skipped")
        else:
            for data in args:
                if data_split_name is None:
                    data_split_name = f"data_split_{_id_generator()}"
                self.tru.add_data(
                    data_split_name=data_split_name,
                    data=data,
                    column_spec=ColumnSpec(
                        id_col_name=id_col_name, **column_spec_kwargs
                    ),
                    **add_data_kwargs
                )
                logging.info(f"Added data split: {data_split_name}")

        self.tru.set_data_split(data_split_name)
        # compute predictions
        self.tru.compute_predictions()
        logging.info(f"Computed predictions for: {data_split_name}")
        # compute feature infs
        self.tru.set_influences_background_data_split(data_split_name)
        self.tru.compute_feature_influences()
        logging.info(f"Computed feature influences for: {data_split_name}")
        kwargs.get("id_col_name", None)
        if "label_col_names" in kwargs:
            # compute error infs
            self.tru.compute_feature_influences(
                score_type="mean_absolute_error_for_regression"
            )
            logging.info(f"Computed error influences for: {data_split_name}")
        return ret

    def get_truera_workspace(self) -> TrueraWorkspace:
        """Fetch the TruEra workspace associated with the `Explainer`.
        """
        return self.tru
