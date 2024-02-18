from typing import Any, List, Callable, Optional, Dict, Type, TypeVar
import json
from string import Template

from agentic.core.typing import IsDataclass
from agentic.core.serialization import base
from agentic.llm import (
    Chat,
    structure_from_chat,
)
from agentic.llm.agentic_openai.util import function_to_openai_structure

from agentic.proto import task_types_agent_pb2
from agentic.proto import chat_pb2

from agentic.core.serialization.task import add_func_to_registry
from agentic.core.serialization.base import (
    serialize_with_json_pickle,
    deserialize_with_json_pickle,
    ensure_in_proto_type_registry,
)
from agentic.core.decorators import action

from .workflow import instruct_agent


DataclassT = TypeVar("DataclassT", bound=IsDataclass)


class Agent:
    DEFAULT_SYSTEM_MESSAGE = ""
    DEFAULT_NAME = "Agent"

    def __init__(
        self,
        name: Optional[str] = None,
        functions: List[Callable] = [],
    ):
        self._name = name or self.DEFAULT_NAME
        self._functions = functions
        self._chats: Dict[Optional[Agent], Chat] = {}

    @property
    def name(self):
        return self._name

    async def create_chat(self) -> str:
        out = await create_agent_chat(
            task_types_agent_pb2.CreateChatInput(
                name=f"Conversation with {self.name}",
                system_message=self._system_message,
            )
        )
        return out.chat_id

    async def handle_instructions(self, chat_id: str, instructions: str) -> str:
        chat = Chat(chat_id=chat_id)
        function_keys = self._get_function_keys()
        _is_done = self.get_is_done_callback()
        is_done_key = add_func_to_registry(_is_done)
        res = await instruct_agent(
            input=task_types_agent_pb2.RunAgentWorkflowInput(
                name=self._name,
                chat_id=chat.chat_id,
                instructions=instructions,
                function_keys=function_keys,
                is_done_function_key=is_done_key,
            ),
        )
        return res.content

    async def get_structured_response(
        self,
        chat_id: str,
        structure: Type[DataclassT],
    ) -> DataclassT:
        res = await get_structured_response_from_agent(
            input=task_types_agent_pb2.GetStructuredResponseInput(
                chat_id=chat_id,
                structure_json=serialize_with_json_pickle(structure),
            )
        )
        obj = deserialize_with_json_pickle(res.structure_instance_json)
        return obj

    def get_is_done_callback(self) -> Callable[[str], bool]:
        """Returns a function that takes a message and returns a boolean indicating if the message is a termination message.
        Actual function cannot be a method on the class due to shortcomings with workflow arg serialization.
        """
        raise NotImplementedError("Must be implemented by subclass.")

    def _get_function_keys(self):
        keys = []
        for func in self._functions:
            keys.append(add_func_to_registry(func))
        return keys

    def _functions_to_pb(self):
        as_pb = []
        for func in self._functions:
            serialized_function = function_to_openai_structure(func)
            as_pb.append(
                chat_pb2.Function(
                    name=serialized_function["name"],
                    parameters=json.dumps(serialized_function["parameters"]),
                    description=serialized_function.get("description"),
                )
            )
        return as_pb

    @property
    def _system_message(self):
        sys_message_templ = Template(self.DEFAULT_SYSTEM_MESSAGE)
        sys_message = sys_message_templ.substitute(name=self.name)
        assert sys_message
        return sys_message


@action(
    serialization=base.PROTOBUF,
)
async def create_agent_chat(
    input: task_types_agent_pb2.CreateChatInput,
) -> task_types_agent_pb2.CreateChatOutput:
    chat = await Chat.create(name=f"{input.name}")
    await chat.add_message(
        chat_pb2.Message(role="system", content=input.system_message)
    )
    return task_types_agent_pb2.CreateChatOutput(chat_id=chat.chat_id)


ensure_in_proto_type_registry(task_types_agent_pb2.CreateChatInput)
ensure_in_proto_type_registry(task_types_agent_pb2.CreateChatOutput)


@action(
    serialization=base.PROTOBUF,
)
async def get_structured_response_from_agent(
    input: task_types_agent_pb2.GetStructuredResponseInput,
) -> task_types_agent_pb2.GetStructuredResponseOutput:
    chat = Chat(chat_id=input.chat_id)
    structure = deserialize_with_json_pickle(input.structure_json)
    res = await structure_from_chat(chat=chat, structure=structure)
    as_json = serialize_with_json_pickle(res)
    return task_types_agent_pb2.GetStructuredResponseOutput(
        structure_instance_json=as_json
    )


ensure_in_proto_type_registry(task_types_agent_pb2.GetStructuredResponseInput)
ensure_in_proto_type_registry(task_types_agent_pb2.GetStructuredResponseOutput)
