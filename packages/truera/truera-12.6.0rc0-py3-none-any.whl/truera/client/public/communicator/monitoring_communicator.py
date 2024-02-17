from abc import ABC
from abc import abstractmethod

from truera.protobuf.monitoring import \
    monitoring_dashboard_pb2 as monitoring_dashboard_pb2


class MonitoringCommunicator(ABC):

    @abstractmethod
    def query_data(
        self,
        req: monitoring_dashboard_pb2.QueryDataRequest,
        request_context=None
    ) -> monitoring_dashboard_pb2.QueryDataResponse:
        pass

    @abstractmethod
    def create_dashboard(
        self,
        req: monitoring_dashboard_pb2.CreateDashboardRequest,
        request_context=None
    ) -> monitoring_dashboard_pb2.CreateDashboardResponse:
        pass

    @abstractmethod
    def update_dashboard(
        self,
        req: monitoring_dashboard_pb2.UpdateDashboardRequest,
        request_context=None
    ) -> monitoring_dashboard_pb2.UpdateDashboardResponse:
        pass

    @abstractmethod
    def get_dashboard(
        self,
        req: monitoring_dashboard_pb2.GetDashboardRequest,
        request_context=None
    ) -> monitoring_dashboard_pb2.GetDashboardResponse:
        pass

    @abstractmethod
    def delete_dashboard(
        self,
        req: monitoring_dashboard_pb2.DeleteDashboardRequest,
        request_context=None
    ) -> monitoring_dashboard_pb2.DeleteDashboardResponse:
        pass

    @abstractmethod
    def list_dashboards(
        self,
        req: monitoring_dashboard_pb2.ListDashboardsRequest,
        request_context=None
    ) -> monitoring_dashboard_pb2.ListDashboardsResponse:
        pass

    @abstractmethod
    def validate_time_range_split_bounds(
        self,
        req: monitoring_dashboard_pb2.ValidateTimeRangeSplitBoundsRequest,
        request_context=None
    ) -> monitoring_dashboard_pb2.ValidateTimeRangeSplitBoundsResponse:
        pass

    @abstractmethod
    def list_segment_tags(
        self,
        req: monitoring_dashboard_pb2.ListSegmentTagsRequest,
        request_context=None
    ) -> monitoring_dashboard_pb2.ListSegmentTagsResponse:
        pass

    @abstractmethod
    def list_custom_metrics(
        self,
        req: monitoring_dashboard_pb2.ListCustomMetricsRequest,
        request_context=None
    ) -> monitoring_dashboard_pb2.ListCustomMetricsResponse:
        pass
