from abc import ABC
from abc import abstractmethod

from truera.protobuf.useranalytics import useranalytics_pb2 as useranalytics_pb


class UserAnalyticsCommunicator(ABC):

    @abstractmethod
    def send_analytics_event(
        self,
        req: useranalytics_pb.SendAnalyticsEventRequest,
        request_context=None
    ) -> useranalytics_pb.SendAnalyticsEventResponse:
        pass
