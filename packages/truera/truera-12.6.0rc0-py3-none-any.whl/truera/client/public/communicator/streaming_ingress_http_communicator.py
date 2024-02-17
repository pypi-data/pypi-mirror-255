import logging
from typing import Union

from truera.client.public.auth_details import AuthDetails
from truera.client.public.communicator.http_communicator import \
    HttpCommunicator
from truera.client.public.communicator.streaming_ingress_communicator import \
    StreamingIngressServiceCommunicator
from truera.protobuf.public.streaming import \
    streaming_ingress_service_pb2 as si_pb


class HttpStreamingIngressServiceCommunicator(
    StreamingIngressServiceCommunicator
):

    def __init__(
        self,
        connection_string: str,
        auth_details: AuthDetails,
        logger: logging.Logger,
        *,
        verify_cert: Union[bool, str] = True
    ):
        connection_string = connection_string.rstrip("/")
        self.connection_string = f"{connection_string}/api/v0/ingest"
        self.http_communicator = HttpCommunicator(
            connection_string=self.connection_string,
            auth_details=auth_details,
            logger=logger,
            verify_cert=verify_cert
        )
        self.http_communicator.__not_supported_message = "RPC not supported via HTTP client"

    def ping(self, req: si_pb.PingRequest) -> si_pb.PingResponse:
        uri = f"{self.connection_string}/streaming/ping"
        json_req = self.http_communicator._proto_to_json(req)
        json_resp = self.http_communicator.get_request(uri, json_req)
        return self.http_communicator._json_to_proto(
            json_resp, si_pb.PingResponse()
        )

    def ingest_point(
        self, req: si_pb.IngestPointRequest
    ) -> si_pb.IngestPointResponse:
        uri = f"{self.connection_string}/streaming/point"
        json_req = self.http_communicator._proto_to_json(req)
        json_resp = self.http_communicator.post_request(uri, json_req)
        return self.http_communicator._json_to_proto(
            json_resp, si_pb.IngestPointResponse()
        )

    def ingest_bulk(
        self, req: si_pb.IngestBulkRequest
    ) -> si_pb.IngestBulkResponse:
        uri = f"{self.connection_string}/streaming/bulk"
        json_req = self.http_communicator._proto_to_json(req)
        json_resp = self.http_communicator.post_request(uri, json_req)
        return self.http_communicator._json_to_proto(
            json_resp, si_pb.IngestBulkResponse()
        )

    def ingest_metric(
        self, req: si_pb.IngestMetricRequest
    ) -> si_pb.IngestMetricResponse:
        uri = f"{self.connection_string}/streaming/metric"
        json_req = self.http_communicator._proto_to_json(req)
        json_resp = self.http_communicator.post_request(uri, json_req)
        return self.http_communicator._json_to_proto(
            json_resp, si_pb.IngestMetricResponse()
        )

    def ingest_events(
        self, req: si_pb.IngestEventsRequest
    ) -> si_pb.IngestEventsResponse:
        uri = f"{self.connection_string}/streaming/events"
        json_req = self.http_communicator._proto_to_json(req)
        json_resp = self.http_communicator.post_request(uri, json_req)
        return self.http_communicator._json_to_proto(
            json_resp, si_pb.IngestEventsResponse()
        )

    def ingest_generative_trace(
        self, req: si_pb.IngestGenerativeTraceRequest
    ) -> si_pb.IngestGenerativeTraceResponse:
        uri = f"{self.connection_string}/streaming/generative/trace"
        json_req = self.http_communicator._proto_to_json(req)
        json_resp = self.http_communicator.post_request(uri, json_req)
        return self.http_communicator._json_to_proto(
            json_resp, si_pb.IngestGenerativeTraceResponse()
        )

    def ingest_generative_feedback(
        self, req: si_pb.IngestGenerativeFeedbackRequest
    ) -> si_pb.IngestGenerativeFeedbackResponse:
        uri = f"{self.connection_string}/streaming/generative/feedback"
        json_req = self.http_communicator._proto_to_json(req)
        json_resp = self.http_communicator.post_request(uri, json_req)
        return self.http_communicator._json_to_proto(
            json_resp, si_pb.IngestGenerativeFeedbackResponse()
        )

    def close(self):
        self.http_communicator.close()
