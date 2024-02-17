from dataclasses import dataclass
import logging
from typing import Any, Callable, Mapping, Optional, Sequence, Tuple, Union
from uuid import uuid1

# pylint: disable=no-name-in-module
from google.protobuf.struct_pb2 import Value
from google.protobuf.timestamp_pb2 import Timestamp
from google.protobuf.wrappers_pb2 import DoubleValue
from google.protobuf.wrappers_pb2 import Int32Value
# pylint: enable=no-name-in-module
from pydantic import BaseModel
import trulens_eval
from trulens_eval import schema as trulens_schema
from trulens_eval.utils.serial import JSON

from truera.client.cache import MetadataCache
from truera.client.ingestion.schema import python_val_to_pb_value
from truera.client.remote_truera_workspace import RemoteTrueraWorkspace
from truera.client.truera_authentication import TrueraAuthentication
from truera.protobuf.public.common import generative_pb2 as gen_pb
import truera.protobuf.public.metadata_message_types_pb2 as md_pb

EXPERIMENT_SPLIT_NAME = "experiment"


@dataclass
class IngestionContext:
    project_id: str
    data_collection_id: str
    app_id: str
    split_id: str
    feedback_function_name_id_map: Mapping[str, str]


@dataclass
class Production:
    pass


@dataclass
class Experiment:
    pass


@dataclass
class Evaluation:
    pass


class LLMDatasetConfig(BaseModel):
    config: Union[Production, Experiment, Evaluation]


class TruApp():

    @property
    def app(self):
        return self.trulens_app.app

    def __init__(
        self, trulens_app, trace_handler: Callable[[trulens_schema.Record],
                                                   None],
        feedback_handler: Callable[[trulens_schema.FeedbackResult], None]
    ):
        self.trulens_app = trulens_app
        self.trace_handler = trace_handler
        self.feedback_handler = feedback_handler
        self.trulens_app = trulens_app

    def __enter__(self):
        return self.trulens_app.__enter__()

    def __exit__(self, exc_type, exc_value, exc_tb):
        # ingest traces and feedbacks
        ctx = self.trulens_app.recording_contexts.get()
        self.trulens_app.__exit__(exc_type, exc_value, exc_tb)
        for trace in ctx.records:
            trace_uuid = str(uuid1())
            trace.record_id = trace_uuid
            self.trace_handler(trace)
            for feedback_future in trace.feedback_results or []:
                feedback_future.add_done_callback(
                    create_done_callback(
                        feedback_handler=self.feedback_handler,
                        trace_id=trace_uuid
                    )
                )


class TrueraGenerativeTextWorkspace:

    def __init__(
        self,
        connection_string: str,
        authentication: TrueraAuthentication,
        log_level: int = logging.INFO,
        workspace_name: str = "",
    ):
        logging.basicConfig(
        )  # Have to do this in order to enable setting log level below WARNING in jupyter
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        self.remote_tru = RemoteTrueraWorkspace(
            connection_string=connection_string,
            authentication=authentication,
            workspace_name=workspace_name
        )

        self.md_cache = MetadataCache(self.remote_tru)
        trulens_eval.Tru()  # Instantiate trulens_eval.Tru singleton

    def add_project(self, project: str):
        return self.remote_tru.add_project(
            project=project,
            score_type="generative_text",
            input_type="text",
            project_type="application_project"
        )

    def get_projects(self) -> Sequence[str]:
        return self.remote_tru.get_projects()

    def delete_project(self, project: str):
        return self.remote_tru.delete_project(project)

    def get_apps(self, project_name: str) -> Sequence[str]:
        project_id = self._get_application_project_id_from_project_name(
            project_name
        )
        return [a.name for a in self._get_apps(project_id=project_id)]

    def delete_app(self, app_name: str, project_name: str):
        project_id = self._get_application_project_id_from_project_name(
            project_name
        )
        self.remote_tru.artifact_interaction_client.delete_model(
            project_id=project_id, model_name=app_name, recursive=True
        )
        self.remote_tru.delete_data_collection(app_name, recursive=True)

    def _create_app(self, app_name, project_name) -> str:
        """Creates data collection and app of the same name. Returns app id. Also creates experiment split."""
        project_id = self._get_application_project_id_from_project_name(
            project_name
        )
        self.remote_tru.add_data_collection(data_collection_name=app_name)
        data_collection_id = self.remote_tru.ar_client.get_data_collection_metadata(
            project_id=project_id, data_collection_name=app_name
        ).id
        self.remote_tru.data_service_client.create_empty_split(
            project_id=project_id,
            data_collection_id=data_collection_id,
            split_name=EXPERIMENT_SPLIT_NAME
        )
        return self.remote_tru.ar_client.create_model_metadata(
            project_id=project_id,
            data_collection_name=app_name,
            model_id="",
            model_name=app_name,
            model_type="virtual",
            model_output_type="text_output",
            locator=""
        )

    def _get_apps(self, project_id: str) -> Sequence[md_pb.ModelMetadata]:
        return self.remote_tru.ar_client.get_all_model_metadata_in_project(
            project_id=project_id, as_json=False
        )

    def get_feedback_functions(self, project_name: str) -> Sequence[str]:
        return self.remote_tru.artifact_interaction_client.get_all_feedback_function_names_in_project(
            project_id=self.
            _get_application_project_id_from_project_name(project_name)
        )

    def add_user_feedback(
        self, project_name: str, app_name: str, feedback_function_name: str,
        trace_id: str, dataset_type: LLMDatasetConfig, result: float
    ):
        # TODO: implement!
        raise NotImplementedError()

    def run_feedback_function(
        self, project_name: str, app_name: str, trace: trulens_schema.Record,
        feedback_functions: Sequence[trulens_eval.Feedback]
    ):
        # TODO: implement!
        raise NotImplementedError()

    def _wrap_app(
        self,
        app,
        app_class,
        project_name: str,
        app_name: str,
        feedbacks: Sequence[trulens_eval.Feedback],
        dataset_config: LLMDatasetConfig,
    ):
        feedback_function_names = []
        for f in feedbacks:
            if not f.supplied_name:
                raise ValueError(
                    "All Feedback functions must have a supplied name for ingestion!"
                )
            feedback_function_names.append(str(f.supplied_name))
        ingestion_context = self._resolve_ingestion_context(
            project_name=project_name,
            app_name=app_name,
            feedback_function_names=feedback_function_names,
            dataset_config=dataset_config
        )
        return TruApp(
            trulens_app=app_class(app, app_id=app_name, feedbacks=feedbacks),
            trace_handler=lambda trace: self.
            _ingest_trace(trace, ingestion_context),
            feedback_handler=lambda feedback: self.
            _ingest_feedback(feedback, ingestion_context)
        )

    def wrap_basic_app(
        self,
        app: Any,
        project_name: str,
        app_name: str,
        feedbacks: Sequence[trulens_eval.Feedback],
        dataset_config: LLMDatasetConfig,
    ) -> TruApp:
        """Wrap a basic app."""
        return self._wrap_app(
            app=app,
            app_class=trulens_eval.TruBasicApp,
            project_name=project_name,
            app_name=app_name,
            feedbacks=feedbacks,
            dataset_config=dataset_config,
        )

    def wrap_llama_index_app(
        self,
        app: Any,
        project_name: str,
        app_name: str,
        feedbacks: Sequence[trulens_eval.Feedback],
        dataset_config: LLMDatasetConfig,
    ) -> TruApp:
        """Wrap a LlamaIndex app."""
        return self._wrap_app(
            app=app,
            app_class=trulens_eval.TruLlama,
            project_name=project_name,
            app_name=app_name,
            feedbacks=feedbacks,
            dataset_config=dataset_config,
        )

    def wrap_langchain_app(
        self,
        app: Any,
        project_name: str,
        app_name: str,
        feedbacks: Sequence[trulens_eval.Feedback],
        dataset_config: LLMDatasetConfig,
    ) -> TruApp:
        """Wrap a Langchain app."""
        return self._wrap_app(
            app=app,
            app_class=trulens_eval.Langchain,
            project_name=project_name,
            app_name=app_name,
            feedbacks=feedbacks,
            dataset_config=dataset_config,
        )

    def wrap_custom_app(
        self,
        app: Any,
        project_name: str,
        app_name: str,
        feedbacks: Sequence[trulens_eval.Feedback],
        dataset_config: LLMDatasetConfig,
    ) -> TruApp:
        """Wrap a custom app."""
        return self._wrap_app(
            app=app,
            app_class=trulens_eval.TruCustomApp,
            project_name=project_name,
            app_name=app_name,
            feedbacks=feedbacks,
            dataset_config=dataset_config,
        )

    def _resolve_ingestion_context(
        self, project_name: str, app_name: str,
        feedback_function_names: Sequence[str], dataset_config: LLMDatasetConfig
    ) -> IngestionContext:

        project_id = self._get_application_project_id_from_project_name(
            project_name
        )
        existing_apps = self._get_apps(project_id)
        if app_name not in [a.name for a in existing_apps]:
            app_id = self._create_app(
                app_name=app_name, project_name=project_name
            )
            self.logger.info(
                f"App '{app_name}' did not exist. Created new app '{app_name}' in project '{project_name}'."
            )
        else:
            app_id = [a for a in existing_apps if a.name == app_name][0].id
        data_collection_md = self.remote_tru.ar_client.get_data_collection_metadata(
            project_id=project_id,
            data_collection_name=
            app_name  # data collections have the same name as app
        )

        if isinstance(dataset_config.config, Production):
            split_id = data_collection_md.prod_split_id
        elif isinstance(dataset_config.config, Experiment):
            split_id = self.remote_tru.ar_client.get_datasplit_metadata(
                project_id=project_id,
                data_collection_name=app_name,
                datasplit_name=EXPERIMENT_SPLIT_NAME
            ).id
        else:
            raise ValueError(
                f"Dataset config '{dataset_config.config}' not supported. Please use Production or Experiment"
            )

        existing_feedback_functions = {
            f.name: f.id for f in self.remote_tru.ar_client.
            get_all_feedback_function_names_and_ids_in_project(
                project_id=project_id
            )
        }
        for ff_name in feedback_function_names:
            if ff_name not in existing_feedback_functions:
                existing_feedback_functions[
                    ff_name
                ] = self.remote_tru.artifact_interaction_client.create_feedback_function(
                    ff_name, project_id
                )
                self.logger.info(
                    f"Feedback function '{ff_name}' did not exist. Created new feedback function '{ff_name}' in project '{project_name}"
                )

        return IngestionContext(
            project_id=project_id,
            data_collection_id=data_collection_md.id,
            app_id=app_id,
            split_id=split_id,
            feedback_function_name_id_map=existing_feedback_functions
        )

    def _get_application_project_id_from_project_name(
        self, project_name: str
    ) -> str:
        """Get project id from project name. Raises ValueError if project is not an application project."""
        project_metadata = self.remote_tru.ar_client.get_project_metadata(
            project_id=project_name
        )
        if project_metadata.project_type != md_pb.APPLICATION_PROJECT:
            raise ValueError(
                f"Project '{project_name}' is not an generative application project!"
            )
        return project_metadata.id

    def _ingest_trace(
        self, trace: trulens_schema.Record, ingestion_context: IngestionContext
    ) -> None:
        self.remote_tru.streaming_ingress_client.ingest_trace(
            project_id=ingestion_context.project_id,
            data_collection_id=ingestion_context.data_collection_id,
            model_id=ingestion_context.app_id,
            split_id=ingestion_context.split_id,
            trace=trace_to_pb(trace)
        )

    def _ingest_feedback(
        self, feedback_result: trulens_schema.FeedbackResult,
        ingestion_context: IngestionContext
    ) -> None:
        self.remote_tru.streaming_ingress_client.ingest_feedback(
            project_id=ingestion_context.project_id,
            data_collection_id=ingestion_context.data_collection_id,
            model_id=ingestion_context.app_id,
            split_id=ingestion_context.split_id,
            feedback=feedback_result_to_pb(
                feedback_result, ingestion_context=ingestion_context
            )
        )


def record_app_call_method_to_pb(
    record_app_call_method: trulens_schema.RecordAppCallMethod
) -> Value:
    return json_to_value(
        dict(
            path=str(record_app_call_method.path),
            method=json_to_value(
                dict(
                    name=record_app_call_method.method.name,
                    obj={
                        "class": record_app_call_method.method.obj.cls.name,
                        "id": record_app_call_method.method.obj.id
                    }
                )
            )
        )
    )


def perf_to_pb(perf: Optional[trulens_schema.Perf]) -> Value:
    if perf:
        return json_to_value(
            dict(
                start_time=str(perf.start_time.isoformat()),
                end_time=str(perf.end_time.isoformat())
            )
        )
    return json_to_value(None)


def record_app_call_to_pb(
    record_app_call: trulens_schema.RecordAppCall
) -> Value:
    return json_to_value(
        dict(
            stack=[
                record_app_call_method_to_pb(v) for v in record_app_call.stack
            ],
            args=record_app_call.args,
            rets=record_app_call.rets,
            error=record_app_call.error,
            perf=perf_to_pb(record_app_call.perf),
            pid=record_app_call.pid,
            tid=record_app_call.tid
        )
    )


def trace_to_pb(trace: trulens_schema.Record) -> gen_pb.GenerativeTrace:
    if trace.perf:
        start_time = Timestamp()
        start_time.FromDatetime(trace.perf.start_time)
        end_time = Timestamp()
        end_time.FromDatetime(trace.perf.end_time)
    else:
        start_time = None
        end_time = None
    return gen_pb.GenerativeTrace(
        record_id=trace.record_id,
        meta=json_to_value(trace.meta),
        main_input=json_to_value(trace.main_input),
        main_output=json_to_value(trace.main_output),
        main_error=json_to_value(trace.main_error),
        calls=json_to_value([record_app_call_to_pb(c) for c in trace.calls]),
        prompt=json_to_value(trace.main_input
                            ),  # prompt and main_input are the same
        start_time=start_time,
        end_time=end_time,
        cost=cost_to_pb(trace.cost)
    )


def json_to_value(json_value: JSON) -> Value:
    """Turns the trulens_eval JSON into a protobuf Value"""
    # TODO: consolidate the below function into a shared library
    try:
        return python_val_to_pb_value(json_value)
    except:
        return python_val_to_pb_value(str(json_value))


def cost_to_pb(
    cost: Optional[trulens_schema.Cost]
) -> Optional[gen_pb.GenerativeCost]:
    """Turns the trulens_eval Cost into GenerativeCost protobuf"""
    if cost:
        return gen_pb.GenerativeCost(
            n_requests=Int32Value(value=cost.n_requests),
            n_successful_requests=Int32Value(value=cost.n_successful_requests),
            n_classes=Int32Value(value=cost.n_classes),
            n_tokens=Int32Value(value=cost.n_tokens),
            n_stream_chunks=Int32Value(value=cost.n_stream_chunks),
            n_prompt_tokens=Int32Value(value=cost.n_prompt_tokens),
            n_completion_tokens=Int32Value(value=cost.n_completion_tokens),
            cost=DoubleValue(value=cost.cost),
        )
    return None


def feedback_call_to_pb(feedback_call: trulens_schema.FeedbackCall) -> Value:
    return json_to_value(
        dict(
            args=json_to_value(feedback_call.args),
            ret=json_to_value(feedback_call.ret),
        )
    )


def feedback_result_to_pb(
    feedback_result: trulens_schema.FeedbackResult,
    ingestion_context: IngestionContext
) -> gen_pb.GenerativeFeedback:
    evaluation_timestamp = Timestamp()
    evaluation_timestamp.FromDatetime(feedback_result.last_ts)
    feedback_function_id = ingestion_context.feedback_function_name_id_map.get(
        feedback_result.name, feedback_result.feedback_definition_id
    )
    return gen_pb.GenerativeFeedback(
        feedback_function_id=feedback_function_id,
        feedback_result_id=feedback_result.feedback_result_id,
        record_id=feedback_result.record_id,
        result=feedback_result.result,
        meta=json_to_value([c.meta for c in feedback_result.calls]),
        cost=cost_to_pb(feedback_result.cost),
        evaluation_timestamp=evaluation_timestamp,
        calls=json_to_value(
            [feedback_call_to_pb(f) for f in feedback_result.calls]
        ),
    )


def format_feedback_result(
    future_result, trace_id: str
) -> trulens_schema.FeedbackResult:
    """We got to do some jank stuff. 
        * The result isn't actually a result, but a Tuple[Feedback, FeedbackResult]
        * Record_id should be replaced with the uuid1 one
    """
    if isinstance(future_result, Tuple):
        _, feedback_result = future_result
    else:
        feedback_result = future_result
    feedback_result.record_id = trace_id  # trulens doesn't give the right trace_id
    return feedback_result


def create_done_callback(feedback_handler, trace_id: str):
    """Need this function so variable lookup works as expected."""
    #TODO: Delete this method once formatting with uuid1 is no longer necessary
    return lambda f: feedback_handler(
        format_feedback_result(f.result(), trace_id=trace_id)
    )
