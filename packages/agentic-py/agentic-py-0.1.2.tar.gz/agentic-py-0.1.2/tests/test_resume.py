import uuid
import asyncio
import pytest
from multiprocessing import Process
import tempfile
import os

from agentic.core.logging import logger
from agentic.core.run_workflow import run_workflow

import agentic as ag


@ag.action()
async def resume_test_inc_val(filename: str):
    cur_val = _get_val_from_file(filename)
    _set_val_in_file(filename, cur_val + 1)


@ag.action()
async def set_before_sleep_val(filename: str):
    _set_val_in_file(filename, 1)


@ag.workflow()
async def resume_test_wf(
    val_filename: str, should_hang_filename: str, before_sleep_filename: str
):
    await resume_test_inc_val(val_filename)
    # Signals that the previous step has definitely finished
    # and result has been recorded
    await set_before_sleep_val(before_sleep_filename)
    if _get_val_from_file(should_hang_filename) == 1:
        # Hang forever so we can terminate without running final step
        await asyncio.sleep(9999)
    await resume_test_inc_val(val_filename)


def _run_wf_in_process(wf, run_id, *args):
    asyncio.run(
        run_workflow(
            run_id=run_id,
            workflow=wf,
            args=args,
        )
    )


@pytest.mark.asyncio
async def test_simple_resume_workflow():
    val_filename = await _get_int_tmp_file(0)
    should_hang_filename = await _get_int_tmp_file(1)
    before_sleep_filename = await _get_int_tmp_file(0)

    run_id = uuid.uuid4()

    pr = Process(
        target=_run_wf_in_process,
        args=(
            resume_test_wf,
            run_id,
            val_filename,
            should_hang_filename,
            before_sleep_filename,
        ),
    )
    pr.start()
    # Indicates that the val action has run and so we
    # can terminate
    sleep_val = await _await_val(before_sleep_filename, 1)
    assert sleep_val == 1
    pr.terminate()
    pr.join()

    val = _get_val_from_file(val_filename)
    assert val == 1

    # Prevent hang on next run
    _set_val_in_file(should_hang_filename, 0)

    pr = Process(
        target=_run_wf_in_process,
        args=(
            resume_test_wf,
            run_id,
            val_filename,
            should_hang_filename,
            before_sleep_filename,
        ),
    )
    pr.start()
    pr.join(timeout=10)
    assert pr.exitcode is not None, "Process should have terminated"

    val = _get_val_from_file(val_filename)

    # Should not have re-run the first action, only the second which was never executed
    assert val == 2


@ag.workflow()
async def resume_with_child_wf(
    val_filename: str, should_hang_filename: str, before_sleep_filename: str
):
    await resume_test_inc_val(val_filename)
    await resume_test_wf(val_filename, should_hang_filename, before_sleep_filename)
    await resume_test_inc_val(val_filename)


@pytest.mark.asyncio
async def test_resume_workflow_with_child_workflow():
    val_filename = await _get_int_tmp_file(0)
    should_hang_filename = await _get_int_tmp_file(1)
    before_sleep_filename = await _get_int_tmp_file(0)

    run_id = uuid.uuid4()

    pr = Process(
        target=_run_wf_in_process,
        args=(
            resume_with_child_wf,
            run_id,
            val_filename,
            should_hang_filename,
            before_sleep_filename,
        ),
    )
    pr.start()
    # Indicates that the val action has run and so we
    # can terminate
    sleep_val = await _await_val(before_sleep_filename, 1)
    assert sleep_val == 1
    pr.terminate()
    pr.join()

    # Should have run in parent and child workflows
    val = _get_val_from_file(val_filename)
    assert val == 2

    # Prevent hang on next run
    _set_val_in_file(should_hang_filename, 0)

    pr = Process(
        target=_run_wf_in_process,
        args=(
            resume_with_child_wf,
            run_id,
            val_filename,
            should_hang_filename,
            before_sleep_filename,
        ),
    )
    pr.start()
    pr.join(timeout=10)
    assert pr.exitcode is not None, "Process should have terminated"

    val = _get_val_from_file(val_filename)

    # Should have skipped the first two invocations on replay
    # and just run final two
    # TODO - This is still flaky, sometimes get 5, sometimes 4.
    assert val == 4


def _get_val_from_file(filename: str):
    with open(filename, "r") as f:
        return int(f.read())


def _set_val_in_file(filename: str, new_val: int):
    with open(filename, "w") as f:
        f.write(str(new_val))


async def _get_int_tmp_file(init_val: int) -> str:
    new_file, val_filename = tempfile.mkstemp()
    os.close(new_file)
    _set_val_in_file(val_filename, init_val)
    return val_filename


async def _await_val(filename: str, expected_val: int, retry=30):
    count = 0
    while count < retry:
        try:
            val = _get_val_from_file(filename)
            if val == expected_val:
                return val
        except:
            pass
        count += 1
        await asyncio.sleep(0.1)
    return None
