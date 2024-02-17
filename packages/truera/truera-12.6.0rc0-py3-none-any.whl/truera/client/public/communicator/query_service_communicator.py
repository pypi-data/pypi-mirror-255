from abc import ABC
from abc import abstractmethod
from typing import Iterable

from truera.protobuf.queryservice import query_service_pb2 as qs_pb


class AbstractQueryServiceCommunicator(ABC):

    @abstractmethod
    def echo(self, request: qs_pb.EchoRequest) -> qs_pb.EchoResponse:
        pass

    @abstractmethod
    def query(
        self,
        request: qs_pb.QueryRequest,
        request_context=None,
        ignore_response=False
    ) -> Iterable[qs_pb.QueryResponse]:
        pass

    @abstractmethod
    def accuracy(
        self,
        request: qs_pb.AccuracyRequest,
        request_context=None
    ) -> qs_pb.AccuracyResponse:
        pass
