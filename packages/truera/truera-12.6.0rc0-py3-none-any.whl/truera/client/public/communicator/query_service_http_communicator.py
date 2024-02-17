import json
import logging
import time
from typing import List, Union

from truera.client.public.auth_details import AuthDetails
from truera.client.public.communicator.http_communicator import \
    HttpCommunicator
from truera.client.public.communicator.query_service_communicator import \
    AbstractQueryServiceCommunicator
from truera.protobuf.queryservice import query_service_pb2 as qs_pb


class HttpQueryServiceCommunicator(
    HttpCommunicator, AbstractQueryServiceCommunicator
):

    def __init__(
        self,
        connection_string: str,
        auth_details: AuthDetails = None,
        logger=None,
        verify_cert: Union[bool, str] = True,
    ):
        connection_string = connection_string.rstrip("/")
        self.connection_string = f"{connection_string}/api/query"
        self.http_communicator = HttpCommunicator(
            connection_string=connection_string,
            auth_details=auth_details,
            logger=logger,
            verify_cert=verify_cert
        )
        self.logger = logger if logger else logging.getLogger(__name__)

    def echo(self, request: qs_pb.EchoRequest) -> qs_pb.EchoResponse:
        uri = f"{self.connection_string}/queryservice/echo/{request.request_id}/{request.message}"
        json_resp = self.http_communicator.get_request(uri, None)
        return self.http_communicator._json_to_proto(
            json_resp, qs_pb.EchoResponse()
        )

    def query(
        self,
        request: qs_pb.QueryRequest,
        request_context=None,
        ignore_response=False
    ) -> List[qs_pb.QueryResponse]:
        uri = f"{self.connection_string}/queryservice/query"
        json_req = self.http_communicator._proto_to_json(request)
        resp_content_arr = []
        start = time.time()
        ttfb = None
        with self.http_communicator.post_request(
            uri, json_data_or_generator=json_req, stream=True
        ) as response:
            if ttfb is None:
                ttfb = time.time() - start
            self.http_communicator._handle_response(response)
            response.encoding = "UTF-8"
            for body in response.iter_content(
                chunk_size=None, decode_unicode=True
            ):
                resp_content_arr.append(body)
        transfer_complete = time.time() - start
        if ignore_response:
            # self.logger.info(f"ttfb: {ttfb}, transfer: {transfer_complete}")
            return None
        json_str = "".join(resp_content_arr)
        response_protos = self.http_communicator._json_arr_to_proto_list(
            json_str, qs_pb.QueryResponse()
        )
        end = time.time() - start
        self.logger.info(
            f"ttfb: {ttfb}, transfer: {transfer_complete}, end: {end}"
        )
        return response_protos

    def accuracy(
        self,
        request: qs_pb.AccuracyRequest,
        request_context=None
    ) -> qs_pb.AccuracyResponse:
        uri = f"{self.connection_string}/queryservice/accuracy"
        json_req = self.http_communicator._proto_to_json(request)
        response = self.http_communicator.post_request(
            uri, json_data_or_generator=json_req
        )
        return self.http_communicator._json_to_proto(
            response, qs_pb.AccuracyResponse()
        )
