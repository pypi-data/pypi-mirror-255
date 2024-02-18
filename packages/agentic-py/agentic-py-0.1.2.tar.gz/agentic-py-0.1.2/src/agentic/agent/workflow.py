from typing import Any, List, Callable

from agentic.proto import chat_pb2
from agentic.core.serialization import base
from agentic.core import action, workflow
from agentic.llm import (
    Chat,
    get_chat_completion,
)
from agentic.llm.agentic_openai.util import call_function_from_openai_structure
from agentic.llm.agentic_openai import call_function_and_update_messages

from agentic.core.serialization.base import ensure_in_proto_type_registry
from agentic.core.serialization.task import get_func_from_registry

from agentic.util import shorten_text

from agentic.proto import task_types_agent_pb2


@workflow(
    serialization=base.PROTOBUF,
    description=lambda input: shorten_text(input.instructions),
)
async def instruct_agent(
    input: task_types_agent_pb2.RunAgentWorkflowInput,
) -> task_types_agent_pb2.RunAgentWorkflowOutput:
    chat = Chat(chat_id=input.chat_id)
    instructions = input.instructions
    is_done = get_func_from_registry(input.is_done_function_key)
    assert is_done is not None
    message = None
    await give_instructions(
        task_types_agent_pb2.AddUserMessageInput(
            chat_id=chat.chat_id, content=instructions
        )
    )
    while not message or is_done(message) is False:
        response = await get_agent_response(
            task_types_agent_pb2.GetAgentResponseInput(
                chat_id=chat.chat_id,
                function_keys=input.function_keys,
                function_call="auto",
            )
        )
        message = response.message
        function_call = message.function_call
        if function_call and function_call.name:
            await call_function(
                task_types_agent_pb2.CallFunctionInput(
                    chat_id=chat.chat_id,
                    function_keys=input.function_keys,
                    function_call=function_call,
                )
            )
    assert message
    return task_types_agent_pb2.RunAgentWorkflowOutput(content=message.content)


ensure_in_proto_type_registry(task_types_agent_pb2.RunAgentWorkflowInput)
ensure_in_proto_type_registry(task_types_agent_pb2.RunAgentWorkflowOutput)


@action(
    serialization=base.PROTOBUF,
)
async def give_instructions(
    input: task_types_agent_pb2.AddUserMessageInput,
) -> task_types_agent_pb2.AddUserMessageOutput:
    chat = Chat(chat_id=input.chat_id)
    message = input.content
    await chat.add_message(chat_pb2.Message(role="user", content=message))
    return task_types_agent_pb2.AddUserMessageOutput()


ensure_in_proto_type_registry(task_types_agent_pb2.AddUserMessageInput)
ensure_in_proto_type_registry(task_types_agent_pb2.AddUserMessageOutput)


@action(
    serialization=base.PROTOBUF,
)
async def get_agent_response(
    input: task_types_agent_pb2.GetAgentResponseInput,
) -> task_types_agent_pb2.GetAgentResponseOutput:
    """Takes a prompt and returns a single completion result."""
    chat = Chat(chat_id=input.chat_id)
    functions = [get_func_from_registry(key) for key in input.function_keys]
    function_call = input.function_call
    message = await get_chat_completion(
        chat, functions=functions, function_call=function_call
    )
    return task_types_agent_pb2.GetAgentResponseOutput(message=message)


ensure_in_proto_type_registry(task_types_agent_pb2.GetAgentResponseInput)
ensure_in_proto_type_registry(task_types_agent_pb2.GetAgentResponseOutput)


@workflow(
    serialization=base.PROTOBUF,
    name=lambda input: "Call function for agent: " + input.function_call.name,
)
async def call_function(
    input: task_types_agent_pb2.CallFunctionInput,
) -> task_types_agent_pb2.CallFunctionOutput:
    chat = Chat(chat_id=input.chat_id)
    function_call = input.function_call
    assert function_call.name
    functions = [get_func_from_registry(key) for key in input.function_keys]
    res = await call_function_and_update_messages(
        chat,
        func_call=function_call,
        functions=functions,
        handle_func_call=call_function_from_openai_structure,
        # NOTE: This will mean that exceptions are treated as just
        # another function response. This allows the LLM
        # to handle the exception and change approach accordingly.
        store_exception_in_messages=True,
    )
    # Response only returned so it is viewable in the UI.
    return task_types_agent_pb2.CallFunctionOutput(
        name=res.name, result=str(res.result or "")
    )


ensure_in_proto_type_registry(task_types_agent_pb2.CallFunctionInput)
ensure_in_proto_type_registry(task_types_agent_pb2.CallFunctionOutput)
