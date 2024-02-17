from dataclasses import dataclass
import logging
from typing import List

from google.protobuf.timestamp_pb2 import \
    Timestamp  # pylint: disable=no-name-in-module

from truera.client.private.communicator.metering_service_communicator import \
    MeteringServiceCommunicator
from truera.client.private.communicator.metering_service_grpc_communicator import \
    MeteringServiceGrpcCommunicator
from truera.client.public.auth_details import AuthDetails
from truera.protobuf.metering import metering_pb2 as metering_pb
from truera.protobuf.public.util import time_range_pb2 as time_range_pb


class MeteringServiceClient():

    def __init__(
        self, communicator: MeteringServiceCommunicator, logger=None
    ) -> None:
        self.logger = logger if logger else logging.getLogger(__name__)
        self.communicator = communicator

    @classmethod
    def create(
        cls,
        connection_string: str = None,
        logger=None,
        auth_details: AuthDetails = None
    ):
        communicator = MeteringServiceGrpcCommunicator(
            connection_string, auth_details, logger
        )
        return MeteringServiceClient(communicator, logger)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        self.communicator.close()

    def get_monthly_metering_stats(
        self,
        tenant_id: str,
        month: int,
        year: int,
        report_granularity=metering_pb.ReportGranularity.DAY,
        request_context=None
    ):
        monthly_window = metering_pb.MonthlyMeteringWindow(
            year=year, month=month, time_zone="UTC"
        )
        metering_window = metering_pb.MeteringWindow(
            monthly_metering_window=monthly_window
        )
        req = metering_pb.MeteringIngestionStatsRequest(
            tenant_id=tenant_id,
            metering_window=metering_window,
            report_granularity=report_granularity
        )
        return self.communicator.get_metering_ingestion_stats(
            req, request_context=request_context
        )

    def get_continous_metering_stats(
        self,
        tenant_id: str,
        begin: int,
        end: int,
        report_granularity=metering_pb.ReportGranularity.DAY,
        request_context=None
    ):
        timestamp_window = time_range_pb.TimeRange(
            begin=Timestamp(seconds=begin), end=Timestamp(seconds=end)
        )
        metering_window = metering_pb.MeteringWindow(
            timestamp_metering_window=timestamp_window
        )
        req = metering_pb.MeteringIngestionStatsRequest(
            tenant_id=tenant_id,
            metering_window=metering_window,
            report_granularity=report_granularity
        )
        return self.communicator.get_metering_ingestion_stats(
            req, request_context=request_context
        )