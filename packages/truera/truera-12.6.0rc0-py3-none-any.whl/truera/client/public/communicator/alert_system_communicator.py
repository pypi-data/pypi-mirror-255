from abc import ABC
from abc import abstractmethod

from truera.protobuf.monitoring import alert_service_pb2


class AlertSystemCommunicator(ABC):

    @abstractmethod
    def enable_alerting(
        self,
        req: alert_service_pb2.EnableAlertingRequest,
        request_context=None
    ) -> alert_service_pb2.EnableAlertingResponse:
        pass

    @abstractmethod
    def disable_alerting(
        self,
        req: alert_service_pb2.DisableAlertingRequest,
        request_context=None
    ) -> alert_service_pb2.DisableAlertingResponse:
        pass

    @abstractmethod
    def add_alert_rule(
        self,
        req: alert_service_pb2.AddAlertRuleRequest,
        request_context=None
    ) -> alert_service_pb2.AddAlertRuleResponse:
        pass

    @abstractmethod
    def get_alert_rule(
        self,
        req: alert_service_pb2.GetAlertRuleRequest,
        request_context=None
    ) -> alert_service_pb2.GetAlertRuleResponse:
        pass

    @abstractmethod
    def modify_alert_rule(
        self,
        req: alert_service_pb2.ModifyAlertRuleRequest,
        request_context=None
    ) -> alert_service_pb2.ModifyAlertRuleResponse:
        pass

    @abstractmethod
    def delete_alert_rule(
        self,
        req: alert_service_pb2.DeleteAlertRuleRequest,
        request_context=None
    ) -> alert_service_pb2.DeleteAlertRuleResponse:
        pass

    @abstractmethod
    def list_dashboard_alerts_with_status(
        self,
        req: alert_service_pb2.ListDashboardAlertsWithStatusRequest,
        request_context=None
    ) -> alert_service_pb2.ListDashboardAlertsWithStatusResponse:
        pass

    @abstractmethod
    def get_alert_rule_history(
        self,
        req: alert_service_pb2.GetAlertRuleRequest,
        request_context=None
    ) -> alert_service_pb2.GetAlertRuleResponse:
        pass
