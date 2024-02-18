from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import any_pb2 as _any_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
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

class TaskType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    WORKFLOW: _ClassVar[TaskType]
    ACTION: _ClassVar[TaskType]

WORKFLOW: TaskType
ACTION: TaskType

class ScheduleTaskRequest(_message.Message):
    __slots__ = ("run_id", "step", "parent_run_id", "child_run_id", "task")
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    STEP_FIELD_NUMBER: _ClassVar[int]
    PARENT_RUN_ID_FIELD_NUMBER: _ClassVar[int]
    CHILD_RUN_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_FIELD_NUMBER: _ClassVar[int]
    run_id: str
    step: int
    parent_run_id: str
    child_run_id: str
    task: Task
    def __init__(
        self,
        run_id: _Optional[str] = ...,
        step: _Optional[int] = ...,
        parent_run_id: _Optional[str] = ...,
        child_run_id: _Optional[str] = ...,
        task: _Optional[_Union[Task, _Mapping]] = ...,
    ) -> None: ...

class ScheduleTaskResponse(_message.Message):
    __slots__ = ("run_id", "step")
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    STEP_FIELD_NUMBER: _ClassVar[int]
    run_id: str
    step: int
    def __init__(
        self, run_id: _Optional[str] = ..., step: _Optional[int] = ...
    ) -> None: ...

class AwaitTaskResultRequest(_message.Message):
    __slots__ = ("run_id", "step")
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    STEP_FIELD_NUMBER: _ClassVar[int]
    run_id: str
    step: int
    def __init__(
        self, run_id: _Optional[str] = ..., step: _Optional[int] = ...
    ) -> None: ...

class AwaitTaskResultResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: TaskRunResult
    def __init__(
        self, result: _Optional[_Union[TaskRunResult, _Mapping]] = ...
    ) -> None: ...

class GetNextTaskRequest(_message.Message):
    __slots__ = ("run_id",)
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    run_id: str
    def __init__(self, run_id: _Optional[str] = ...) -> None: ...

class GetNextTaskResponse(_message.Message):
    __slots__ = ("step", "task_run_id", "task", "use_child_run_id")
    STEP_FIELD_NUMBER: _ClassVar[int]
    TASK_RUN_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_FIELD_NUMBER: _ClassVar[int]
    USE_CHILD_RUN_ID_FIELD_NUMBER: _ClassVar[int]
    step: int
    task_run_id: str
    task: Task
    use_child_run_id: str
    def __init__(
        self,
        step: _Optional[int] = ...,
        task_run_id: _Optional[str] = ...,
        task: _Optional[_Union[Task, _Mapping]] = ...,
        use_child_run_id: _Optional[str] = ...,
    ) -> None: ...

class QueryScheduledTaskRequest(_message.Message):
    __slots__ = ("run_id", "step")
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    STEP_FIELD_NUMBER: _ClassVar[int]
    run_id: str
    step: int
    def __init__(
        self, run_id: _Optional[str] = ..., step: _Optional[int] = ...
    ) -> None: ...

class QueryScheduledTaskResponse(_message.Message):
    __slots__ = ("task", "completion", "child_run_id")
    TASK_FIELD_NUMBER: _ClassVar[int]
    COMPLETION_FIELD_NUMBER: _ClassVar[int]
    CHILD_RUN_ID_FIELD_NUMBER: _ClassVar[int]
    task: Task
    completion: TaskCompleted
    child_run_id: str
    def __init__(
        self,
        task: _Optional[_Union[Task, _Mapping]] = ...,
        completion: _Optional[_Union[TaskCompleted, _Mapping]] = ...,
        child_run_id: _Optional[str] = ...,
    ) -> None: ...

class RegisterTaskStartedRequest(_message.Message):
    __slots__ = ("run_id", "step", "task_run_id")
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    STEP_FIELD_NUMBER: _ClassVar[int]
    TASK_RUN_ID_FIELD_NUMBER: _ClassVar[int]
    run_id: str
    step: int
    task_run_id: str
    def __init__(
        self,
        run_id: _Optional[str] = ...,
        step: _Optional[int] = ...,
        task_run_id: _Optional[str] = ...,
    ) -> None: ...

class RegisterTaskStartedResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class RegisterTaskFailedRequest(_message.Message):
    __slots__ = ("run_id", "step", "task_run_id", "exception")
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    STEP_FIELD_NUMBER: _ClassVar[int]
    TASK_RUN_ID_FIELD_NUMBER: _ClassVar[int]
    EXCEPTION_FIELD_NUMBER: _ClassVar[int]
    run_id: str
    step: int
    task_run_id: str
    exception: _any_pb2.Any
    def __init__(
        self,
        run_id: _Optional[str] = ...,
        step: _Optional[int] = ...,
        task_run_id: _Optional[str] = ...,
        exception: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...,
    ) -> None: ...

class RegisterTaskFailedResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class RegisterTaskCompletedRequest(_message.Message):
    __slots__ = ("run_id", "step", "task_run_id", "result")
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    STEP_FIELD_NUMBER: _ClassVar[int]
    TASK_RUN_ID_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    run_id: str
    step: int
    task_run_id: str
    result: _any_pb2.Any
    def __init__(
        self,
        run_id: _Optional[str] = ...,
        step: _Optional[int] = ...,
        task_run_id: _Optional[str] = ...,
        result: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...,
    ) -> None: ...

class RegisterTaskCompletedResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class UpdateTaskRunProgressRequest(_message.Message):
    __slots__ = ("run_id", "step", "task_run_id", "progress")
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    STEP_FIELD_NUMBER: _ClassVar[int]
    TASK_RUN_ID_FIELD_NUMBER: _ClassVar[int]
    PROGRESS_FIELD_NUMBER: _ClassVar[int]
    run_id: str
    step: int
    task_run_id: str
    progress: _any_pb2.Any
    def __init__(
        self,
        run_id: _Optional[str] = ...,
        step: _Optional[int] = ...,
        task_run_id: _Optional[str] = ...,
        progress: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...,
    ) -> None: ...

class UpdateTaskRunProgressResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListWorkflowRunsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListWorkflowRunsResponse(_message.Message):
    __slots__ = ("runs",)
    RUNS_FIELD_NUMBER: _ClassVar[int]
    runs: _containers.RepeatedCompositeFieldContainer[WorkflowRun]
    def __init__(
        self, runs: _Optional[_Iterable[_Union[WorkflowRun, _Mapping]]] = ...
    ) -> None: ...

class WatchWorkflowRunRequest(_message.Message):
    __slots__ = ("run_id",)
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    run_id: str
    def __init__(self, run_id: _Optional[str] = ...) -> None: ...

class GetWorkflowRunRequest(_message.Message):
    __slots__ = ("run_id",)
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    run_id: str
    def __init__(self, run_id: _Optional[str] = ...) -> None: ...

class GetWorkflowRunResponse(_message.Message):
    __slots__ = ("scheduled_tasks", "path", "new_run_id")
    SCHEDULED_TASKS_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    NEW_RUN_ID_FIELD_NUMBER: _ClassVar[int]
    scheduled_tasks: _containers.RepeatedCompositeFieldContainer[ScheduledTask]
    path: PathPart
    new_run_id: str
    def __init__(
        self,
        scheduled_tasks: _Optional[_Iterable[_Union[ScheduledTask, _Mapping]]] = ...,
        path: _Optional[_Union[PathPart, _Mapping]] = ...,
        new_run_id: _Optional[str] = ...,
    ) -> None: ...

class RegisterNewRunFromExistingRequest(_message.Message):
    __slots__ = ("existing_run_id", "new_run_id")
    EXISTING_RUN_ID_FIELD_NUMBER: _ClassVar[int]
    NEW_RUN_ID_FIELD_NUMBER: _ClassVar[int]
    existing_run_id: str
    new_run_id: str
    def __init__(
        self, existing_run_id: _Optional[str] = ..., new_run_id: _Optional[str] = ...
    ) -> None: ...

class RegisterNewRunFromExistingResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DataWrapper(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: _any_pb2.Any
    def __init__(
        self, data: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...
    ) -> None: ...

class Task(_message.Message):
    __slots__ = ("name", "description", "task_type", "function_name", "args")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TASK_TYPE_FIELD_NUMBER: _ClassVar[int]
    FUNCTION_NAME_FIELD_NUMBER: _ClassVar[int]
    ARGS_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    task_type: TaskType
    function_name: str
    args: _any_pb2.Any
    def __init__(
        self,
        name: _Optional[str] = ...,
        description: _Optional[str] = ...,
        task_type: _Optional[_Union[TaskType, str]] = ...,
        function_name: _Optional[str] = ...,
        args: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...,
    ) -> None: ...

class WorkflowRun(_message.Message):
    __slots__ = ("run_id",)
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    run_id: str
    def __init__(self, run_id: _Optional[str] = ...) -> None: ...

class ScheduledTask(_message.Message):
    __slots__ = ("run_id", "parent_run_id", "child_run_id", "step", "task", "runs")
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    PARENT_RUN_ID_FIELD_NUMBER: _ClassVar[int]
    CHILD_RUN_ID_FIELD_NUMBER: _ClassVar[int]
    STEP_FIELD_NUMBER: _ClassVar[int]
    TASK_FIELD_NUMBER: _ClassVar[int]
    RUNS_FIELD_NUMBER: _ClassVar[int]
    run_id: str
    parent_run_id: str
    child_run_id: str
    step: int
    task: Task
    runs: _containers.RepeatedCompositeFieldContainer[TaskRun]
    def __init__(
        self,
        run_id: _Optional[str] = ...,
        parent_run_id: _Optional[str] = ...,
        child_run_id: _Optional[str] = ...,
        step: _Optional[int] = ...,
        task: _Optional[_Union[Task, _Mapping]] = ...,
        runs: _Optional[_Iterable[_Union[TaskRun, _Mapping]]] = ...,
    ) -> None: ...

class TaskRun(_message.Message):
    __slots__ = ("started_at", "result", "progress")
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    PROGRESS_FIELD_NUMBER: _ClassVar[int]
    started_at: _timestamp_pb2.Timestamp
    result: TaskRunResult
    progress: _any_pb2.Any
    def __init__(
        self,
        started_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
        result: _Optional[_Union[TaskRunResult, _Mapping]] = ...,
        progress: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...,
    ) -> None: ...

class TaskStarted(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class TaskRunResult(_message.Message):
    __slots__ = ("completed", "failed")
    COMPLETED_FIELD_NUMBER: _ClassVar[int]
    FAILED_FIELD_NUMBER: _ClassVar[int]
    completed: TaskCompleted
    failed: TaskFailed
    def __init__(
        self,
        completed: _Optional[_Union[TaskCompleted, _Mapping]] = ...,
        failed: _Optional[_Union[TaskFailed, _Mapping]] = ...,
    ) -> None: ...

class TaskCompleted(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: _any_pb2.Any
    def __init__(
        self, result: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...
    ) -> None: ...

class TaskFailed(_message.Message):
    __slots__ = ("exception",)
    EXCEPTION_FIELD_NUMBER: _ClassVar[int]
    exception: _any_pb2.Any
    def __init__(
        self, exception: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...
    ) -> None: ...

class PathPart(_message.Message):
    __slots__ = ("run_id", "name", "parent")
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PARENT_FIELD_NUMBER: _ClassVar[int]
    run_id: str
    name: str
    parent: PathPart
    def __init__(
        self,
        run_id: _Optional[str] = ...,
        name: _Optional[str] = ...,
        parent: _Optional[_Union[PathPart, _Mapping]] = ...,
    ) -> None: ...
