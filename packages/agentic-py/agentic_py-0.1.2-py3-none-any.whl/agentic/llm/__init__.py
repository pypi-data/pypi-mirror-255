from typing import Any, TypeVar, Type, Optional, List, Union, Callable, Dict

from types import SimpleNamespace

from agentic.proto import chat_pb2

from agentic.core import action
from agentic.core.typing import IsDataclass

from .agentic_openai import (
    prompt as openai_prompt,
    prompt_structured_response as openai_prompt_structured_response,
    structure_from_chat as openai_structure_from_chat,
    get_chat_completion as openai_get_chat_completion,
    get_and_handle_chat_completion as openai_get_and_handle_chat_completion,
)
from .chat import Chat


llms = SimpleNamespace(openai="openai", onprem="onprem")

openai = llms.openai


@action(name=lambda: f"Prompt LLM")
async def prompt(
    message: str, llm: SimpleNamespace = llms.openai, **kwargs: Any
) -> str:
    """Takes a prompt and returns a single completion result."""
    if llm == llms.openai:
        return await openai_prompt(message, **kwargs)
    raise NotImplementedError(f"llm '{llm}' not implemented")


Structure = TypeVar("Structure")


@action()
async def get_chat_completion(
    chat: Chat,
    llm: SimpleNamespace = llms.openai,
    function_call: str = "auto",
    **kwargs: Any,
) -> chat_pb2.Message:
    """Takes Messages and produces a chat response from them."""
    if llm == llms.openai:
        return await openai_get_chat_completion(
            chat, function_call=function_call, **kwargs
        )
    raise NotImplementedError(f"llm '{llm}' not implemented")


@action()
async def get_and_handle_chat_completion(
    chat: Chat,
    llm: SimpleNamespace = llms.openai,
    functions: List[Union[Callable, Dict]] = [],
    on_request_func_call: Optional[Callable] = None,
    create_func_llm_response: Optional[Callable] = None,
    **kwargs: Any,
):
    if llm == llms.openai:
        return await openai_get_and_handle_chat_completion(
            chat,
            functions=functions,
            on_request_func_call=on_request_func_call,
            create_func_llm_response=create_func_llm_response,
            **kwargs,
        )
    raise NotImplementedError(f"llm '{llm}' not implemented")


@action(
    name=lambda: "Get structured response from LLM",
)
async def prompt_structured_response(
    message: str,
    structure: Type[IsDataclass],
    llm: SimpleNamespace = llms.openai,
    **kwargs: Any,
) -> IsDataclass:
    """Takes a prompt and produces a structured object from it."""
    if llm == llms.openai:
        return await openai_prompt_structured_response(
            message=message, structure=structure, **kwargs
        )
    raise NotImplementedError(f"llm '{llm}' not implemented")


@action()
async def structure_from_chat(
    chat: Chat,
    structure: Type[IsDataclass],
    llm: SimpleNamespace = llms.openai,
    **kwargs: Any,
) -> Optional[IsDataclass]:
    """Takes Chat and may produce a structured object from them."""
    if llm == llms.openai:
        return await openai_structure_from_chat(chat, structure, **kwargs)
    raise NotImplementedError(f"llm '{llm}' not implemented")
