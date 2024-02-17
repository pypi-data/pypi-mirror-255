from temporalio.converter import CompositePayloadConverter
from temporalio.converter import JSONPlainPayloadConverter


class BaselineModelPayloadConverter(CompositePayloadConverter):

    def __init__(self) -> None:
        super().__init__(JSONPlainPayloadConverter(),)