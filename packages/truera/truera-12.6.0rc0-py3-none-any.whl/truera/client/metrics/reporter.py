import datetime
import logging
from typing import Mapping, Optional

from truera.client.services.streaming_ingress_client import \
    StreamingIngressClient
from truera.client.truera_workspace import TrueraWorkspace


def _fix_up_time(
    time: Optional[datetime.datetime], logger
) -> datetime.datetime:
    if time is None:
        return datetime.datetime.now(datetime.timezone.utc)
    if time.tzinfo is None or time.tzinfo.utcoffset(time) is None:
        logger.warning(
            "Provided `time` does not include timezone info. Timezone info will be set to UTC."
        )
        return time.replace(tzinfo=datetime.timezone.utc)
    return time


class MetricReporter:

    def __init__(
        self,
        streaming_ingress_client: StreamingIngressClient,
        project_id: str,
        model_id: Optional[str] = None,
        logger: Optional[logging.Logger] = None
    ):
        """Class responsible for sending metrics. If `model_id` is not None, metrics will be associated with the given model."""
        self.streaming_ingress_client = streaming_ingress_client
        self.project_id = project_id
        self.model_id = model_id
        self.logger = logger or logging.getLogger(__name__)

    def sendMetrics(
        self,
        metrics: Mapping[str, float],
        *,
        time: Optional[datetime.datetime] = None
    ):
        """Send metric values at point in time.

        Args:
            metrics: Mapping of metric names to values.
            time: Datetime representing timestamp of the metric. Defaults to `datetime.utcnow()`.
        """
        self.streaming_ingress_client.ingest_metric(
            project_id=self.project_id,
            timestamp=str(_fix_up_time(time, self.logger).isoformat()),
            metrics=metrics,
            model_id=self.model_id
        )

    def send(
        self,
        metric: str,
        value: float,
        *,
        time: Optional[datetime.datetime] = None
    ):
        """Send a value for a metric at point in time.

        Args:
            metric: Name of the metric to send.
            value: Value of the metric to send.
            time: Datetime representing timestamp of the metric. Defaults to `datetime.utcnow()`.
        """
        metrics = {metric: value}
        self.sendMetrics(metrics, time=time)


class PointMetricReporter:

    def __init__(
        self,
        streaming_ingress_client: StreamingIngressClient,
        project_id: str,
        model_id: str,
        logger: Optional[logging.Logger] = None
    ):
        """Class responsible for sending point metrics."""
        self.streaming_ingress_client = streaming_ingress_client
        self.project_id = project_id
        self.model_id = model_id
        self.logger = logger or logging.getLogger(__name__)

    def sendMetrics(
        self,
        point_id: str,
        metrics: Mapping[str, float],
        *,
        time: Optional[datetime.datetime] = None
    ):
        """Send metric values at point in time.

        Args:
            point_id: The point which the metric is for.
            metrics: Mapping of metric names to values.
            time: Datetime representing timestamp of the metric. Defaults to `datetime.utcnow()`.
        """
        self.streaming_ingress_client.ingest_metric(
            project_id=self.project_id,
            timestamp=str(_fix_up_time(time, self.logger).isoformat()),
            metrics=metrics,
            model_id=self.model_id,
            point_id=point_id
        )

    def send(
        self,
        point_id: str,
        metric: str,
        value: float,
        *,
        time: Optional[datetime.datetime] = None
    ):
        """Send a value for a metric at point in time.

        Args:
            point_id: The point which the metric is for.
            metric: Name of the metric to send.
            value: Value of the metric to send.
            time: Datetime representing timestamp of the metric. Defaults to `datetime.utcnow()`.
        """
        metrics = {metric: value}
        self.sendMetrics(point_id, metrics, time=time)


def getGeneralMetricReporter(tru: TrueraWorkspace) -> MetricReporter:
    tru._ensure_project()
    return MetricReporter(
        streaming_ingress_client=tru.remote_tru.streaming_ingress_client,
        project_id=tru.current_tru.project.id,
        logger=tru.logger
    )


def getModelMetricReporter(tru: TrueraWorkspace) -> MetricReporter:
    tru._ensure_project()
    tru._ensure_model()
    return MetricReporter(
        streaming_ingress_client=tru.remote_tru.streaming_ingress_client,
        project_id=tru.current_tru.project.id,
        model_id=tru.current_tru.model.model_id,
        logger=tru.logger
    )


def getPointMetricReporter(tru: TrueraWorkspace) -> PointMetricReporter:
    tru._ensure_project()
    tru._ensure_model()
    return PointMetricReporter(
        streaming_ingress_client=tru.remote_tru.streaming_ingress_client,
        project_id=tru.current_tru.project.id,
        model_id=tru.current_tru.model.model_id,
        logger=tru.logger
    )
