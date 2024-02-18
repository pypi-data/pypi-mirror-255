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

class CreateChatRequest(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class CreateChatResponse(_message.Message):
    __slots__ = ("chat",)
    CHAT_FIELD_NUMBER: _ClassVar[int]
    chat: Chat
    def __init__(self, chat: _Optional[_Union[Chat, _Mapping]] = ...) -> None: ...

class AddMessageRequest(_message.Message):
    __slots__ = ("chat_id", "message")
    CHAT_ID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    chat_id: str
    message: Message
    def __init__(
        self,
        chat_id: _Optional[str] = ...,
        message: _Optional[_Union[Message, _Mapping]] = ...,
    ) -> None: ...

class AddMessageResponse(_message.Message):
    __slots__ = ("message",)
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: Message
    def __init__(self, message: _Optional[_Union[Message, _Mapping]] = ...) -> None: ...

class UpdateMessageRequest(_message.Message):
    __slots__ = ("message",)
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: Message
    def __init__(self, message: _Optional[_Union[Message, _Mapping]] = ...) -> None: ...

class UpdateMessageResponse(_message.Message):
    __slots__ = ("message",)
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: Message
    def __init__(self, message: _Optional[_Union[Message, _Mapping]] = ...) -> None: ...

class GetChatRequest(_message.Message):
    __slots__ = ("chat_id",)
    CHAT_ID_FIELD_NUMBER: _ClassVar[int]
    chat_id: str
    def __init__(self, chat_id: _Optional[str] = ...) -> None: ...

class WatchChatRequest(_message.Message):
    __slots__ = ("chat_id",)
    CHAT_ID_FIELD_NUMBER: _ClassVar[int]
    chat_id: str
    def __init__(self, chat_id: _Optional[str] = ...) -> None: ...

class GetChatResponse(_message.Message):
    __slots__ = ("chat", "messages")
    CHAT_FIELD_NUMBER: _ClassVar[int]
    MESSAGES_FIELD_NUMBER: _ClassVar[int]
    chat: Chat
    messages: _containers.RepeatedCompositeFieldContainer[Message]
    def __init__(
        self,
        chat: _Optional[_Union[Chat, _Mapping]] = ...,
        messages: _Optional[_Iterable[_Union[Message, _Mapping]]] = ...,
    ) -> None: ...

class Chat(_message.Message):
    __slots__ = ("id", "name")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    def __init__(
        self, id: _Optional[str] = ..., name: _Optional[str] = ...
    ) -> None: ...

class Message(_message.Message):
    __slots__ = ("id", "role", "content", "function_call", "name", "finish_reason")
    ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    FUNCTION_CALL_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    FINISH_REASON_FIELD_NUMBER: _ClassVar[int]
    id: str
    role: str
    content: str
    function_call: FunctionCall
    name: str
    finish_reason: str
    def __init__(
        self,
        id: _Optional[str] = ...,
        role: _Optional[str] = ...,
        content: _Optional[str] = ...,
        function_call: _Optional[_Union[FunctionCall, _Mapping]] = ...,
        name: _Optional[str] = ...,
        finish_reason: _Optional[str] = ...,
    ) -> None: ...

class Function(_message.Message):
    __slots__ = ("name", "parameters", "description")
    NAME_FIELD_NUMBER: _ClassVar[int]
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    name: str
    parameters: str
    description: str
    def __init__(
        self,
        name: _Optional[str] = ...,
        parameters: _Optional[str] = ...,
        description: _Optional[str] = ...,
    ) -> None: ...

class FunctionCall(_message.Message):
    __slots__ = ("name", "arguments")
    NAME_FIELD_NUMBER: _ClassVar[int]
    ARGUMENTS_FIELD_NUMBER: _ClassVar[int]
    name: str
    arguments: str
    def __init__(
        self, name: _Optional[str] = ..., arguments: _Optional[str] = ...
    ) -> None: ...
