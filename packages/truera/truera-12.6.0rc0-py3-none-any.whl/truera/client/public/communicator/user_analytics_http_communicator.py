import logging
from typing import Union

from truera.client.public.auth_details import AuthDetails
from truera.client.public.communicator.http_communicator import \
    HttpCommunicator
from truera.client.public.communicator.user_analytics_communicator import \
    UserAnalyticsCommunicator
from truera.protobuf.useranalytics import useranalytics_pb2 as useranalytics_pb


class HttpUserAnalyticsCommunicator(UserAnalyticsCommunicator):

    def __init__(
        self,
        connection_string: str,
        auth_details: AuthDetails,
        logger: logging.Logger,
        *,
        verify_cert: Union[bool, str] = True
    ):
        connection_string = connection_string.rstrip("/")
        self.connection_string = f"{connection_string}/api/useranalytics"
        self.http_communicator = HttpCommunicator(
            connection_string=self.connection_string,
            auth_details=auth_details,
            logger=logger,
            verify_cert=verify_cert
        )
        self.http_communicator.__not_supported_message = "RPC not supported via HTTP client"

    def send_analytics_event(
        self,
        req: useranalytics_pb.SendAnalyticsEventRequest,
        request_context=None
    ) -> useranalytics_pb.SendAnalyticsEventResponse:
        uri = f"{self.connection_string}/useranalytics/send"
        json_req = self.http_communicator._proto_to_json(req)
        json_resp = self.http_communicator.post_request(uri, json_req)
        return self.http_communicator._json_to_proto(
            json_resp, useranalytics_pb.SendAnalyticsEventResponse()
        )

    def close(self):
        self.http_communicator.close()
