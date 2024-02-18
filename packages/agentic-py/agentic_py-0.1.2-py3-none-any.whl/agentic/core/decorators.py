import functools
import inspect
from contextvars import ContextVar
from typing import Tuple, Dict, Callable, Any, Optional, TypeVar, Protocol

from .logging import logger
from .serialization.task import TaskType, add_func_to_registry, func_fullname

# from .coordinator_client import get_client
from .context import schedule_context, caller_type_context

from .clients.coordinator_client import Handle

from .serialization import base


ACTION = TaskType.Value("ACTION")
WORKFLOW = TaskType.Value("WORKFLOW")


class AgenticCallable(Protocol):
    """Protocol for agentic functions with
    monkey-patched methods."""

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        ...

    async def schedule(self, *, args: Any, **kwargs: Any) -> Handle:
        ...

    async def run_direct(self, args: Any, **kwargs: Any) -> Any:
        ...


def _make_decorator(task_type: int, default_name: Callable[[Callable], str]):
    """
    Decorator for tasks.
    """

    def decorator_factory(
        name: Optional[Callable] = None,
        description: Optional[Callable] = None,
        serialization: base.SerializationType = base.JSON,
    ):
        def decorator(f: Callable) -> AgenticCallable:
            if not inspect.iscoroutinefunction(f):
                raise TypeError("The decorated function must be asynchronous")

            @functools.wraps(f)
            async def schedule(*, args, kwargs):  # type: ignore
                call_args = inspect.getcallargs(f, *args, **kwargs)
                schedule = schedule_context.get()
                assert schedule, "Schedule context not set"
                task_name = (
                    default_name(f)
                    if name is None
                    else _call_func_with_args(f, name, call_args)
                )
                task_description = (
                    ""
                    if description is None
                    else _call_func_with_args(f, description, call_args)
                )
                handle = await schedule(
                    name=task_name,
                    description=task_description,
                    task_type=task_type,
                    function=wrapped_func,
                    call_args=call_args,
                    serialization=serialization,
                )
                return handle

            @functools.wraps(f)
            async def run(*args: Any, **kwargs: Any) -> Any:
                caller_type = caller_type_context.get()
                if caller_type == ACTION:
                    # Run function as normal if we are calling from an action.
                    return await f(*args, **kwargs)
                handle = await schedule(args=args, kwargs=kwargs)
                return await handle.wait()

            @functools.wraps(f)
            async def wrapped_func(*args: Any, **kwargs: Any):
                return await run(*args, **kwargs)

            wrapped_func.schedule = schedule  # type: ignore
            wrapped_func.run_direct = f  # type: ignore
            wrapped_func.task_type = task_type  # type: ignore

            add_func_to_registry(wrapped_func)

            return wrapped_func  # type: ignore

        return decorator

    return decorator_factory


def _make_default_workflow_name(f: Callable) -> str:
    name = _get_workflow_name(f)
    return _humanize_name(name)


def _make_default_action_name(f: Callable) -> str:
    name = f.__name__
    return _humanize_name(name)


def _get_workflow_name(f: Callable) -> str:
    parts = func_fullname(f).split(".")
    for p in reversed(parts):
        if p not in ["main", "workflows"]:
            return p
    return parts[-1]


workflow = _make_decorator(WORKFLOW, _make_default_workflow_name)
action = _make_decorator(ACTION, _make_default_action_name)


def _humanize_name(name: str):
    return name.replace("_", " ").strip().capitalize()


def _call_func_with_args(f: Callable, name: Callable, call_args: dict) -> str:
    to_call = {}
    for p in inspect.signature(name).parameters:
        if p in call_args:
            to_call[p] = call_args[p]
        else:
            raise TypeError(f"Name function parameter {p} not in function {f.__name__}")
    return name(**to_call)
