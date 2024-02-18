import uuid
import asyncio
import traceback
import re
import os
from copy import copy
from typing import Optional, Any, Tuple, Dict, Callable
from dataclasses import dataclass

from termcolor import colored

from .clients.coordinator_client import CoordinatorClient, Handle

from .serialization.task import (
    TaskType,
    LocalFuncCall,
    func_fullname,
)

from .context import schedule_context, caller_type_context, update_progress_context

from .logging import logger

from .serialization.base import SerializationType


_client = CoordinatorClient()

DEFAULT_WEB_URL = "http://localhost:8080"


def run_workflow_module(workflow_module: Any, *args: Tuple, **kwargs: Dict):
    run_id = uuid.UUID(os.environ["AGENTIC_RUN_ID"])
    web_url = os.environ.get("AGENTIC_WEB_URL", DEFAULT_WEB_URL)
    # loop = asyncio.new_event_loop()
    assert (
        workflow_module.main
    ), f"Workflow {workflow_module} does not have a main function"

    print(
        f"\nRunning workflow",
    )
    print(
        f"View progress: ",
        end="",
    )
    print(colored(f"{web_url}/r/{run_id}", "white", attrs=["bold"]))

    _, exc = asyncio.run(
        run_workflow(
            run_id=run_id,
            workflow=workflow_module.main,
            args=args,
            kwargs=kwargs,
            parent_run_id=None,
        )
    )

    if exc:
        print(colored("\nException in workflow:", "red", attrs=["bold"]))
        traceback.print_tb(exc.__traceback__)


async def run_workflow(
    *,
    run_id: uuid.UUID,
    workflow: Callable,
    args: Tuple = (),
    kwargs: Dict = {},
    parent_run_id: Optional[uuid.UUID] = None,
):
    assert getattr(workflow, "task_type", None) == TaskType.Value(
        "WORKFLOW"
    ), f"Function {func_fullname(workflow)} is not a workflow. Ensure it is wrapped with the workflow decorator."

    _step_id = 0

    def _get_step_id():
        nonlocal _step_id
        ret = _step_id
        _step_id += 1
        return ret

    run_schedule = lambda *args, **kwargs: _schedule(
        run_id=run_id,
        parent_run_id=parent_run_id,
        get_step_id=_get_step_id,
        *args,
        **kwargs,
    )
    schedule_context.set(run_schedule)

    handle = await workflow.schedule(args=args, kwargs=kwargs)

    # Run handle task loop independently
    asyncio.create_task(_run_handle_task_loop(run_id))

    exc = None
    ret = None
    try:
        ret = await handle.wait()
    except Exception as e:
        exc = e

    return ret, exc


async def _schedule(
    *,
    run_id: uuid.UUID,
    parent_run_id: Optional[uuid.UUID],
    name: str,
    description: str,
    task_type: TaskType,
    function: Callable,
    call_args: Dict,
    serialization: SerializationType,
    get_step_id: Callable[[], int],
) -> Handle:
    send_parent_run_id = None
    step_id = get_step_id()
    logger.debug("Starting run with ID: %s", run_id)
    if step_id == 0 and task_type != TaskType.Value("WORKFLOW"):
        raise ValueError("First step must be a workflow")
    if task_type == TaskType.Value("WORKFLOW"):
        if step_id == 0:
            # Send parent_run_id to simplify linking this workflow back
            # to parent. If we have a parent for this task,
            # then we cannot have a child as well.
            send_parent_run_id = parent_run_id
    handle = await _client.schedule_task(
        run_id,
        step_id,
        LocalFuncCall(
            name=name,
            description=description,
            task_type=task_type,
            function=function,
            call_args=call_args,
            use_child_run_id=None,
            use_parent_run_id=send_parent_run_id,
            serialization=serialization,
        ),
    )
    return handle


async def _run_handle_task_loop(run_id: uuid.UUID):
    finished_event = asyncio.Event()

    def on_main_workflow_done(result: Any):
        finished_event.set()

    def on_main_workflow_failed(exc: Exception):
        finished_event.set()

    while True:
        logger.debug("Waiting on task for run: %s", run_id)
        get_aiotask = asyncio.create_task(_client.get_next_task(run_id))
        finished_aiotask = asyncio.create_task(finished_event.wait())
        done, pending = await asyncio.wait(
            [get_aiotask, finished_aiotask], return_when=asyncio.FIRST_COMPLETED
        )
        for aiotask in pending:
            # Cancel because we can just restart the task on next loop
            aiotask.cancel()
        for aiotask in done:
            if aiotask == get_aiotask:
                res = aiotask.result()
                assert type(res) == tuple
                step, task_run_id, call = res
                on_done = on_main_workflow_done if step == 0 else None
                on_exc = on_main_workflow_failed if step == 0 else None
                asyncio.create_task(
                    _handle_scheduled_task(
                        run_id,
                        step,
                        task_run_id,
                        call,
                        on_done=on_done,
                        on_exception=on_exc,
                    )
                )
            elif aiotask == finished_aiotask:
                return


async def _handle_scheduled_task(
    run_id: uuid.UUID,
    step: int,
    task_run_id: uuid.UUID,
    call: LocalFuncCall,
    on_done: Optional[Callable],
    on_exception: Optional[Callable],
):
    logger.debug("Handling task for run: %s, step: %s", run_id, step)
    ret, exc = await _run_function_and_store_result(run_id, step, task_run_id, call)

    if exc and on_exception:
        on_exception(exc)

    if on_done:
        on_done(ret)


async def _run_function_and_store_result(
    run_id: uuid.UUID, step: int, task_run_id: uuid.UUID, call: LocalFuncCall
):
    _log_step(step, call)

    await _client.register_task_started(run_id, step, task_run_id)

    async def _update_run_progress(progress: Any):
        await _client.update_task_run_progress(run_id, step, task_run_id, progress)

    update_progress_context.set(_update_run_progress)

    exc = None
    result = None
    try:
        result = await _run_function(run_id, call, step)
    except Exception as e:
        exc = e

    if exc:
        await _client.register_task_failed(run_id, step, task_run_id, exc)
    else:
        await _client.register_task_completed(
            run_id, step, task_run_id, result, call.serialization
        )
    return result, exc


async def _run_function(
    run_id: uuid.UUID,
    call: LocalFuncCall,
    step: int,
):
    caller_type_context.set(call.task_type)
    call_args = copy(call.call_args)

    # TODO - This assumes kwargs will always be called kwargs.
    # Need to fix this.
    kwargs = call_args.pop("kwargs", {})
    args = call_args.values()

    if call.task_type == TaskType.Value("WORKFLOW") and step != 0:
        # First step is always the current workflow, every other workflow
        # task is a child workflow
        assert call.use_child_run_id, "Child workflow must have a child run ID"
        result, exc = await run_as_child_workflow(
            parent_run_id=run_id,
            function=call.function,
            args=(),
            kwargs=call_args,
            use_child_run_id=call.use_child_run_id,
        )
        if exc:
            raise exc
    else:
        logger.info(colored("\nRunning...\n", "white", attrs=["bold"]))
        # At this point we want to run the inner function directly, otherwise this will just
        # reschedule the function as a new task.
        result = await call.function.run_direct(*args, **kwargs)
    return result


async def run_as_child_workflow(
    *,
    parent_run_id: uuid.UUID,
    function: Callable,
    args: Tuple,
    kwargs: Dict,
    use_child_run_id: uuid.UUID,
) -> Any:
    return await run_workflow(
        run_id=use_child_run_id,
        workflow=function,
        args=args,
        kwargs=kwargs,
        parent_run_id=parent_run_id,
    )


def _log_step(step: int, call: LocalFuncCall):
    args = str(call.call_args)
    # Replace repeated spaces with single space.
    # Often args have strings split over multiple lines for readability.
    args = re.sub(r"\s+", " ", args)
    args = args[:100] + "... ]" if len(args) > 100 else args
    logger.info(
        colored(
            f"\nStep {step}. {func_fullname(call.function)}",
            "green",
            attrs=["bold"],
        ),
    )
    logger.info(colored(f"Arguments: {args}", "white"))
