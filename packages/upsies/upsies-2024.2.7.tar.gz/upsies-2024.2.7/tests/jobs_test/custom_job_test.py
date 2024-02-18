import asyncio
from unittest.mock import AsyncMock, call

import pytest

from upsies import errors
from upsies.jobs.custom import CustomJob


@pytest.fixture
def make_CustomJob(tmp_path):
    def make_CustomJob(**kwargs):
        return CustomJob(home_directory=tmp_path, cache_directory=tmp_path, **kwargs)
    return make_CustomJob


def test_name(make_CustomJob):
    job = make_CustomJob(name='foo', label='Foo', worker=AsyncMock())
    assert job.name == 'foo'


def test_label(make_CustomJob):
    job = make_CustomJob(name='foo', label='Foo', worker=AsyncMock())
    assert job.label == 'Foo'


def test_initialize(make_CustomJob):
    worker = AsyncMock()
    job = make_CustomJob(
        name='foo',
        label='Foo',
        worker=worker,
        catch=(TypeError, ValueError),
    )
    assert job._worker is worker
    assert job._expected_exceptions == (TypeError, ValueError)


@pytest.mark.asyncio
async def test_worker_raises_unexpected_exception(mocker, make_CustomJob):
    worker = AsyncMock(side_effect=RuntimeError('Oh no!'))
    job = make_CustomJob(name='foo', label='Foo', worker=worker, catch=(ValueError,))
    mocker.patch.object(job, 'error')

    job.start()
    with pytest.raises(RuntimeError, match=r'^Oh no!$'):
        await job.wait()

    assert worker.call_args_list == [call(job)]
    assert job.error.call_args_list == []
    assert job.output == ()
    assert job.is_finished is True
    assert job.exit_code == 1


@pytest.mark.asyncio
async def test_worker_raises_expected_exception(mocker, make_CustomJob):
    worker = AsyncMock(side_effect=errors.RequestError('Oh oh.'))
    job = make_CustomJob(name='foo', label='Foo', worker=worker, catch=(errors.RequestError,))
    mocker.patch.object(job, 'error')

    job.start()
    await job.wait()

    assert worker.call_args_list == [call(job)]
    assert job.error.call_args_list == [call(errors.RequestError('Oh oh.'))]
    assert job.output == ()
    assert job.is_finished is True
    assert job.exit_code == 1


@pytest.mark.asyncio
async def test_worker_returns_None(make_CustomJob, mocker):
    worker = AsyncMock(return_value=None)
    job = make_CustomJob(name='foo', label='Foo', worker=worker)
    mocker.patch.object(job, 'error')

    job.start()
    await job.wait()

    assert worker.call_args_list == [call(job)]
    assert job.error.call_args_list == []
    assert job.output == ()
    assert job.is_finished is True
    assert job.exit_code == 1


@pytest.mark.asyncio
async def test_worker_returns_iterable(make_CustomJob, mocker):
    worker = AsyncMock(return_value=('foo', 'bar', 'baz'))
    job = make_CustomJob(name='foo', label='Foo', worker=worker)
    mocker.patch.object(job, 'error')

    job.start()
    await job.wait()

    assert worker.call_args_list == [call(job)]
    assert job.error.call_args_list == []
    assert job.output == ('foo', 'bar', 'baz')
    assert job.is_finished is True
    assert job.exit_code == 0


@pytest.mark.parametrize('return_value', ('look at my work', ''))
@pytest.mark.asyncio
async def test_worker_returns_noniterable(return_value, make_CustomJob, mocker):
    worker = AsyncMock(return_value=return_value)
    job = make_CustomJob(name='foo', label='Foo', worker=worker)
    mocker.patch.object(job, 'error')

    job.start()
    await job.wait()

    assert worker.call_args_list == [call(job)]
    assert job.error.call_args_list == []
    assert job.output == (return_value,)
    assert job.is_finished is True
    assert job.exit_code == 0


@pytest.mark.asyncio
async def test_terminate_cancels_worker(make_CustomJob, mocker):
    async def delay(job):
        await asyncio.sleep(30)
        return 'sorry for being late'

    job = make_CustomJob(name='foo', label='Foo', worker=delay)
    mocker.patch.object(job, 'error')

    job.start()
    asyncio.get_running_loop().call_later(0.1, job.terminate)
    await job.wait()

    assert job.error.call_args_list == []
    assert job.output == ()
    assert job.exit_code == 1
    assert job.is_finished is True
