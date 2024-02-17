from base64 import b64encode

from google.protobuf.message import Message

from truera.protobuf.public.data_service import \
    data_service_messages_pb2 as ds_messages_pb

RECORD_SEPARATOR = '␞'
GROUP_SEPARATOR = '␝'


def serialize_protobuf_base64(message):
    return b64encode(_serialize_protobuf(message).encode('utf-8'))


def _serialize_protobuf(message):
    '''
    Serialize arbitrary protobuf messages, in order of fields and by ignoring default values.
    This method guarantees that fields are serialized in-order by field number.
    If a field is set to a default value, it is not added to the serialization.
    Therefore, messages with the same fields set should be serialized in the same way,
    even if a new field is added to proto.
    This serialization method cannot handle reserved fields or field numbers which are skipped.

    This method must be functionally equivalent to serializeProtobuf
    in java/common/src/main/java/com/truera/common/util/ProtobufSerializationUtil.java
    '''

    sorted_fields = message.ListFields()
    buffer = []
    for field_descriptor, field_value in sorted_fields:
        if isinstance(field_value, Message):
            # ␞ stands for "record separator". It separates the field index from the field value
            buffer.append(
                str(field_descriptor.number) + RECORD_SEPARATOR + "(" +
                _serialize_protobuf(field_value) + ")"
            )
        else:
            if not field_descriptor.has_default_value:
                if field_descriptor.enum_type is not None:
                    buffer.append(
                        str(field_descriptor.number) + RECORD_SEPARATOR +
                        field_descriptor.enum_type.values[int(field_value)].name
                    )
                else:
                    buffer.append(
                        str(field_descriptor.number) + RECORD_SEPARATOR +
                        str(field_value)
                    )
    # ␝ stands for "group separator" and separates the field index:value pairs
    return GROUP_SEPARATOR.join(buffer)
