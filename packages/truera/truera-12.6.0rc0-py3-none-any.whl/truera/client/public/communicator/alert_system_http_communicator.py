import logging
from typing import Union

from truera.client.public.auth_details import AuthDetails
from truera.client.public.communicator.alert_system_communicator import \
    AlertSystemCommunicator
from truera.client.public.communicator.http_communicator import \
    HttpCommunicator
from truera.protobuf.monitoring import alert_service_pb2


class HttpAlertSystemCommunicator(AlertSystemCommunicator):

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

    def enable_alerting(
        self,
        req: alert_service_pb2.EnableAlertingRequest,
        request_context=None
    ) -> alert_service_pb2.EnableAlertingResponse:
        uri = f"{self.connection_string}/alertservice/enable"
        json_req = self.http_communicator._proto_to_json(req)
        json_resp = self.http_communicator.post_request(uri, json_req)
        return self.http_communicator._json_to_proto(
            json_resp, alert_service_pb2.EnableAlertingResponse()
        )

    def disable_alerting(
        self,
        req: alert_service_pb2.DisableAlertingRequest,
        request_context=None
    ) -> alert_service_pb2.DisableAlertingResponse:
        uri = f"{self.connection_string}/alertservice/disable"
        json_req = self.http_communicator._proto_to_json(req)
        json_resp = self.http_communicator.post_request(uri, json_req)
        return self.http_communicator._json_to_proto(
            json_resp, alert_service_pb2.DisableAlertingResponse()
        )

    def add_alert_rule(
        self,
        req: alert_service_pb2.AddAlertRuleRequest,
        request_context=None
    ) -> alert_service_pb2.AddAlertRuleResponse:
        uri = f"{self.connection_string}/alertservice/rules/{req.request.dashboard_id}"
        json_req = self.http_communicator._proto_to_json(req)
        json_resp = self.http_communicator.post_request(uri, json_req)
        return self.http_communicator._json_to_proto(
            json_resp, alert_service_pb2.AddAlertRuleResponse()
        )

    def get_alert_rule(
        self,
        req: alert_service_pb2.GetAlertRuleRequest,
        request_context=None
    ) -> alert_service_pb2.GetAlertRuleResponse:
        uri = f"{self.connection_string}/alertservice/rules/{req.dashboard_id}/{req.rule_id}"
        json_req = self.http_communicator._proto_to_json(req)
        json_resp = self.http_communicator.get_request(uri, json_req)
        return self.http_communicator._json_to_proto(
            json_resp, alert_service_pb2.GetAlertRuleResponse()
        )

    def modify_alert_rule(
        self,
        req: alert_service_pb2.ModifyAlertRuleRequest,
        request_context=None
    ) -> alert_service_pb2.ModifyAlertRuleResponse:
        uri = f"{self.connection_string}/alertservice/rules/{req.request.dashboard_id}/{req.request.dashboard_id}"
        json_req = self.http_communicator._proto_to_json(req)
        json_resp = self.http_communicator.put_request(uri, json_req)
        return self.http_communicator._json_to_proto(
            json_resp, alert_service_pb2.ModifyAlertRuleResponse()
        )

    def delete_alert_rule(
        self,
        req: alert_service_pb2.DeleteAlertRuleRequest,
        request_context=None
    ) -> alert_service_pb2.DeleteAlertRuleResponse:
        uri = f"{self.connection_string}/alertservice/rules/{req.dashboard_id}/{req.rule_id}"
        json_req = self.http_communicator._proto_to_json(req)
        json_resp = self.http_communicator.delete_request(uri, json_req)
        return self.http_communicator._json_to_proto(
            json_resp, alert_service_pb2.DeleteAlertRuleResponse()
        )

    def list_dashboard_alerts_with_status(
        self,
        req: alert_service_pb2.ListDashboardAlertsWithStatusRequest,
        request_context=None
    ) -> alert_service_pb2.ListDashboardAlertsWithStatusResponse:
        uri = f"{self.connection_string}/alertservice/rules/{req.dashboard_id}"
        json_req = self.http_communicator._proto_to_json(req)
        json_resp = self.http_communicator.get_request(uri, json_req)
        return self.http_communicator._json_to_proto(
            json_resp, alert_service_pb2.ListDashboardAlertsWithStatusResponse()
        )

    def get_alert_rule_history(
        self,
        req: alert_service_pb2.GetAlertRuleHistoryRequest,
        request_context=None
    ) -> alert_service_pb2.GetAlertRuleHistoryResponse:
        uri = f"{self.connection_string}/alertservice/rules/{req.dashboard_id}/history"
        json_req = self.http_communicator._proto_to_json(req)
        json_resp = self.http_communicator.get_request(uri, json_req)
        return self.http_communicator._json_to_proto(
            json_resp, alert_service_pb2.GetAlertRuleHistoryResponse()
        )
