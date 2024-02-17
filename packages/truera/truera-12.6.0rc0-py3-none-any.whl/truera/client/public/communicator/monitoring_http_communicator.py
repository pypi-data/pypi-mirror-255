import logging
from typing import Union

from truera.client.public.auth_details import AuthDetails
from truera.client.public.communicator.http_communicator import \
    HttpCommunicator
from truera.client.public.communicator.monitoring_communicator import \
    MonitoringCommunicator
from truera.protobuf.monitoring import \
    monitoring_dashboard_pb2 as monitoring_dashboard_pb2


class HttpMonitoringCommunicator(MonitoringCommunicator):

    def __init__(
        self,
        connection_string: str,
        auth_details: AuthDetails,
        logger: logging.Logger,
        *,
        verify_cert: Union[bool, str] = True
    ):
        connection_string = connection_string.rstrip("/")
        self.connection_string = f"{connection_string}/api/monitoring"
        self.logger = logger
        self.http_communicator = HttpCommunicator(
            connection_string=self.connection_string,
            auth_details=auth_details,
            logger=logger,
            verify_cert=verify_cert
        )

    def query_data(
        self,
        req: monitoring_dashboard_pb2.QueryDataRequest,
        request_context=None
    ) -> monitoring_dashboard_pb2.QueryDataResponse:
        uri = f"{self.connection_string}/querydata"
        json_req = self.http_communicator._proto_to_json(req)
        json_resp = self.http_communicator.get_request(uri, {}, body=json_req)
        return self.http_communicator._json_to_proto(
            json_resp, monitoring_dashboard_pb2.QueryDataResponse()
        )

    def create_dashboard(
        self,
        req: monitoring_dashboard_pb2.CreateDashboardRequest,
        request_context=None
    ) -> monitoring_dashboard_pb2.CreateDashboardResponse:
        uri = f"{self.connection_string}/dashboard"
        json_req = self.http_communicator._proto_to_json(req)
        json_resp = self.http_communicator.post_request(uri, json_req)
        return self.http_communicator._json_to_proto(
            json_resp, monitoring_dashboard_pb2.CreateDashboardResponse()
        )

    def update_dashboard(
        self,
        req: monitoring_dashboard_pb2.UpdateDashboardRequest,
        request_context=None
    ) -> monitoring_dashboard_pb2.UpdateDashboardResponse:
        uri = f"{self.connection_string}/dashboard/{req.dashboard_detail.dashboard_id}"
        json_req = self.http_communicator._proto_to_json(req)
        json_resp = self.http_communicator.put_request(uri, json_req)
        return self.http_communicator._json_to_proto(
            json_resp, monitoring_dashboard_pb2.UpdateDashboardResponse()
        )

    def get_dashboard(
        self,
        req: monitoring_dashboard_pb2.GetDashboardRequest,
        request_context=None
    ) -> monitoring_dashboard_pb2.GetDashboardResponse:
        uri = f"{self.connection_string}/dashboard/{req.dashboard_id}"
        json_req = self.http_communicator._proto_to_json(req)
        json_resp = self.http_communicator.get_request(uri, json_req)
        return self.http_communicator._json_to_proto(
            json_resp, monitoring_dashboard_pb2.GetDashboardResponse()
        )

    def delete_dashboard(
        self,
        req: monitoring_dashboard_pb2.DeleteDashboardRequest,
        request_context=None
    ) -> monitoring_dashboard_pb2.DeleteDashboardResponse:
        uri = f"{self.connection_string}/dashboard/{req.dashboard_id}"
        json_req = self.http_communicator._proto_to_json(req)
        json_resp = self.http_communicator.delete_request(uri, json_req)
        return self.http_communicator._json_to_proto(
            json_resp, monitoring_dashboard_pb2.DeleteDashboardResponse()
        )

    def list_dashboards(
        self,
        req: monitoring_dashboard_pb2.ListDashboardsRequest,
        request_context=None
    ) -> monitoring_dashboard_pb2.ListDashboardsResponse:
        uri = f"{self.connection_string}/dashboards"
        json_req = self.http_communicator._proto_to_json(req)
        json_resp = self.http_communicator.get_request(uri, json_req)
        return self.http_communicator._json_to_proto(
            json_resp, monitoring_dashboard_pb2.ListDashboardsResponse()
        )

    def validate_time_range_split_bounds(
        self,
        req: monitoring_dashboard_pb2.ValidateTimeRangeSplitBoundsRequest,
        request_context=None
    ) -> monitoring_dashboard_pb2.ValidateTimeRangeSplitBoundsResponse:
        raise NotImplementedError(
            "validate_time_range_split_bounds is not implemented for HTTP communicator"
        )

    def list_segment_tags(
        self,
        req: monitoring_dashboard_pb2.ListSegmentTagsRequest,
        request_context=None
    ) -> monitoring_dashboard_pb2.ListSegmentTagsResponse:
        raise NotImplementedError(
            "list_segment_tags is not implemented for HTTP communicator"
        )

    def list_custom_metrics(
        self,
        req: monitoring_dashboard_pb2.ListCustomMetricsRequest,
        request_context=None
    ) -> monitoring_dashboard_pb2.ListCustomMetricsResponse:
        raise NotImplementedError(
            "list_custom_metrics is not implemented for HTTP communicator"
        )
