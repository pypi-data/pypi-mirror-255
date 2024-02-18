from typing import Callable, Any, Optional, Tuple, Optional, List
from dataclasses import dataclass
import uuid
import traceback

from agentic.proto import coordinator_pb2

from google.protobuf.any_pb2 import Any as PbAny

from ..logging import logger

from .base import (
    JSON,
    PROTOBUF,
    ensure_in_proto_type_registry,
    serialize_any_as_json_wrapper,
    deserialize_any,
    serialize_with_json_pickle,
    SerializationType,
)


TaskType = coordinator_pb2.TaskType


@dataclass
class LocalFuncCall:
    name: str
    description: str
    task_type: TaskType
    function: Callable
    call_args: dict
    serialization: SerializationType
    use_child_run_id: Optional[uuid.UUID] = None
    use_parent_run_id: Optional[uuid.UUID] = None


@dataclass
class LocalCompletion:
    result: Any


@dataclass
class WrappedException:
    message: str
    traceback: List[str]
    instance: Exception


INPUT = "input"


_func_registry = {}


def add_func_to_registry(function: Callable):
    function_name = func_fullname(function)
    if function_name in _func_registry:
        assert (
            _func_registry[function_name] == function
        ), "New function with same name added to registry"
    else:
        _func_registry[function_name] = function
    return function_name


def get_func_from_registry(function_name: str) -> Optional[Callable]:
    return _func_registry.get(function_name)


def serialize_func_call_as_task(call: LocalFuncCall) -> coordinator_pb2.Task:
    serialized_args = serialize_task_args(call.call_args, call.serialization)
    task = coordinator_pb2.Task(
        name=call.name,
        description=call.description,
        task_type=call.task_type,
        function_name=func_fullname(call.function),
        args=serialized_args,
    )
    return task


def serialize_task_result(result: Any, serialization: SerializationType) -> PbAny:
    if serialization == JSON:
        return serialize_any_as_json_wrapper(result)
    elif serialization == PROTOBUF:
        return _serialize_protobuf_result(result)
    raise ValueError("Invalid serialization type")


def serialize_exception(exception: Exception) -> PbAny:
    tb = traceback.format_tb(exception.__traceback__)
    wrapped = WrappedException(
        message=str(exception),
        traceback=tb,
        instance=exception,
    )
    return serialize_any_as_json_wrapper(wrapped)


def deserialize_exception(any_message: PbAny) -> Exception:
    wrapped, _ = deserialize_any(any_message)
    assert isinstance(
        wrapped, WrappedException
    ), f"Expected WrappedException, got {wrapped}"
    return wrapped.instance


def deserialize_task(
    task: coordinator_pb2.Task, use_child_run_id: Optional[uuid.UUID]
) -> LocalFuncCall:
    py_args, serialization_type = deserialize_task_args(task.args)
    assert isinstance(py_args, dict)
    function = get_func_from_registry(task.function_name)
    assert function, f"Function {task.function_name} not found in registry"
    return LocalFuncCall(
        name=task.name,
        description=task.description,
        task_type=task.task_type,
        function=function,
        call_args=py_args,
        use_child_run_id=use_child_run_id,
        serialization=serialization_type,
    )


def serialize_task_args(data: dict, serialization: SerializationType = JSON) -> PbAny:
    if serialization == JSON:
        return serialize_any_as_json_wrapper(data)
    elif serialization == PROTOBUF:
        return _serialize_protobuf_args(data)
    raise ValueError("Invalid serialization type")


def deserialize_task_args(args: PbAny) -> Tuple[dict, SerializationType]:
    py_args, serialization_type = deserialize_any(args)
    if serialization_type == SerializationType.protobuf:
        py_args = {INPUT: py_args}
    assert isinstance(py_args, dict)
    return py_args, serialization_type


def _serialize_protobuf_args(data: dict):
    input_msg = data.get(INPUT)
    if not input_msg:
        raise ValueError("Protobuf serialization selected, but no input value found")
    if len(data) > 1:
        raise ValueError("Protobuf serialization only supports one input value")
    any_message = PbAny()
    any_message.Pack(input_msg)
    # ensure_in_proto_type_registry(input_msg)
    return any_message


def _serialize_protobuf_result(result: Any):
    any_message = PbAny()
    any_message.Pack(result)
    # ensure_in_proto_type_registry(result)
    return any_message


def calls_match(call: LocalFuncCall, other_task: coordinator_pb2.Task) -> bool:
    # TODO - Fix this for protobuf Any
    as_task = serialize_func_call_as_task(call)
    if as_task.function_name != other_task.function_name:
        logger.info(
            f"\nFunction at this step changed: \
            \n  * Previous: {other_task.function_name} \
            \n  * Current: {as_task.function_name}",
        )
        return False
    args_as_str = as_task.args.decode("utf-8")
    other_args_as_str = other_task.args.decode("utf-8")
    if args_as_str != other_args_as_str:
        logger.info(
            f"\nArguments changed: \
            \n  * Previous: {other_args_as_str} \
            \n  * Current: {args_as_str}",
        )
        return False
    return True


def func_fullname(func: Callable):
    return func.__module__ + "." + func.__name__
