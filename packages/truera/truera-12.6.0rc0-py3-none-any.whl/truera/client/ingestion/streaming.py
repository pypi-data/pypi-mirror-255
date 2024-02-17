from enum import Enum
from typing import Any, Callable, Mapping, Optional, Sequence, TYPE_CHECKING

from pydantic import BaseModel

from truera.protobuf.public.streaming import \
    streaming_ingress_service_pb2 as si_pb

if TYPE_CHECKING:
    from truera.client.remote_truera_workspace import RemoteTrueraWorkspace


class StreamingValidationError(BaseModel):
    message: str
    type: str

    column: Optional[str] = None
    event_indexes: Optional[Sequence[int]] = None

    def __str__(self) -> str:
        s = self.message
        if self.event_indexes:
            s += f" Error applies to events with index {self.event_indexes}."
        return s


class StreamingStatus(str, Enum):
    FAILURE = "FAILURE"
    SUCCESS = "SUCCESS"


class StreamingResponse(BaseModel):
    errors: Sequence[StreamingValidationError]
    status: StreamingStatus
    events: Sequence[Mapping[str, Any]]


class StreamingValidationErrorGroup(Exception):
    """Exception raised when there is one or more validation exceptions encountered while ingesting events."""

    #TODO: Implement with ExceptionGroup for python>=3.11

    def __init__(self, errors: Sequence[StreamingValidationError]):
        self.errors = errors
        message = f"Encountered {len(self.errors)} validation error(s) while ingesting events. Please try again after fixing the following:"
        for i, error in enumerate(self.errors):
            message += f"\n {i+1}. {str(error)}"
        super().__init__(message)


def ingest_events(
    remote: 'RemoteTrueraWorkspace', project_id: str, model_id: str,
    events: Sequence[Mapping[str, Any]], raise_errors: bool
) -> StreamingResponse:
    errors = []
    try:
        res = remote.streaming_ingress_client.ingest_events(
            project_id=project_id, model_id=model_id, events=events
        )
        errors = [
            StreamingValidationError(
                message=err.message,
                column=err.column_name,
                type=si_pb.ValidationErrorType.Name(err.type),
                event_indexes=[i for i in err.event_indexes]
            ) for err in res.validation_errors
        ]
    except Exception as e:
        errors.append(
            StreamingValidationError(
                message=str(e), type=str(e.__class__.__name__)
            )
        )
    finally:
        if raise_errors and errors:
            raise StreamingValidationErrorGroup(errors)
        return StreamingResponse(
            errors=errors,
            status=StreamingStatus.FAILURE
            if errors else StreamingStatus.SUCCESS,
            events=events
        )
