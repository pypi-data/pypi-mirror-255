import atexit
from enum import Enum
import logging
import platform
from queue import Queue
from threading import Thread
import time
import traceback
from typing import Dict, List, Optional, Union
import uuid

from google.protobuf.timestamp_pb2 import \
    Timestamp  # pylint: disable=no-name-in-module

from truera.client.public.auth_details import AuthDetails
from truera.client.public.communicator.user_analytics_communicator import \
    UserAnalyticsCommunicator
from truera.client.public.communicator.user_analytics_http_communicator import \
    HttpUserAnalyticsCommunicator
from truera.protobuf.useranalytics import \
    analytics_event_schema_pb2 as analytics_event_schema_pb
from truera.protobuf.useranalytics import useranalytics_pb2 as useranalytics_pb


class AnalyticsClientMode(Enum):
    SDK = 1
    CLI = 2
    BACKEND = 3

    def toProtoEventSource(self):
        if self.name == 'SDK':
            return useranalytics_pb.EventSourceProperties.EventSource.SDK
        elif self.name == 'CLI':
            return useranalytics_pb.EventSourceProperties.EventSource.CLI
        else:
            return useranalytics_pb.EventSourceProperties.EventSource.BACKEND


class UserAnalyticsServiceClient():

    def __init__(
        self,
        communicator: UserAnalyticsCommunicator,
        logger=None,
        analytics_client_mode: AnalyticsClientMode = AnalyticsClientMode.SDK,
    ) -> None:
        self.logger = logger if logger else logging.getLogger(__name__)
        self.communicator = communicator
        self.analytics_client_mode = analytics_client_mode
        self.event_queue: Queue = Queue()
        self.is_consumer_active = True
        self.consumer_thread = Thread(
            target=self.poll_queue_for_events, daemon=True
        )
        self.consumer_thread.start()
        atexit.register(self.close)

    @classmethod
    def create(
        cls,
        connection_string: str = None,
        logger=None,
        auth_details: AuthDetails = None,
        use_http: bool = False,
        *,
        verify_cert: Union[bool, str] = True,
        analytics_client_mode: AnalyticsClientMode = AnalyticsClientMode.SDK
    ):
        if use_http:
            communicator = HttpUserAnalyticsCommunicator(
                connection_string,
                auth_details,
                logger,
                verify_cert=verify_cert
            )
        else:
            from truera.client.private.communicator.user_analytics_grpc_communicator import \
                GrpcUserAnalyticsCommunicator
            communicator = GrpcUserAnalyticsCommunicator(
                connection_string, auth_details, logger
            )
        return UserAnalyticsServiceClient(
            communicator, logger, analytics_client_mode
        )

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        if self.logger is not None:
            self.logger.debug("draining event queue")
        self.event_queue.join()  # waits for all pending events to be processed
        self.is_consumer_active = False  # stops while loop in consumer
        self.communicator.close()

    def poll_queue_for_events(self):
        while self.is_consumer_active:
            (sendEventRequest, request_ctx) = self.event_queue.get()
            try:
                self.communicator.send_analytics_event(
                    sendEventRequest, request_ctx
                )
            except:
                if self.logger is not None:
                    # using logger.debug because warn will still be visible incase of cli, which may not be desriable ux.
                    self.logger.debug(
                        "failed in sending usage analytics data %s",
                        traceback.format_exc()
                    )
            # always mark task as done else queue will never get empty
            # a non draining queue can lead to OOM and also this interfers with the close operation which blocks on queue to be empty
            self.event_queue.task_done()

    def __generate_event_source_properties(
        self, experimentation_flags: Dict[str, str]
    ) -> useranalytics_pb.EventPlatformProperties:
        event_platform_properties = useranalytics_pb.EventPlatformProperties(
            os_name=platform.system(), os_version=platform.release()
        )
        event_source = self.analytics_client_mode.toProtoEventSource()
        return useranalytics_pb.EventSourceProperties(
            event_source=event_source,
            event_platform_properties=event_platform_properties,
            experimentation_flags=experimentation_flags
        )

    def __generate_entity_indentifiers(
        self,
        *,
        project_id: Optional[str] = None,
        data_collection_id: Optional[str] = None,
        data_source_id: Optional[str] = None,
        data_split_id: Optional[str] = None,
        model_id: Optional[str] = None,
        feedback_function_id: Optional[str] = None,
        report_id: Optional[str] = None,
        dashboard_id: Optional[str] = None,
    ) -> List[useranalytics_pb.TrueraEntityIdentifier]:
        entity_indentifiers = []
        if project_id is not None:
            entity_indentifiers.append(
                useranalytics_pb.TrueraEntityIdentifier(project_id=project_id)
            )
        if data_collection_id is not None:
            entity_indentifiers.append(
                useranalytics_pb.TrueraEntityIdentifier(
                    data_collection_id=data_collection_id
                )
            )
        if data_source_id is not None:
            entity_indentifiers.append(
                useranalytics_pb.TrueraEntityIdentifier(
                    data_source_id=data_source_id
                )
            )
        if data_split_id is not None:
            entity_indentifiers.append(
                useranalytics_pb.TrueraEntityIdentifier(
                    data_split_id=data_split_id
                )
            )
        if model_id is not None:
            entity_indentifiers.append(
                useranalytics_pb.TrueraEntityIdentifier(model_id=model_id)
            )
        if feedback_function_id is not None:
            entity_indentifiers.append(
                useranalytics_pb.TrueraEntityIdentifier(
                    feedback_function_id=feedback_function_id
                )
            )
        if report_id is not None:
            entity_indentifiers.append(
                useranalytics_pb.TrueraEntityIdentifier(report_id=report_id)
            )
        if dashboard_id is not None:
            entity_indentifiers.append(
                useranalytics_pb.TrueraEntityIdentifier(
                    dashboard_id=dashboard_id
                )
            )
        return entity_indentifiers

    def create_send_event_request(
        self,
        *,
        structured_event_properties: analytics_event_schema_pb.
        StructuredEventProperties = None,
        experimentation_flags: Dict[str, str] = {},
        project_id: Optional[str] = None,
        data_collection_id: Optional[str] = None,
        data_source_id: Optional[str] = None,
        data_split_id: Optional[str] = None,
        model_id: Optional[str] = None,
        feedback_function_id: Optional[str] = None,
        report_id: Optional[str] = None,
        dashboard_id: Optional[str] = None,
        is_success: Optional[bool] = False
    ):
        event_source_properties = self.__generate_event_source_properties(
            experimentation_flags
        )
        entity_identifiers = self.__generate_entity_indentifiers(
            project_id=project_id,
            data_collection_id=data_collection_id,
            data_source_id=data_source_id,
            data_split_id=data_split_id,
            model_id=model_id,
            feedback_function_id=feedback_function_id,
            report_id=report_id,
            dashboard_id=dashboard_id
        )
        sendEventRequest = useranalytics_pb.SendAnalyticsEventRequest(
            event_id=str(uuid.uuid4()),
            event_timestamp=Timestamp(seconds=int(time.time())),
            truera_entity_identifiers=entity_identifiers,
            event_source_properties=event_source_properties,
            structured_event_properties=structured_event_properties,
            is_success=is_success
        )
        return sendEventRequest

    def track_event(
        self,
        *,
        structured_event_properties: analytics_event_schema_pb.
        StructuredEventProperties = None,
        experimentation_flags: Dict[str, str] = {},
        project_id: Optional[str] = None,
        data_collection_id: Optional[str] = None,
        data_source_id: Optional[str] = None,
        data_split_id: Optional[str] = None,
        model_id: Optional[str] = None,
        feedback_function_id: Optional[str] = None,
        report_id: Optional[str] = None,
        dashboard_id: Optional[str] = None,
        is_success: Optional[bool] = False,
        request_context=None
    ):
        try:
            sendEventRequest = self.create_send_event_request(
                structured_event_properties=structured_event_properties,
                experimentation_flags=experimentation_flags,
                project_id=project_id,
                data_collection_id=data_collection_id,
                data_source_id=data_source_id,
                data_split_id=data_split_id,
                model_id=model_id,
                feedback_function_id=feedback_function_id,
                report_id=report_id,
                dashboard_id=dashboard_id,
                is_success=is_success
            )
            self.event_queue.put((sendEventRequest, request_context))
        except:
            if self.logger is not None:
                # using logger.debug because warning will still be visible incase of cli, which may not be desriable ux.
                self.logger.debug(
                    "failed in sending usage analytics data %s",
                    traceback.format_exc()
                )
