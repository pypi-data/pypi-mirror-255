import logging
from typing import Any, Dict, List, Mapping, Sequence, Union

from google.protobuf.struct_pb2 import \
    Value  # pylint: disable=no-name-in-module

from truera.client.ingestion.schema import python_val_to_pb_value
from truera.client.public.auth_details import AuthDetails
from truera.client.public.communicator.streaming_ingress_communicator import \
    StreamingIngressServiceCommunicator
from truera.client.public.communicator.streaming_ingress_http_communicator import \
    HttpStreamingIngressServiceCommunicator
from truera.protobuf.public.common import generative_pb2 as gen_pb
from truera.protobuf.public.streaming import \
    streaming_ingress_service_pb2 as si_pb


class StreamingIngressClient():

    def __init__(
        self,
        communicator: StreamingIngressServiceCommunicator,
        logger=None
    ) -> None:
        self.logger = logger if logger else logging.getLogger(__name__)
        self.communicator = communicator

    @classmethod
    def create(
        cls,
        connection_string: str = None,
        logger=None,
        auth_details: AuthDetails = None,
        use_http: bool = False,
        *,
        verify_cert: Union[bool, str] = True
    ):
        if use_http:
            communicator = HttpStreamingIngressServiceCommunicator(
                connection_string,
                auth_details,
                logger,
                verify_cert=verify_cert
            )
        else:
            from truera.client.private.communicator.streaming_ingress_grpc_communicator import \
                GrpcStreamingIngressServiceCommunicator
            communicator = GrpcStreamingIngressServiceCommunicator(
                connection_string, auth_details, logger
            )
        return StreamingIngressClient(communicator, logger)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        self.communicator.close()

    def ping(self):
        return self.communicator.ping(si_pb.PingRequest())

    def ingest_point(
        self,
        project_id: str,
        data_collection_id: str,
        **kwargs,
    ):
        req = si_pb.IngestPointRequest(
            project_id=project_id,
            data_collection_id=data_collection_id,
            **kwargs,
        )
        return self.communicator.ingest_point(req)

    def ingest_bulk(
        self,
        project_id: str,
        data_collection_id: str,
        points: List[si_pb.BulkPoint],
        **kwargs,
    ):
        req = si_pb.IngestBulkRequest(
            project_id=project_id,
            data_collection_id=data_collection_id,
            points=points,
            **kwargs,
        )
        return self.communicator.ingest_bulk(req)

    def ingest_metric(
        self,
        project_id: str,
        metrics: Dict[str, float],
        *,
        timestamp: str = "",
        point_id: str = "",
        **kwargs,
    ):
        req = si_pb.IngestMetricRequest(
            project_id=project_id,
            timestamp=timestamp,
            metrics=metrics,
            point_id=point_id,
            **kwargs,
        )
        return self.communicator.ingest_metric(req)

    def ingest_events(
        self, project_id: str, model_id: str, events: Sequence[Mapping[str,
                                                                       Any]]
    ) -> si_pb.IngestEventsResponse:
        req = si_pb.IngestEventsRequest(
            project_id=project_id,
            model_id=model_id,
            events=[
                si_pb.Event(
                    data={
                        k: python_val_to_pb_value(v) for k, v in event.items()
                    }
                ) for event in events
            ]
        )
        return self.communicator.ingest_events(req)

    def ingest_generative_trace(
        self,
        trace_id: str,
        project_id: str,
        data_collection_id: str,
        split_id: str,
        model_id: str,
        prompt: str,
        cost,
        **kwargs,
    ):
        req = si_pb.IngestGenerativeTraceRequest(
            project_id=project_id,
            data_collection_id=data_collection_id,
            split_id=split_id,
            model_id=model_id,
            trace=gen_pb.GenerativeTrace(
                prompt=Value(string_value=prompt),
                record_id=trace_id,
                cost=cost,
            ),
            **kwargs,
        )
        return self.communicator.ingest_generative_trace(req)

    def ingest_generative_feedback(
        self,
        trace_id: str,
        project_id: str,
        data_collection_id: str,
        split_id: str,
        model_id: str,
        feedback_result_id: str,
        feedback_function_id: str,
        feedback_result,
        cost,
        **kwargs,
    ):
        req = si_pb.IngestGenerativeFeedbackRequest(
            project_id=project_id,
            data_collection_id=data_collection_id,
            split_id=split_id,
            model_id=model_id,
            feedback=gen_pb.GenerativeFeedback(
                feedback_result_id=feedback_result_id,
                feedback_function_id=feedback_function_id,
                record_id=trace_id,
                result=feedback_result,
                cost=cost,
            ),
            **kwargs,
        )
        return self.communicator.ingest_generative_feedback(req)

    def ingest_feedback(
        self, project_id: str, data_collection_id: str, split_id: str,
        model_id: str, feedback: gen_pb.GenerativeFeedback
    ):
        req = si_pb.IngestGenerativeFeedbackRequest(
            project_id=project_id,
            data_collection_id=data_collection_id,
            split_id=split_id,
            model_id=model_id,
            feedback=feedback
        )
        return self.communicator.ingest_generative_feedback(req)

    def ingest_trace(
        self, project_id: str, data_collection_id: str, split_id: str,
        model_id: str, trace: gen_pb.GenerativeTrace
    ):
        req = si_pb.IngestGenerativeTraceRequest(
            project_id=project_id,
            data_collection_id=data_collection_id,
            split_id=split_id,
            model_id=model_id,
            trace=trace
        )
        return self.communicator.ingest_generative_trace(req)
