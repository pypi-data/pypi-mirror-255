from typing import Any, Tuple, Optional
import asyncio
import uuid
from dataclasses import dataclass

import backoff

from grpc.aio import AioRpcError

from agentic.proto import coordinator_pb2_grpc, coordinator_pb2

from ..logging import logger

from .grpc_channel import get_channel

from ..serialization.task import (
    LocalFuncCall,
    LocalCompletion,
    serialize_func_call_as_task,
    deserialize_task,
    serialize_task_result,
    calls_match,
    serialize_exception,
    deserialize_exception,
)

from ..serialization.base import (
    SerializationType,
    serialize_any_as_json_wrapper,
    deserialize_any,
)


DEFAULT_TIMEOUT = 30


class CoordinatorClient:
    @property
    async def _stub(self) -> coordinator_pb2_grpc.CoordinatorServiceStub:
        channel = await get_channel()
        stub = coordinator_pb2_grpc.CoordinatorServiceStub(channel)
        return stub

    async def schedule_task(
        self,
        run_id: uuid.UUID,
        step_id: int,
        call: LocalFuncCall,
    ) -> "Handle":
        assert not (
            call.use_parent_run_id and call.use_child_run_id
        ), "Must specify only one of parent_run_id or child_run_id"
        task = serialize_func_call_as_task(call)
        parent_run_id_str = (
            str(call.use_parent_run_id) if call.use_parent_run_id else None
        )
        child_run_id_str = str(call.use_child_run_id) if call.use_child_run_id else None
        req = coordinator_pb2.ScheduleTaskRequest(
            run_id=str(run_id),
            step=step_id,
            parent_run_id=parent_run_id_str,
            child_run_id=child_run_id_str,
            task=task,
        )
        stub = await self._stub
        logger.debug("Scheduling task: %s %d", req.run_id, req.step)
        logger.debug("Task details: %s", task)
        res = await stub.ScheduleTask(req, timeout=DEFAULT_TIMEOUT)
        logger.debug("Scheduled task: %s %d", req.run_id, req.step)
        handle = Handle(client=self, run_id=run_id, step=res.step)
        return handle

    async def await_task_result(
        self, run_id: uuid.UUID, step: int
    ) -> coordinator_pb2.TaskRunResult:
        stub = await self._stub
        logger.debug("Making AwaitTaskResult request for %s %s", run_id, step)
        res = await stub.AwaitTaskResult(
            coordinator_pb2.AwaitTaskResultRequest(run_id=str(run_id), step=step),
        )
        logger.debug("Retrieved task result for %s %s", run_id, step)
        return res.result

    @backoff.on_exception(
        backoff.constant,
        (AioRpcError),
        max_tries=3,
        logger=None,
    )
    async def get_next_task(
        self, run_id: uuid.UUID
    ) -> Tuple[int, uuid.UUID, LocalFuncCall]:
        stub = await self._stub
        res = await stub.GetNextTask(
            coordinator_pb2.GetNextTaskRequest(run_id=str(run_id))
        )
        call = deserialize_task(res.task, res.use_child_run_id)
        return res.step, uuid.UUID(res.task_run_id), call

    async def register_task_started(
        self, run_id: uuid.UUID, step: int, task_run_id: uuid.UUID
    ):
        stub = await self._stub
        await stub.RegisterTaskStarted(
            coordinator_pb2.RegisterTaskStartedRequest(
                run_id=str(run_id), step=step, task_run_id=str(task_run_id)
            ),
            timeout=DEFAULT_TIMEOUT,
        )

    async def register_task_completed(
        self,
        run_id: uuid.UUID,
        step: int,
        task_run_id: uuid.UUID,
        result: Any,
        serialization: SerializationType,
    ):
        res = serialize_task_result(result, serialization=serialization)
        stub = await self._stub
        await stub.RegisterTaskCompleted(
            coordinator_pb2.RegisterTaskCompletedRequest(
                run_id=str(run_id), step=step, task_run_id=str(task_run_id), result=res
            ),
            timeout=DEFAULT_TIMEOUT,
        )

    async def register_task_failed(
        self, run_id: uuid.UUID, step: int, task_run_id: uuid.UUID, exception: Exception
    ):
        exc = serialize_exception(exception)
        stub = await self._stub
        await stub.RegisterTaskFailed(
            coordinator_pb2.RegisterTaskFailedRequest(
                run_id=str(run_id),
                step=step,
                task_run_id=str(task_run_id),
                exception=exc,
            ),
            timeout=DEFAULT_TIMEOUT,
        )

    @backoff.on_exception(
        backoff.constant,
        (AioRpcError),
        max_tries=3,
    )
    async def update_task_run_progress(
        self, run_id: uuid.UUID, step: int, task_run_id: uuid.UUID, progress: Any
    ):
        stub = await self._stub
        await stub.UpdateTaskRunProgress(
            coordinator_pb2.UpdateTaskRunProgressRequest(
                run_id=str(run_id),
                step=step,
                task_run_id=str(task_run_id),
                progress=serialize_any_as_json_wrapper(progress),
            ),
            timeout=DEFAULT_TIMEOUT,
        )

    async def register_new_run_from_existing(
        self, existing_run_id: uuid.UUID, new_run_id: uuid.UUID
    ):
        stub = await self._stub
        await stub.RegisterNewRunFromExisting(
            coordinator_pb2.RegisterNewRunFromExistingRequest(
                new_run_id=str(new_run_id), existing_run_id=str(existing_run_id)
            ),
            timeout=DEFAULT_TIMEOUT,
        )

    async def get_matching_historical_data(
        self, run_id: uuid.UUID, step: int, call: LocalFuncCall
    ) -> Tuple[Optional[LocalCompletion], Optional[uuid.UUID]]:
        stub = await self._stub
        res = await stub.QueryScheduledTask(
            coordinator_pb2.QueryScheduledTaskRequest(
                run_id=str(run_id),
                step=step,
            ),
            timeout=DEFAULT_TIMEOUT,
        )
        if not res.HasField("task"):
            return None, None

        if not calls_match(call, res.task):
            return None, None

        completion = None
        if not res.HasField("completion"):
            return None, None
        # Ignore serialization type as it should not be needed
        prev_result, _ = deserialize_any(res.completion.result)
        completion = LocalCompletion(result=prev_result)
        return completion, res.child_run_id


class Handle:
    def __init__(self, *, client: CoordinatorClient, run_id: uuid.UUID, step: int):
        self.client = client
        self.run_id = run_id
        self.step = step

    async def wait(self):
        res = await self.client.await_task_result(self.run_id, self.step)
        res_type = res.WhichOneof("result")
        if res_type == "failed":
            exc = deserialize_exception(res.failed.exception)
            assert isinstance(exc, Exception), f"Expected exception, got {exc}"
            raise exc
        elif res_type == "completed":
            result, _ = deserialize_any(res.completed.result)
            return result
        raise Exception("Unexpected result type")
