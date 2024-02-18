from proto import chat_pb2 as _chat_pb2
from proto import task_types_base_pb2 as _task_types_base_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import (
    ClassVar as _ClassVar,
    Iterable as _Iterable,
    Mapping as _Mapping,
    Optional as _Optional,
    Union as _Union,
)

DESCRIPTOR: _descriptor.FileDescriptor

class RunAgentWorkflowInput(_message.Message):
    __slots__ = (
        "name",
        "instructions",
        "chat_id",
        "function_keys",
        "is_done_function_key",
    )
    NAME_FIELD_NUMBER: _ClassVar[int]
    INSTRUCTIONS_FIELD_NUMBER: _ClassVar[int]
    CHAT_ID_FIELD_NUMBER: _ClassVar[int]
    FUNCTION_KEYS_FIELD_NUMBER: _ClassVar[int]
    IS_DONE_FUNCTION_KEY_FIELD_NUMBER: _ClassVar[int]
    name: str
    instructions: str
    chat_id: str
    function_keys: _containers.RepeatedScalarFieldContainer[str]
    is_done_function_key: str
    def __init__(
        self,
        name: _Optional[str] = ...,
        instructions: _Optional[str] = ...,
        chat_id: _Optional[str] = ...,
        function_keys: _Optional[_Iterable[str]] = ...,
        is_done_function_key: _Optional[str] = ...,
    ) -> None: ...

class RunAgentWorkflowOutput(_message.Message):
    __slots__ = ("content",)
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    content: str
    def __init__(self, content: _Optional[str] = ...) -> None: ...

class AddUserMessageInput(_message.Message):
    __slots__ = ("chat_id", "content")
    CHAT_ID_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    chat_id: str
    content: str
    def __init__(
        self, chat_id: _Optional[str] = ..., content: _Optional[str] = ...
    ) -> None: ...

class AddUserMessageOutput(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetAgentResponseInput(_message.Message):
    __slots__ = ("chat_id", "function_keys", "function_call")
    CHAT_ID_FIELD_NUMBER: _ClassVar[int]
    FUNCTION_KEYS_FIELD_NUMBER: _ClassVar[int]
    FUNCTION_CALL_FIELD_NUMBER: _ClassVar[int]
    chat_id: str
    function_keys: _containers.RepeatedScalarFieldContainer[str]
    function_call: str
    def __init__(
        self,
        chat_id: _Optional[str] = ...,
        function_keys: _Optional[_Iterable[str]] = ...,
        function_call: _Optional[str] = ...,
    ) -> None: ...

class GetAgentResponseOutput(_message.Message):
    __slots__ = ("message",)
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: _chat_pb2.Message
    def __init__(
        self, message: _Optional[_Union[_chat_pb2.Message, _Mapping]] = ...
    ) -> None: ...

class CreateChatInput(_message.Message):
    __slots__ = ("name", "system_message")
    NAME_FIELD_NUMBER: _ClassVar[int]
    SYSTEM_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    name: str
    system_message: str
    def __init__(
        self, name: _Optional[str] = ..., system_message: _Optional[str] = ...
    ) -> None: ...

class CreateChatOutput(_message.Message):
    __slots__ = ("chat_id",)
    CHAT_ID_FIELD_NUMBER: _ClassVar[int]
    chat_id: str
    def __init__(self, chat_id: _Optional[str] = ...) -> None: ...

class CallFunctionInput(_message.Message):
    __slots__ = ("chat_id", "function_keys", "function_call")
    CHAT_ID_FIELD_NUMBER: _ClassVar[int]
    FUNCTION_KEYS_FIELD_NUMBER: _ClassVar[int]
    FUNCTION_CALL_FIELD_NUMBER: _ClassVar[int]
    chat_id: str
    function_keys: _containers.RepeatedScalarFieldContainer[str]
    function_call: _chat_pb2.FunctionCall
    def __init__(
        self,
        chat_id: _Optional[str] = ...,
        function_keys: _Optional[_Iterable[str]] = ...,
        function_call: _Optional[_Union[_chat_pb2.FunctionCall, _Mapping]] = ...,
    ) -> None: ...

class CallFunctionOutput(_message.Message):
    __slots__ = ("name", "result")
    NAME_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    name: str
    result: str
    def __init__(
        self, name: _Optional[str] = ..., result: _Optional[str] = ...
    ) -> None: ...

class GetStructuredResponseInput(_message.Message):
    __slots__ = ("chat_id", "structure_json")
    CHAT_ID_FIELD_NUMBER: _ClassVar[int]
    STRUCTURE_JSON_FIELD_NUMBER: _ClassVar[int]
    chat_id: str
    structure_json: str
    def __init__(
        self, chat_id: _Optional[str] = ..., structure_json: _Optional[str] = ...
    ) -> None: ...

class GetStructuredResponseOutput(_message.Message):
    __slots__ = ("structure_instance_json",)
    STRUCTURE_INSTANCE_JSON_FIELD_NUMBER: _ClassVar[int]
    structure_instance_json: str
    def __init__(self, structure_instance_json: _Optional[str] = ...) -> None: ...
