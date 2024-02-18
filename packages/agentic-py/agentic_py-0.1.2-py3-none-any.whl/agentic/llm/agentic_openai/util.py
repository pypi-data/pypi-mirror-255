from typing import Callable, Type, Any, List, Dict
import typing
import pprint

import re

import inspect

import json

from agentic.proto import chat_pb2

from agentic.core.typing import IsDataclass


def function_to_openai_structure(func: Callable):
    sig = inspect.signature(func)
    doc = func.__doc__ or ""
    parameters = []
    for name, param in sig.parameters.items():
        param_desc = {
            "name": name,
            "type_descriptor": _get_type_descriptor(param.annotation),
            "required": param.default == inspect.Parameter.empty,
        }
        param_doc = _get_param_docstring(doc, name)
        if param_doc:
            param_desc["description"] = param_doc
        parameters.append(param_desc)

    func_properties = {}
    for param in parameters:
        desc = param["type_descriptor"]
        if "description" in param:
            desc["description"] = param["description"]
        func_properties[param["name"]] = desc

    function_info = {
        "name": func.__name__,
        "parameters": {
            "type": "object",
            "properties": func_properties,
            "required": [param["name"] for param in parameters if param["required"]],
        },
    }

    if func.__doc__:
        function_info["description"] = func.__doc__

    return function_info


def dataclass_to_openai_structure(cls: Type[IsDataclass]):
    cls_name = cls.__name__
    assert cls_name is not None
    doc = cls.__doc__ or ""
    dataclass_info = {
        "name": "create_" + cls_name,
        "description": f"Create a new {cls_name} object. Object structure description: {doc}.",
        "parameters": _dataclass_type_descriptor(cls),
    }
    return dataclass_info


async def call_function_from_openai_structure(
    functions: List[Callable], openai_call: chat_pb2.FunctionCall
):
    # Find the function with the correct name
    func = next((f for f in functions if f.__name__ == openai_call.name), None)
    if func is None:
        raise Exception(f"No function found with name '{openai_call.name}'")
    try:
        args = json.loads(openai_call.arguments, strict=False)
    except json.decoder.JSONDecodeError:
        raise Exception(
            f"Could not decode arguments for function '{func.__name__}': {openai_call.arguments}"
        )
    return await call_function(func, **args)


def create_instance_from_openai_structure(
    cls: Type, openai_call: chat_pb2.FunctionCall
):
    # TODO - Handle case where the type has nested types, e.g. a dataclass
    # that refers to other dataclasses.
    args = json.loads(openai_call.arguments, strict=False)
    return cls(**args)


def _get_type_descriptor(t: type) -> dict:
    res = None
    err = None
    if t == str:
        res = {"type": "string"}
    elif t == int:
        res = {"type": "integer"}
    elif t == float or t == int | float:
        res = {"type": "number"}
    elif t == bool:
        res = {"type": "boolean"}
    elif t == type(None):
        res = {"type": "null"}
    elif t == list:
        res = {"type": "array"}
    elif t == dict:
        res = {"type": "object"}
    elif type(t) == typing._GenericAlias:
        res, err = _handle_generic_alias(t)
    elif hasattr(t, "__dataclass_fields__"):
        res = _dataclass_type_descriptor(t)
    if not res:
        if err:
            raise ValueError(err)
        raise ValueError(f"Unsupported type: {t}")
    return res


def _dataclass_type_descriptor(cls: Type[IsDataclass]):
    sig = inspect.signature(cls.__init__)
    doc = cls.__doc__ or ""
    assert doc is not None
    parameters = []
    for name, param in sig.parameters.items():
        if name == "self":
            continue
        param_desc = {
            "name": name,
            "type_descriptor": _get_type_descriptor(param.annotation),
            "required": param.default == inspect.Parameter.empty,
        }
        param_doc = _get_param_docstring(doc, name)
        if param_doc:
            param_desc["description"] = param_doc
        parameters.append(param_desc)

    dataclass_properties = {}
    for param in parameters:
        desc = param["type_descriptor"]
        if "description" in param:
            desc["description"] = param["description"]
        dataclass_properties[param["name"]] = desc

    return {
        "type": "object",
        "properties": dataclass_properties,
        "required": [param["name"] for param in parameters if param["required"]],
    }


def _handle_generic_alias(t: typing._GenericAlias):
    res = None
    err = None
    if t.__origin__ == list:
        res = {"type": "array", "items": _get_type_descriptor(t.__args__[0])}
    elif t.__origin__ == dict:
        if t.__args__[0] != str:
            err = f"Unsupported type (JSON keys must be strings): {t}"
        else:
            res = {
                "type": "object",
                "patternProperties": {".*": _get_type_descriptor(t.__args__[1])},
            }
    return res, err


def _get_param_docstring(docstring: str, param_name: str):
    pattern = r":param " + param_name + r": (.*)"
    matches = re.findall(pattern, docstring)
    if len(matches) == 0:
        return None
    if len(matches) > 1:
        raise Exception(f"More than one match found for parameter '{param_name}'")
    else:
        return matches[0]


async def call_function(func: Callable, *args: Any, **kwargs: Any):
    if inspect.iscoroutinefunction(func):
        return await func(*args, **kwargs)
    else:
        return func(*args, **kwargs)
