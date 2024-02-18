from typing import List, Sequence, Dict, Any, Optional, Tuple, Type, Callable, Union

import json

from dataclasses import dataclass

import backoff

import openai

from agentic.proto import chat_pb2
from agentic.core.config import require_config
from agentic.core import action
from agentic.core.typing import IsDataclass
from agentic.core.logging import logger

from .config import OPENAI_API_KEY

from .util import (
    function_to_openai_structure,
    dataclass_to_openai_structure,
    call_function_from_openai_structure,
    create_instance_from_openai_structure,
    call_function,
)

from ..chat import Chat


@dataclass
class FuncResult:
    name: str
    result: Any


@action()
async def get_chat_completion(
    chat: Chat,
    model: str = "gpt-4-turbo-preview",
    functions: Optional[
        Sequence[Union[Callable, Dict]]
    ] = None,  # Functions may already be serialized
    function_call: str = "auto",  # auto is default, but we'll be explicit
    temperature: float = 0.0,
) -> chat_pb2.Message:
    api_key = require_config(OPENAI_API_KEY)
    func_args = {}
    if functions:
        functions = _serialize_functions(functions)
        func_args = {
            "functions": functions,
            "function_call": function_call,
        }
    retrieved_messages = await _get_messages_in_oai_format(chat)
    message_id = await chat.add_message(chat_pb2.Message(role="assistant", content=""))
    (
        content_res,
        func_name,
        func_args,
        finish_reason,
    ) = await _stream_completion_with_retry(
        model, retrieved_messages, temperature, api_key, chat, message_id, **func_args
    )
    func_res = None
    if func_name:
        func_res = chat_pb2.FunctionCall(name=func_name, arguments=func_args)
    logger.debug("Returning response from OpenAI API")
    msg = chat_pb2.Message(
        id=message_id,
        content=content_res,
        function_call=func_res,
        finish_reason=finish_reason,
        role="assistant",
    )
    await chat.update_message(msg)
    return msg


@backoff.on_exception(backoff.expo, Exception, max_tries=3)
async def _stream_completion_with_retry(
    model, retrieved_messages, temperature, api_key, chat, message_id, **func_args
):
    """TODO — Agentic workflow runtime should have built in retry
    support"""
    response = _start_completion_with_retry(
        model=model,
        messages=retrieved_messages,
        temperature=temperature,
        api_key=api_key,
        stream=True,
        **func_args,
    )
    content_res = ""
    func_name = ""
    func_args = ""
    finish_reason = ""
    logger.debug("Stream response from OpenAI API")
    for evt in response:
        (
            content_res,
            func_name,
            func_args,
            finish_reason,
        ) = await _handle_partial_chat_response(
            evt, chat, message_id, content_res, func_name, func_args
        )
    return content_res, func_name, func_args, finish_reason


@backoff.on_exception(
    backoff.expo,
    (
        openai.error.RateLimitError,  # type: ignore
        openai.error.APIError,  # type: ignore
        ConnectionError,
    ),
    max_tries=3,
)
def _start_completion_with_retry(*args: Any, **kwargs: Any):
    logger.debug("Calling OpenAI API")
    original_base = openai.api_base
    original_key = openai.api_key
    try:
        res = openai.ChatCompletion.create(*args, request_timeout=60, **kwargs)
    finally:
        openai.api_base = original_base
        openai.api_key = original_key
    logger.debug("Received response from OpenAI API")
    return res


def _serialize_functions(functions: Sequence[Union[Callable, Dict]]):
    ret = []
    for f in functions:
        if isinstance(f, dict):
            ret.append(f)
        else:
            ret.append(function_to_openai_structure(f))
    return ret


async def _get_messages_in_oai_format(chat: Chat):
    msgs = await chat.get_messages()
    dict_msgs = []
    for msg in msgs:
        dict_msg: Dict[str, Any] = {
            "role": msg.role,
            "content": msg.content,
        }
        if msg.function_call and msg.function_call.name:
            dict_msg["function_call"] = {
                "name": msg.function_call.name,
                "arguments": msg.function_call.arguments,
            }
        if msg.name:
            dict_msg["name"] = msg.name
        dict_msgs.append(dict_msg)
    return dict_msgs


async def _handle_partial_chat_response(
    evt, chat: Chat, message_id: str, content_res: str, func_name: str, func_args: str
):
    choices = evt.get("choices", [{}])  # type: ignore
    # Will only be one if n=1 is always used for initial chat completion creation
    choice = choices[0]
    finish_reason = choice.get("finish_reason")
    delta = choice.get("delta", {})
    content = delta.get("content") or ""
    content_res += content
    func_text = ""
    func = delta.get("function_call")
    if func:
        name = func.get("name") or ""
        func_name += name
        args = func.get("arguments") or ""
        func_args += args
        func_text += name + args
    updated_func_call = None
    if func_name:
        updated_func_call = chat_pb2.FunctionCall(
            name=func_name,
            arguments=func_args,
        )
    updated_msg = chat_pb2.Message(
        id=message_id,
        content=content_res,
        function_call=updated_func_call,
        role="assistant",
    )
    await chat.update_message(updated_msg)
    return content_res, func_name, func_args, finish_reason


async def get_and_handle_chat_completion(
    chat: Chat,
    functions: List[Union[Callable, Dict]] = [],
    on_request_function_call: Optional[Callable] = None,
    create_func_llm_response: Optional[Callable] = None,
    **kwargs: Any,
) -> Optional[FuncResult]:
    if functions:
        assert (
            on_request_function_call
        ), "You must define an on_request_function_call callback if functions are passed in."
    chat_res = await get_chat_completion(chat=chat, functions=functions, **kwargs)
    func_call = chat_res.function_call
    call_data = None
    if func_call and func_call.name and functions and on_request_function_call:
        call_data = await call_function_and_update_messages(
            chat,
            func_call,
            functions,
            on_request_function_call,
            create_func_llm_response,
        )
    return call_data


async def call_function_and_update_messages(
    chat: Chat,
    func_call: chat_pb2.FunctionCall,
    functions: List[Union[Callable, Dict]],
    handle_func_call: Callable,
    create_func_llm_response: Optional[Callable] = None,
    store_exception_in_messages: bool = False,
):
    assert func_call.name, "Function call has no name"
    func_resp = None
    call_data = None
    try:
        func_resp = await call_function(handle_func_call, functions, func_call)
    except Exception as e:
        if store_exception_in_messages:
            logger.info("Exception while calling function for LLM")
            logger.info(e)
            func_resp = e
        else:
            raise e
    # Optionally override the response to the LLM
    func_call_res = (
        create_func_llm_response(func_resp)
        if create_func_llm_response
        else str(func_resp) or ""
    )
    # Add result of calling function to history so OpenAI can see what happened
    await chat.add_message(
        chat_pb2.Message(
            role="function",
            name=func_call.name,
            content=func_call_res,
        )
    )
    call_data = FuncResult(name=func_call.name, result=func_resp)
    return call_data


@action()
async def prompt(message: str, **kwargs: Any) -> str:
    messages = await Chat.create(name="Prompt")
    await messages.add_message(chat_pb2.Message(role="user", content=message))
    res = await get_chat_completion(messages, **kwargs)
    return res.content


@action()
async def prompt_func_call(message: str, function: Callable):
    chat = await Chat.create(name="Prompt function call")
    await chat.add_message(chat_pb2.Message(role="user", content=message))
    func_call_result = await get_and_handle_chat_completion(
        chat,
        functions=[function],
        function_call={"name": function.__name__},
        on_request_function_call=call_function_from_openai_structure,
    )
    return func_call_result.result if func_call_result else None


@action()
async def prompt_structured_response(
    message: str,
    structure: Type[IsDataclass],
    **kwargs: Any,
):
    chat = await Chat.create(name="Get structured response")
    await chat.add_message(chat_pb2.Message(role="user", content=message))
    return await structure_from_chat(chat, structure, **kwargs)


@action()
async def structure_from_chat(
    chat: Chat, structure: Type[IsDataclass], **kwargs: Any
) -> Optional[IsDataclass]:
    func = dataclass_to_openai_structure(structure)
    function_call_arg = kwargs.pop("function_call", {"name": func["name"]})
    func_call_result = await get_and_handle_chat_completion(
        chat,
        functions=[func],
        function_call=function_call_arg,
        on_request_function_call=lambda _, call: create_instance_from_openai_structure(
            structure, call
        ),
        # Save tokens by not returning a string of the created instance,
        # since LLM will already know all details of the structure.
        create_func_llm_response=lambda _: "Instance created",
        **kwargs,
    )
    return func_call_result.result if func_call_result else None
