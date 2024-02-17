from abc import ABC
from abc import abstractmethod

from truera.protobuf.public.streaming import \
    streaming_ingress_service_pb2 as si_pb


class StreamingIngressServiceCommunicator(ABC):

    @abstractmethod
    def ping(self, req: si_pb.PingRequest) -> si_pb.PingResponse:
        pass

    @abstractmethod
    def ingest_point(
        self, req: si_pb.IngestPointRequest
    ) -> si_pb.IngestPointResponse:
        pass

    @abstractmethod
    def ingest_bulk(
        self, req: si_pb.IngestBulkRequest
    ) -> si_pb.IngestBulkResponse:
        pass

    @abstractmethod
    def ingest_metric(
        self, req: si_pb.IngestMetricRequest
    ) -> si_pb.IngestMetricResponse:
        pass

    @abstractmethod
    def ingest_events(
        self, req: si_pb.IngestEventsRequest
    ) -> si_pb.IngestEventsResponse:
        pass

    @abstractmethod
    def ingest_generative_trace(
        self, req: si_pb.IngestGenerativeTraceRequest
    ) -> si_pb.IngestGenerativeTraceResponse:
        pass

    @abstractmethod
    def ingest_generative_feedback(
        self, req: si_pb.IngestGenerativeFeedbackRequest
    ) -> si_pb.IngestGenerativeFeedbackResponse:
        pass

    @abstractmethod
    def close(self):
        pass
