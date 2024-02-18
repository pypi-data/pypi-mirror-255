from typing import Tuple, Any

import jsonpickle

import enum

from agentic.proto import coordinator_pb2, task_types_base_pb2

from google.protobuf.any_pb2 import Any as PbAny


class SerializationType(enum.Enum):
    json = 1
    protobuf = 2


JSON = SerializationType.json
PROTOBUF = SerializationType.protobuf


_type_registry = {
    task_types_base_pb2.JSONWrapper.DESCRIPTOR.full_name: task_types_base_pb2.JSONWrapper,
}


def serialize_with_json_pickle(data: Any) -> str:
    json = jsonpickle.encode(data)
    return json


def deserialize_with_json_pickle(json: str) -> Any:
    data = jsonpickle.decode(json)
    return data


def serialize_any_as_json_wrapper(data: Any) -> PbAny:
    # TODO - Migrate away from jsonpickle. Too much magic...
    # Maybe support regular pickle instead?
    json = serialize_with_json_pickle(data)
    inner_msg = task_types_base_pb2.JSONWrapper(json=json)
    any_message = PbAny()
    any_message.Pack(inner_msg)
    return any_message


def ensure_in_proto_type_registry(msg_type):
    if msg_type.DESCRIPTOR.full_name not in _type_registry:
        _type_registry[msg_type.DESCRIPTOR.full_name] = msg_type
    elif _type_registry[msg_type.DESCRIPTOR.full_name] != msg_type:
        raise ValueError(
            f"Type {msg_type.DESCRIPTOR.full_name} already registered with different message type"
        )


def deserialize_any(any_message: PbAny) -> Tuple[object, SerializationType]:
    if any_message.Is(task_types_base_pb2.JSONWrapper.DESCRIPTOR):
        return _json_deserialization(any_message)
    return _protobuf_deserialization(any_message)


def _json_deserialization(any_message: PbAny):
    assert any_message.Is(task_types_base_pb2.JSONWrapper.DESCRIPTOR)
    js_message = task_types_base_pb2.JSONWrapper()
    any_message.Unpack(js_message)
    obj = deserialize_with_json_pickle(js_message.json)
    return obj, SerializationType.json


def _protobuf_deserialization(any_message: PbAny):
    parts = any_message.type_url.split("/")
    if len(parts) != 2:
        raise ValueError(
            f"Invalid type_url {any_message.type_url} - must be of form 'type.googleapis.com/full.type.name'"
        )
    name = parts[-1]
    matching_type = _type_registry.get(name)
    if not matching_type:
        raise ValueError(f"Type {any_message.type_url} not found in registry")
    msg_obj = matching_type()
    any_message.Unpack(msg_obj)
    return msg_obj, SerializationType.protobuf
