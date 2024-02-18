import uuid
import asyncio
import pytest

from agentic.core.logging import logger
from agentic.core.run_workflow import run_workflow

import agentic as ag


ANSWER = 42


@ag.action()
async def get_result(to_add: int):
    return ANSWER + to_add


@pytest.mark.asyncio
async def test_simple_answer_workflow():
    @ag.workflow()
    async def simple_answer_wf():
        res = await get_result(0)
        return res

    res, _ = await run_workflow(
        run_id=uuid.uuid4(),
        workflow=simple_answer_wf,
    )
    assert res == ANSWER


@pytest.mark.asyncio
async def test_schedule():
    @ag.workflow()
    async def schedule_step_wf(to_add: int):
        handle = await get_result.schedule(args=(to_add,), kwargs={})
        res = await handle.wait()
        return res

    to_add = 2
    res, _ = await run_workflow(
        run_id=uuid.uuid4(),
        workflow=schedule_step_wf,
        args=(to_add,),
    )
    assert res == ANSWER + to_add


@pytest.mark.asyncio
async def test_concurrent_actions():
    val = 0

    @ag.action()
    async def inc_concurrent_cur(inc_by: int):
        nonlocal val
        val += inc_by
        return val

    @ag.workflow()
    async def concurrent_actions_wf():
        await asyncio.gather(
            inc_concurrent_cur(1), inc_concurrent_cur(2), inc_concurrent_cur(3)
        )
        return val

    res, _ = await run_workflow(
        run_id=uuid.uuid4(),
        workflow=concurrent_actions_wf,
        args=(),
    )

    assert res == 6


@pytest.mark.asyncio
async def test_child_workflow():
    val = 0

    @ag.action()
    async def child_inc_val(inc_by: int):
        nonlocal val
        val += inc_by
        return val

    @ag.workflow()
    async def child_wf():
        await child_inc_val(1)

    @ag.workflow()
    async def parent_wf():
        await child_wf()

    res, _ = await run_workflow(
        run_id=uuid.uuid4(),
        workflow=parent_wf,
        args=(),
    )

    assert val == 1


@pytest.mark.asyncio
async def test_workflow_exception():
    val = 0

    @ag.action()
    async def set_cur_for_exception_test(new_val: int):
        nonlocal val
        val = new_val

    @ag.action()
    async def raise_exception():
        raise ValueError("This is a test exception")

    @ag.workflow()
    async def exception_wf():
        try:
            await raise_exception()
        except Exception as e:
            await set_cur_for_exception_test(1)
            raise e
        await set_cur_for_exception_test(2)

    _, exc = await run_workflow(
        run_id=uuid.uuid4(),
        workflow=exception_wf,
        args=(),
    )
    assert isinstance(exc, ValueError)
    assert val == 1


@pytest.mark.asyncio
async def test_rerun_workflow():
    val = 0

    @ag.action()
    async def rerun_test_inc():
        nonlocal val
        val += 1
        return val

    @ag.workflow()
    async def rerun_test_wf():
        await rerun_test_inc()

    run_id = uuid.uuid4()

    await run_workflow(
        run_id=run_id,
        workflow=rerun_test_wf,
        args=(),
    )

    assert val == 1

    await run_workflow(
        run_id=run_id,
        workflow=rerun_test_wf,
        args=(),
    )

    # Re-running should have no effect
    # as the same run_id was used
    assert val == 1
