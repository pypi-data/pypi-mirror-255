import asyncio
import errno
import os
import re
from unittest.mock import AsyncMock, Mock, PropertyMock, call

import pytest

from upsies import errors
from upsies.jobs import JobBase
from upsies.uis import prompts
from upsies.utils import signal


class FooJob(JobBase):
    name = 'foo'
    label = 'Foo'

    def initialize(self):
        self.recorded_emissions = {}

        def make_emission_recorder(signal_name):
            def record_emission(*args, **kwargs):
                print(f'recording emission: {signal_name}:', args, kwargs)
                if signal_name not in self.recorded_emissions:
                    self.recorded_emissions[signal_name] = []
                self.recorded_emissions[signal_name].append(call(*args, **kwargs))

            return record_emission

        self.signal.register('running', make_emission_recorder('running'))
        self.signal.register('output', make_emission_recorder('output'))
        self.signal.register('info', make_emission_recorder('info'))
        self.signal.register('warning', make_emission_recorder('warning'))
        self.signal.register('error', make_emission_recorder('error'))
        self.signal.register('finished', make_emission_recorder('finished'))
        self.signal.register('prompt', make_emission_recorder('prompt'))
        self.signal.register('refresh_job_list', make_emission_recorder('refresh_job_list'))

    async def run(self):
        pass


@pytest.fixture
def job(tmp_path):
    return FooJob(home_directory=tmp_path, cache_directory=tmp_path)


@pytest.mark.parametrize(
    argnames='path, exp_exception',
    argvalues=(
        ('path/to/home', None),
        ('', None),
        (None, None),
        ('/root/upsies/test', errors.ContentError('/root/upsies/test: Permission denied')),
    ),
)
def test_home_directory_property(path, exp_exception, tmp_path):
    if path is None:
        job = FooJob()
        assert job.home_directory == ''
    else:
        job = FooJob(home_directory=tmp_path / path)
        if exp_exception:
            with pytest.raises(type(exp_exception), match=rf'^{re.escape(str(exp_exception))}$'):
                job.home_directory
        else:
            assert job.home_directory == tmp_path / path
            assert os.path.exists(job.home_directory)


@pytest.mark.parametrize('cache_directory_exists', (True, False))
@pytest.mark.parametrize(
    argnames='path',
    argvalues=(
        'path/to/cache',
        '',
        None,
    ),
)
def test_cache_directory_property(path, cache_directory_exists, tmp_path, mocker):
    mocker.patch('upsies.constants.DEFAULT_CACHE_DIRECTORY', tmp_path / 'default/cache/path')
    if not path:
        job = FooJob()
        assert job.cache_directory == tmp_path / 'default/cache/path'
    else:
        cache_directory = tmp_path / path
        if cache_directory_exists:
            cache_directory.mkdir(parents=True)

        job = FooJob(cache_directory=cache_directory)
        assert job.cache_directory == cache_directory
        assert os.path.exists(job.cache_directory)


@pytest.mark.parametrize(
    argnames='ignore_cache, exp_ignore_cache',
    argvalues=(
        (False, False),
        (True, True),
        ('', False),
        (1, True),
    ),
)
def test_ignore_cache_property(ignore_cache, exp_ignore_cache, tmp_path):
    job = FooJob(home_directory=tmp_path, cache_directory=tmp_path, ignore_cache=ignore_cache)
    assert job.ignore_cache is exp_ignore_cache


@pytest.mark.parametrize(
    argnames='no_output_is_ok, exp_no_output_is_ok',
    argvalues=(
        (False, False),
        (True, True),
        (0, False),
        ('maybe', True),
    ),
)
def test_no_output_is_ok_property(no_output_is_ok, exp_no_output_is_ok, tmp_path):
    job = FooJob(home_directory=tmp_path, cache_directory=tmp_path, no_output_is_ok=no_output_is_ok)
    assert job.no_output_is_ok is exp_no_output_is_ok


@pytest.mark.parametrize(
    argnames='hidden, exp_hidden',
    argvalues=(
        (False, False),
        (True, True),
        ('', False),
        ('yup', True),
        (lambda: False, False),
        (lambda: True, True),
        (lambda: 0, False),
        (lambda: 1, True),
    ),
)
def test_hidden_property(hidden, exp_hidden, tmp_path):
    job = FooJob(home_directory=tmp_path, cache_directory=tmp_path, hidden=hidden)
    assert job.hidden is exp_hidden

    job.hidden = 0
    assert job.hidden is False

    job.hidden = 1
    assert job.hidden is True

    job.hidden = Mock(return_value='')
    assert job.hidden is False

    job.hidden = Mock(return_value='ok')
    assert job.hidden is True


def test_kwargs_property(tmp_path):
    class BarJob(FooJob):
        def initialize(self, *, foo='FOO', bar='BAR'):
            pass

    assert BarJob(home_directory=tmp_path, cache_directory=tmp_path, foo='a').kwargs == {'foo': 'a'}
    assert BarJob(home_directory=tmp_path, cache_directory=tmp_path, bar='a').kwargs == {'bar': 'a'}
    assert BarJob(home_directory=tmp_path, cache_directory=tmp_path, foo='a', bar='b').kwargs == {'foo': 'a', 'bar': 'b'}


@pytest.mark.parametrize(
    argnames='autostart, exp_autostart',
    argvalues=(
        (False, False),
        (True, True),
        (0, False),
        (1, True),
    ),
)
def test_autostart_property(autostart, exp_autostart, tmp_path):
    job = FooJob(home_directory=tmp_path, cache_directory=tmp_path, autostart=autostart)
    assert job.autostart is exp_autostart


precondition_test_cases = pytest.mark.parametrize(
    argnames='precondition, exp_exception',
    argvalues=(
        (Mock(), None),
        ('foo', TypeError("Not callable: 'foo'")),
        ('', TypeError("Not callable: ''")),
        (True, TypeError("Not callable: True")),
        (False, TypeError("Not callable: False")),
    ),
)

@precondition_test_cases
def test_precondition_argument(precondition, exp_exception, tmp_path):
    if exp_exception:
        with pytest.raises(type(exp_exception), match=rf'^{re.escape(str(exp_exception))}$'):
            FooJob(home_directory=tmp_path, cache_directory=tmp_path, precondition=precondition)
    else:
        job = FooJob(home_directory=tmp_path, cache_directory=tmp_path, precondition=precondition)
        assert job.precondition is precondition


@pytest.mark.parametrize(
    argnames='was_started, exp_RuntimeError',
    argvalues=(
        (False, None),
        (True, RuntimeError('Cannot set precondition after job has been started')),
    ),
)
@precondition_test_cases
def test_precondition_property(precondition, exp_exception, was_started, exp_RuntimeError, tmp_path, mocker):
    job = FooJob(home_directory=tmp_path, cache_directory=tmp_path)
    mocker.patch.object(type(job), 'was_started', PropertyMock(return_value=was_started))
    if exp_RuntimeError:
        with pytest.raises(type(exp_RuntimeError), match=rf'^{re.escape(str(exp_RuntimeError))}$'):
            job.precondition = precondition
    elif exp_exception:
        with pytest.raises(type(exp_exception), match=rf'^{re.escape(str(exp_exception))}$'):
            job.precondition = precondition
    else:
        job.precondition = precondition
        assert job.precondition is precondition


@pytest.mark.parametrize(
    argnames='was_started, exp_RuntimeError',
    argvalues=(
        (False, None),
        (True, RuntimeError('Cannot set prejobs after job has been started')),
    ),
)
def test_prejobs_property(was_started, exp_RuntimeError, job, mocker):
    assert isinstance(job.prejobs, tuple)
    assert job.prejobs is job._prejobs

    mocker.patch.object(type(job), 'was_started', PropertyMock(return_value=was_started))
    if exp_RuntimeError:
        with pytest.raises(type(exp_RuntimeError), match=rf'^{re.escape(str(exp_RuntimeError))}$'):
            job.prejobs = [1, 2, 3]
    else:
        job.prejobs = [1, 2, 3]
        assert job.prejobs == (1, 2, 3)


@pytest.mark.parametrize(
    argnames='presignals, emissions, exp_is_enabled_after_all_emissions',
    argvalues=(
        (
            [],
            [],
            True,
        ),
        (
            [],
            [
                {'emission': ('info', 'Info.'), 'exp_is_enabled': True, 'refresh_job_list_calls': []},
            ],
            True,
        ),
        (
            ['info'],
            [
                {'emission': ('output', 'Output.'), 'exp_is_enabled': False, 'refresh_job_list_calls': []},
                {'emission': ('info', 'Info.'), 'exp_is_enabled': True, 'refresh_job_list_calls': [call()]},
                {'emission': ('warning', 'Warning.'), 'exp_is_enabled': True, 'refresh_job_list_calls': []},
            ],
            True,
        ),
        (
            ['info', 'output'],
            [
                {'emission': ('output', 'Output 1.'), 'exp_is_enabled': False, 'refresh_job_list_calls': []},
                {'emission': ('warning', 'Warning 1.'), 'exp_is_enabled': False, 'refresh_job_list_calls': []},
                {'emission': ('output', 'Output 2.'), 'exp_is_enabled': False, 'refresh_job_list_calls': []},
                {'emission': ('info', 'Info 1.'), 'exp_is_enabled': True, 'refresh_job_list_calls': [call()]},
                {'emission': ('warning', 'Warning 2.'), 'exp_is_enabled': True, 'refresh_job_list_calls': []},
            ],
            True,
        ),
        (
            ['info', 'output'],
            [
                {'emission': ('output', 'Output 1.'), 'exp_is_enabled': False, 'refresh_job_list_calls': []},
                {'emission': ('warning', 'Warning 1.'), 'exp_is_enabled': False, 'refresh_job_list_calls': []},
                {'emission': ('output', 'Output 2.'), 'exp_is_enabled': False, 'refresh_job_list_calls': []},
                {'emission': ('warning', 'Warning 2.'), 'exp_is_enabled': False, 'refresh_job_list_calls': []},
            ],
            False,
        ),
    ),
)
def test_presignal(presignals, emissions, exp_is_enabled_after_all_emissions, job):
    job_list_refreshed = Mock()
    job.signal.register('refresh_job_list', job_list_refreshed)

    class BarJob(JobBase):
        name = 'bar'
        label = 'Bar'

        async def run(self):
            pass

    other_job = BarJob()

    for presignal in presignals:
        job.presignal(other_job, presignal)

    # Check registered presignals
    if presignals:
        assert dict(job.presignals) == {
            other_job: {ps: False for ps in presignals}
        }
    else:
        assert dict(job.presignals) == {}

    assert job.is_enabled is (False if presignals else True)

    # Emit emissions in random order
    for state in emissions:
        signal, payload = state['emission']
        other_job.signal.emit(signal, payload)

        assert job.is_enabled is state['exp_is_enabled']

        assert job_list_refreshed.call_args_list == state['refresh_job_list_calls']
        job_list_refreshed.reset_mock()

    assert job.is_enabled is exp_is_enabled_after_all_emissions

    # Check registered presignals
    emitted_signals = list(set(
        state['emission'][0]
        for state in emissions
        if state['emission'][0] in presignals
    ))
    if presignals:
        exp_presignals = {
            other_job: {ps: ps in emitted_signals for ps in presignals}
        }
    else:
        exp_presignals = {}
    assert dict(job.presignals) == dict(exp_presignals)

@pytest.mark.parametrize(
    argnames='was_started, exp_RuntimeError',
    argvalues=(
        (False, None),
        (True, RuntimeError('Cannot set presignal after job has been started')),
    ),
)
def test_presignal_after_job_was_started(was_started, exp_RuntimeError, job, mocker):
    class BarJob(JobBase):
        name = 'bar'
        label = 'Bar'

        async def run(self):
            pass

    other_job = BarJob()

    mocker.patch.object(type(job), 'was_started', PropertyMock(return_value=was_started))
    if exp_RuntimeError:
        with pytest.raises(type(exp_RuntimeError), match=rf'^{re.escape(str(exp_RuntimeError))}$'):
            job.presignal(other_job, 'finished')
    else:
        job.presignal(other_job, 'finished')


@pytest.mark.parametrize(
    argnames='precondition, prejobs, exp_is_enabled',
    argvalues=(
        (Mock(return_value=True), (Mock(is_finished=True, is_enabled=True), Mock(is_finished=True, is_enabled=True)), True),
        (Mock(return_value=False), (Mock(is_finished=True, is_enabled=True), Mock(is_finished=True, is_enabled=True)), False),

        (Mock(return_value=True), (Mock(is_finished=True, is_enabled=True), Mock(is_finished=True, is_enabled=False)), True),
        (Mock(return_value=True), (Mock(is_finished=True, is_enabled=True), Mock(is_finished=False, is_enabled=True)), False),
        (Mock(return_value=True), (Mock(is_finished=True, is_enabled=True), Mock(is_finished=False, is_enabled=False)), True),

        (Mock(return_value=True), (Mock(is_finished=True, is_enabled=False), Mock(is_finished=True, is_enabled=True)), True),
        (Mock(return_value=True), (Mock(is_finished=False, is_enabled=True), Mock(is_finished=True, is_enabled=True)), False),
        (Mock(return_value=True), (Mock(is_finished=False, is_enabled=False), Mock(is_finished=True, is_enabled=True)), True),
    ),
)
def test_is_enabled_property(precondition, prejobs, exp_is_enabled, tmp_path):
    job = FooJob(
        home_directory=tmp_path,
        cache_directory=tmp_path,
        precondition=precondition,
        prejobs=prejobs,
    )
    assert job.is_enabled is exp_is_enabled


def test_signal_property(job):
    assert isinstance(job.signal, signal.Signal)
    assert set(job.signal.signals) == {
        'running',
        'output',
        'info',
        'warning',
        'error',
        'finished',
        'prompt',
        'refresh_job_list',
    }
    assert set(job.signal.recording) == {'output'}


def test_initialize_is_called_after_object_creation(tmp_path):
    class BarJob(FooJob):
        initialize_was_called = False

        def initialize(self):
            self.initialize_was_called = True
            # Assert some properties exist that are created in __init__()
            assert self.home_directory
            assert self.signal

    job = BarJob(home_directory=tmp_path, cache_directory=tmp_path)
    assert job.initialize_was_called


def test_callbacks_argument(tmp_path):
    class BarJob(FooJob):
        def initialize(self):
            self.signal.add('greeted')

    cb = Mock()
    job = BarJob(
        home_directory=tmp_path,
        cache_directory=tmp_path,
        callbacks={
            'output': cb.output,
            'finished': cb.finished,
            'greeted': (cb.hello, cb.hey),
        },
    )
    assert cb.output in job.signal.signals['output']
    assert cb.finished in job.signal.signals['finished']
    assert cb.hello in job.signal.signals['greeted']
    assert cb.hey in job.signal.signals['greeted']


def test_presignals_argument(mocker):
    class BarJob(FooJob):
        def initialize(self):
            self.signal.add('a')
            self.signal.add('b')
            self.signal.add('c')

    class BazJob(FooJob):
        def initialize(self):
            self.signal.add('baz')

    mocker.patch('upsies.jobs.base.JobBase.presignal')

    presignals = {
        BarJob(): ['a', 'c'],
        BazJob(): ['baz'],
    }
    job = BarJob(presignals=presignals)
    assert job.presignal.call_args_list == [
        call(job, signal)
        for job, signals in presignals.items()
        for signal in signals
    ]


def test_start_does_nothing_if_job_is_not_enabled(job, mocker):
    mocker.patch.object(type(job), 'is_enabled', PropertyMock(return_value=False))
    mocks = Mock()
    mocks.attach_mock(mocker.patch.object(job, '_read_cache', return_value=False), '_read_cache')
    mocks.attach_mock(mocker.patch.object(job, '_finish'), '_finish')
    mocks.attach_mock(mocker.patch.object(job, 'run', Mock()), 'run')
    mocks.attach_mock(mocker.patch.object(job, '_add_task'), '_add_task')
    job.start()
    assert job.was_started is False
    assert job._run_was_called is False
    assert mocks.mock_calls == []

def test_start_is_called_multiple_times(job, mocker):
    mocks = Mock()
    mocks.attach_mock(mocker.patch.object(job, '_read_cache', return_value=True), '_read_cache')
    mocks.attach_mock(mocker.patch.object(job, '_finish'), '_finish')
    mocks.attach_mock(mocker.patch.object(job, 'run', Mock()), 'run')
    mocks.attach_mock(mocker.patch.object(job, '_add_task'), '_add_task')
    job.start()
    for _ in range(3):
        with pytest.raises(RuntimeError, match=rf'^start\(\) was already called: {job.name}$'):
            job.start()

def test_start_reads_cache(job, mocker):
    mocks = Mock()
    mocks.attach_mock(mocker.patch.object(job, '_read_cache', return_value=True), '_read_cache')
    mocks.attach_mock(mocker.patch.object(job, '_finish'), '_finish')
    mocks.attach_mock(mocker.patch.object(job, 'run', Mock()), 'run')
    mocks.attach_mock(mocker.patch.object(job, '_add_task'), '_add_task')
    job.start()
    assert job.was_started is True
    assert job._run_was_called is False
    assert mocks.mock_calls == [
        call._read_cache(),
        call._finish()
    ]

def test_start_calls_run(job, mocker):
    mocks = Mock()
    mocks.attach_mock(mocker.patch.object(job, '_read_cache', return_value=False), '_read_cache')
    mocks.attach_mock(mocker.patch.object(job, '_finish'), '_finish')
    mocks.attach_mock(mocker.patch.object(job, 'run', Mock()), 'run')
    mocks.attach_mock(mocker.patch.object(job, '_add_task'), '_add_task')
    job.start()
    assert job.was_started is True
    assert job._run_was_called is True
    assert mocks.mock_calls == [
        call._read_cache(),
        call.run(),
        call._add_task(job.run.return_value),
    ]


def test_was_started_property(job, mocker):
    obj = object()
    mocker.patch.object(job, '_was_started', obj)
    assert job.was_started is obj


@pytest.mark.parametrize(
    argnames='was_started, is_finished, exp_exception',
    argvalues=(
        (True, True, RuntimeError('Do not call add_task if job is already finished: {job_name}')),
        (True, False, None),
        (False, False, RuntimeError('Do not call add_task before job is started: {job_name}')),
    ),
    ids=lambda v: repr(v),
)
@pytest.mark.asyncio
async def test_add_task(was_started, is_finished, exp_exception, job, mocker):
    mocker.patch.object(type(job), 'was_started', PropertyMock(return_value=was_started))
    mocker.patch.object(type(job), 'is_finished', PropertyMock(return_value=is_finished))
    mocker.patch.object(job, '_add_task')

    if exp_exception:
        msg = str(exp_exception).format(job_name=job.name)
        with pytest.raises(type(exp_exception), match=rf'^{re.escape(msg)}$'):
            job.add_task('mock coroutine', callback='mock callback')

    else:
        task = job.add_task('mock coroutine', callback='mock callback')
        assert task is job._add_task.return_value
        assert job._add_task.call_args_list == [call('mock coroutine', callback='mock callback')]

@pytest.mark.asyncio
async def test__add_task_calls_run_task(job):
    job.start()
    try:
        coro = AsyncMock()()
        task = job._add_task(coro)
        assert isinstance(task, asyncio.Task), task
        assert job._tasks[-1] == task
    finally:
        await job.wait()

@pytest.mark.asyncio
async def test__add_task_catches_exceptions_from_coro(job):
    job.start()
    callback = Mock()
    exception = TypeError('foo')
    coro = AsyncMock(side_effect=exception)()
    job.add_task(coro, callback=callback)
    with pytest.raises(type(exception), match=rf'^{re.escape(str(exception))}$'):
        await job.wait()
    assert job.is_finished
    assert isinstance(job.raised, type(exception))
    assert str(job.raised) == str(exception)
    assert callback.call_args_list == [call(exception)]
    assert job.recorded_emissions == {
        'running': [call(job)],
        'finished': [call(job)],
    }

@pytest.mark.asyncio
async def test__add_task_does_not_call_callback_if_task_was_cancelled(job):
    job.start()
    callback = Mock()
    coro = AsyncMock()()
    task = job.add_task(coro, callback=callback)
    task.cancel()
    await job.wait()
    assert job.is_finished
    assert job.raised is None
    assert callback.call_args_list == []
    assert job.recorded_emissions == {
        'running': [call(job)],
        'finished': [call(job)],
    }

@pytest.mark.asyncio
async def test__add_task_catches_exceptions_from_callback(job):
    job.start()
    exception = TypeError('foo')
    callback = Mock(side_effect=exception)
    coro = AsyncMock(return_value='bar')()
    job.add_task(coro, callback=callback)
    with pytest.raises(type(exception), match=rf'^{re.escape(str(exception))}$'):
        await job.wait()
    assert job.is_finished
    assert isinstance(job.raised, type(exception))
    assert str(job.raised) == str(exception)
    assert callback.call_args_list == [call('bar')]
    assert job.recorded_emissions == {
        'running': [call(job)],
        'finished': [call(job)],
    }

@pytest.mark.asyncio
async def test__add_task_catches_exceptions_from_callback_wrapper(job, mocker):
    job.start()
    exception = TypeError('foo')
    mocker.patch.object(job, '_finish', side_effect=exception)
    job.add_task(AsyncMock()())
    with pytest.raises(type(exception), match=rf'^{re.escape(str(exception))}$'):
        await job.wait()
    assert job.is_finished
    assert isinstance(job.raised, type(exception))
    assert str(job.raised) == str(exception)

@pytest.mark.asyncio
async def test__add_task_removes_each_task_when_it_is_done(job, mocker):
    coros = Mock()

    def delayed_coro(name, delay):
        async def coro():
            await asyncio.sleep(delay)
            return name

        coro_func = AsyncMock(name=name, side_effect=coro)
        coros.attach_mock(coro_func, name)
        return coro_func()

    def make_callback(exp_result, exp_tasks_len_after_finished):
        def callback(result):
            print('Callback called:', exp_result)
            assert result == exp_result
            assert len(job._tasks) == exp_tasks_len_after_finished
            assert job.raised is None
            if exp_tasks_len_after_finished == 0:
                assert job.is_finished
                assert job.recorded_emissions == {
                    'running': [call(job)],
                    'finished': [call(job)],
                }
            else:
                assert not job.is_finished
                assert job.recorded_emissions == {
                    'running': [call(job)],
                }

        return callback

    job.start()
    job.add_task(
        delayed_coro('foo', delay=0.3),
        callback=make_callback(exp_result='foo', exp_tasks_len_after_finished=0),
    )
    job.add_task(
        delayed_coro('bar', delay=0.2),
        callback=make_callback(exp_result='bar', exp_tasks_len_after_finished=1),
    )
    job.add_task(
        delayed_coro('baz', delay=0.1),
        callback=make_callback(exp_result='baz', exp_tasks_len_after_finished=2),
    )
    # 3 tasks added by us + 1 run() task = 4
    assert len(job._tasks) == 4
    await job.wait()
    assert job.is_finished
    assert job.raised is None
    assert coros.mock_calls == [
        call.foo(),
        call.bar(),
        call.baz(),
    ]
    assert job.recorded_emissions == {
        'running': [call(job)],
        'finished': [call(job)],
    }

@pytest.mark.parametrize(
    argnames='finalize_event, exp_is_finished',
    argvalues=(
        (Mock(is_set=Mock(return_value=False)), False),
        (Mock(is_set=Mock(return_value=True)), True),
        (None, True),
    ),
    ids=(
        'job is not finalized',
        'job is finalized',
        'no finalization',
    ),
)
@pytest.mark.asyncio
async def test__add_task_callback_does_finish_job(
        finalize_event, exp_is_finished,
        job, mocker,
):
    if finalize_event:
        finalize_event.wait = AsyncMock()

    job.start()
    mocker.patch.object(job, '_finalize_event', finalize_event)
    job.add_task(AsyncMock()())
    await job.wait()
    assert job.is_finished is exp_is_finished


@pytest.mark.parametrize(
    argnames='was_started, is_finished, exp_exception',
    argvalues=(
        (False, False, RuntimeError('Do not call add_prompt before job is started: {job.name}')),
        (True, False, None),
        (True, True, RuntimeError('Do not call add_prompt if job is already finished: {job.name}')),
    ),
    ids=lambda v: repr(v),
)
@pytest.mark.asyncio
async def test_add_prompt(
        was_started, is_finished, exp_exception,
        job, mocker,
):
    if was_started:
        job.start()
    if is_finished:
        job.terminate()
        await job.wait()

    mocks = Mock()
    mocks.attach_mock(mocker.patch.object(job, 'add_task'), 'add_task')
    mocks.attach_mock(mocker.patch.object(job.signal, 'emit'), 'emit')

    class MyPrompt(prompts.Prompt):
        wait = mocks.prompt.wait

    prompt = MyPrompt()

    if exp_exception:
        exp_msg = str(exp_exception).format(job=job)
        with pytest.raises(type(exp_exception), match=rf'^{re.escape(exp_msg)}$'):
            job.add_prompt(prompt)
        assert mocks.mock_calls == []
    else:
        job.add_prompt(prompt)
        assert mocks.mock_calls == [
            call.prompt.wait(),
            call.add_task(prompt.wait.return_value),
            call.emit('prompt', prompt),
        ]

@pytest.mark.asyncio
async def test_add_prompt_gets_bad_prompt_object(job, mocker):
    job.start()

    mocks = Mock()
    mocks.attach_mock(mocker.patch.object(job, 'add_task'), 'add_task')
    mocks.attach_mock(mocker.patch.object(job.signal, 'emit'), 'emit')

    prompt = 'this is not a prompt'
    with pytest.raises(AssertionError, match=r"^Not a Prompt instance: 'this is not a prompt'$"):
        job.add_prompt(prompt)
    assert mocks.mock_calls == []


@pytest.mark.asyncio
async def test_wait_is_called_before_job_is_started(job):
    with pytest.raises(RuntimeError, match=r'^Do not call wait before job is started: foo$'):
        await job.wait()


@pytest.mark.parametrize('finalize_task_id', (None, 1, 3), ids=lambda id: f'finalizer_task_id={id}')
@pytest.mark.parametrize(
    argnames='bad_task_ids, exception_type, exp_exception',
    argvalues=(
        ([], None, None),
        ([9, 3, 6], TypeError, TypeError('3: Raisin!')),
        ([1, 4, 2], asyncio.CancelledError, None),
    ),
    ids=lambda v: repr(v),
)
@pytest.mark.asyncio
async def test_wait_gathers_tasks(bad_task_ids, exception_type, exp_exception, finalize_task_id, job):
    tasks = []
    task_id = 0

    async def do_something(subtasks_count):
        nonlocal task_id
        task_id += 1

        if task_id == finalize_task_id:
            job.finalize()

        if task_id in bad_task_ids:
            raise exception_type(f'{task_id}: Raisin!')

        await asyncio.sleep(task_id / 100)
        add_tasks(subtasks_count)

    def add_tasks(count):
        if count > 0:
            for i in range(count):
                task = job.add_task(do_something(count - 1))
                tasks.append(task)

    job.start()

    if finalize_task_id:
        job.add_task(job.finalization())

    add_tasks(3)
    if exp_exception:
        with pytest.raises(type(exp_exception), match=rf'^{re.escape(str(exp_exception))}$'):
            await job.wait()
    else:
        await job.wait()

    assert job._tasks == []
    if finalize_task_id:
        assert job._finalize_event.is_set()
    else:
        assert job._finalize_event is None

    for task in tasks:
        assert task.done()


@pytest.mark.parametrize(
    argnames='is_finished, emitted, exp_exception',
    argvalues=(
        (
            False,
            [],
            AssertionError('Job is not finished yet: self._finalize_event=None, self._tasks=[]'),
        ),
        (
            True,
            [('finished', {'args': 'finished args', 'kwargs': 'finished kwargs'})],
            AssertionError("\"finished\" signal was already emitted: {'args': 'finished args', 'kwargs': 'finished kwargs'}"),
        ),
        (
            True,
            [],
            None,
        ),
    ),
    ids=lambda v: repr(v),
)
def test__finish(is_finished, emitted, exp_exception, job, mocker):
    mocker.patch.object(type(job), 'is_finished', PropertyMock(return_value=is_finished))
    mocker.patch.object(type(job.signal), 'emitted', PropertyMock(return_value=emitted))
    mocks = Mock()
    mocks.attach_mock(mocker.patch.object(job.signal, 'emit'), 'emit')
    mocks.attach_mock(mocker.patch.object(job, '_write_cache'), '_write_cache')

    if exp_exception:
        with pytest.raises(type(exp_exception), match=rf'^{re.escape(str(exp_exception))}$'):
            job._finish()
        assert mocks.mock_calls == []
    else:
        job._finish()
        assert mocks.mock_calls == [
            call.emit('finished', job),
            call._write_cache(),
        ]


@pytest.mark.parametrize('finalize_event', (None, Mock()), ids=('finalizing', 'not finalizing'))
def test_terminate(finalize_event, job, mocker):
    mocks = Mock()
    mocker.patch.object(job, '_finalize_event', finalize_event)
    mocks.attach_mock(mocker.patch.object(job, 'finalize'), 'finalize')
    mocker.patch.object(job, '_tasks', [
        mocks.task1,
        mocks.task2,
        mocks.task3,
    ])

    job.terminate()

    exp_mock_calls = [
        call.task1.cancel(),
        call.task2.cancel(),
        call.task3.cancel(),
    ]
    if finalize_event:
        exp_mock_calls.append(call.finalize())
    assert mocks.mock_calls == exp_mock_calls

@pytest.mark.parametrize(
    argnames='cancelling_task_id, exp_gracefully_finished_tasks',
    argvalues=(
        (1, [1]),
        (2, [2]),
        (3, [3]),
    ),
    ids=lambda v: repr(v),
)
@pytest.mark.asyncio
async def test_terminate_is_called_from_added_task(cancelling_task_id, exp_gracefully_finished_tasks, job, mocker):
    gracefully_finished_tasks = []

    async def do_something(task_id):
        if task_id == cancelling_task_id:
            print(f'{task_id}: cancelling')
            job.terminate()

        print(f'{task_id}: sleeping {task_id / 100} seconds')
        await asyncio.sleep(task_id / 100)

        print(f'{task_id}: ending gracefully')
        gracefully_finished_tasks.append(task_id)

    job.start()
    job.add_task(do_something(1))
    job.add_task(do_something(2))
    job.add_task(do_something(3))
    await job.wait()

    assert gracefully_finished_tasks == exp_gracefully_finished_tasks

@pytest.mark.parametrize(
    argnames='current_task_exception, exp_exception',
    argvalues=(
        (None, None),
        (RuntimeError('no running event loop'), None),
        (RuntimeError('No running event loop!1!!'), None),
        (RuntimeError('something else'), RuntimeError('something else')),
    ),
    ids=lambda v: repr(v),
)
@pytest.mark.asyncio
async def test_terminate_gracefully_fails_to_get_current_task(current_task_exception, exp_exception, job, mocker):
    job._tasks = [Mock(), Mock(), Mock()]
    mocker.patch('asyncio.current_task', Mock(side_effect=current_task_exception))

    if exp_exception:
        with pytest.raises(type(exp_exception), match=rf'^{re.escape(str(exp_exception))}$'):
            job.terminate()
    else:
        job.terminate()


@pytest.mark.parametrize(
    argnames='finalize_event, is_set',
    argvalues=(
        (None, None),
        (asyncio.Event(), False),
        (asyncio.Event(), True),
    ),
    ids=(
        'finalizing',
        'not finalizing',
        'already finalized',
    ),
)
def test_finalize(finalize_event, is_set, job, mocker):
    mocker.patch.object(job, '_finalize_event', finalize_event)
    if is_set:
        job._finalize_event.set()

    job.finalize()

    assert job._finalize_event is not None
    assert job._finalize_event.is_set() is True


@pytest.mark.parametrize('finalizing', (True, False), ids=('finalizing', 'not finalizing'))
@pytest.mark.asyncio
async def test_finalization(finalizing, job, mocker):
    mocker.patch('asyncio.Event.wait', AsyncMock())
    if finalizing:
        mocker.patch.object(job, '_finalize_event', asyncio.Event())

    await job.finalization()

    assert job._finalize_event.wait.call_args_list == [call()]


@pytest.mark.parametrize(
    argnames='was_started, tasks, finalize_event, exp_is_finished',
    argvalues=(
        (False, None, None, None),
        (True, ['mock task'], None, False),
        (True, [], None, True),
        (True, [], Mock(is_set=Mock(return_value=False)), False),
        (True, [], Mock(is_set=Mock(return_value=True)), True),
    ),
    ids=(
        'not started',
        'tasks running',
        'not waiting for finalize()',
        'finalize() not called yet',
        'finalize() called',
    ),
)
@pytest.mark.asyncio
async def test_is_finished(was_started, tasks, finalize_event, exp_is_finished, job, mocker):
    mocker.patch.object(type(job), 'was_started', PropertyMock(return_value=was_started))
    mocker.patch.object(job, '_tasks', tasks)
    mocker.patch.object(job, '_finalize_event', finalize_event)

    assert job.is_finished is exp_is_finished


@pytest.mark.parametrize('is_finished', (True, False))
@pytest.mark.parametrize(
    argnames='errors, raised, output, no_output_is_ok, exp_exit_code',
    argvalues=(
        (['Something went wrong'], [], ['Some output'], False, 1),
        ([], [Exception('Something went really bad')], ['Some output'], False, 1),
        ([], [], ['Some output'], False, 0),
        ([], [], [], False, 1),
        ([], [], [], True, 0),
    ),
    ids=lambda v: str(v),
)
def test_exit_code(
        is_finished, errors, raised, output, no_output_is_ok,
        exp_exit_code,
        job, mocker,
):
    mocker.patch.object(type(job), 'is_finished', PropertyMock(return_value=is_finished))
    mocker.patch.object(type(job), 'errors', PropertyMock(return_value=errors))
    mocker.patch.object(type(job), 'raised', PropertyMock(return_value=raised))
    mocker.patch.object(type(job), 'output', PropertyMock(return_value=output))
    mocker.patch.object(type(job), 'no_output_is_ok', PropertyMock(return_value=no_output_is_ok))

    if not is_finished:
        assert job.exit_code is None
    else:
        assert job.exit_code is exp_exit_code


@pytest.mark.asyncio
async def test_send_on_unstarted_job(job):
    assert job.is_finished is None
    with pytest.raises(RuntimeError, match='^Do not call send before job is started: foo$'):
        job.send('bar')

@pytest.mark.asyncio
async def test_send_on_finished_job(job):
    job.start()
    await job.wait()
    assert job.is_finished
    with pytest.raises(RuntimeError, match='^Do not call send if job is already finished: foo$'):
        job.send('bar')

@pytest.mark.asyncio
async def test_send_emits_output_signal(job, mocker):
    cb = Mock()
    job.signal.register('output', cb)
    job.start()
    job.add_task(job.finalization())

    job.send('foo')
    assert job.output == ('foo',)
    assert cb.call_args_list == [call('foo')]

    job.send('bar')
    assert job.output == ('foo', 'bar')
    assert cb.call_args_list == [call('foo'), call('bar')]

    job.send('baz')
    assert job.output == ('foo', 'bar', 'baz')
    assert cb.call_args_list == [call('foo'), call('bar'), call('baz')]

    job.finalize()
    await job.wait()
    assert job.is_finished


def test_output(job):
    assert job.output == ()
    job._output = ['foo', 'bar', 'baz']
    assert job.output == ('foo', 'bar', 'baz')


def test_info(job):
    cb = Mock()
    job.signal.register('info', cb)

    job.info = 'foo'
    assert job.info == 'foo'
    assert cb.call_args_list == [call('foo')]

    job.info = 'bar'
    assert job.info == 'bar'
    assert cb.call_args_list == [call('foo'), call('bar')]

    job.info = 'baz'
    assert job.info == 'baz'
    assert cb.call_args_list == [call('foo'), call('bar'), call('baz')]


def test_warn_and_warnings(job):
    cb = Mock()
    job.signal.register('warning', cb)

    job.warn('foo')
    assert job.warnings == ('foo',)
    assert cb.call_args_list == [call('foo')]

    job.warn('bar')
    assert job.warnings == ('foo', 'bar')
    assert cb.call_args_list == [call('foo'), call('bar')]

    job.warn('baz')
    assert job.warnings == ('foo', 'bar', 'baz')
    assert cb.call_args_list == [call('foo'), call('bar'), call('baz')]


def test_clear_warnings(job):
    for msg in ['foo', 'bar', 'baz']:
        job.warn(msg)
    assert job.warnings == ('foo', 'bar', 'baz')
    job.clear_warnings()
    assert job.warnings == ()


def test_error_and_errors(job, mocker):
    mocker.patch.object(job, 'terminate')
    cb = Mock()
    job.signal.register('error', cb)

    assert job.terminate.call_args_list == []
    job.error('foo')
    assert job.terminate.call_args_list == [call()]
    assert job.errors == ('foo',)
    assert cb.call_args_list == [call('foo')]

    job.error('bar')
    assert job.terminate.call_args_list == [call(), call()]
    assert job.errors == ('foo', 'bar')
    assert cb.call_args_list == [call('foo'), call('bar')]

    job.error('baz')
    assert job.terminate.call_args_list == [call(), call(), call()]
    assert job.errors == ('foo', 'bar', 'baz')
    assert cb.call_args_list == [call('foo'), call('bar'), call('baz')]


@pytest.mark.asyncio
async def test_exception_and_raised(job, mocker):
    mocker.patch.object(job, 'terminate')

    # Falsy `exception` argument is ignored
    exception = None
    job.exception(exception)
    assert job.raised is None
    assert job.terminate.call_args_list == []

    exception = TypeError('Sorry, not my type.')
    job.exception(exception)
    assert job.raised is exception
    assert job.terminate.call_args_list == [call()]

    # Further exceptions are ignored
    job.exception(ValueError('Another exception'))
    assert job.raised is exception
    assert job.terminate.call_args_list == [call()]


@pytest.mark.parametrize(
    argnames='run_was_called, emissions, exit_code, cache_file',
    argvalues=(
        (False, (('output', {'args': ('foo',), 'kwargs': {'bar': 'baz'}}),), 0, 'path/to/cache_file'),
        (True, (), 0, 'path/to/cache_file'),
        (True, (('output', {'args': ('foo',), 'kwargs': {'bar': 'baz'}}),), 1, 'path/to/cache_file'),
        (True, (('output', {'args': ('foo',), 'kwargs': {'bar': 'baz'}}),), 0, ''),
        (True, (('output', {'args': ('foo',), 'kwargs': {'bar': 'baz'}}),), 0, None),
    ),
)
def test__write_cache_does_nothing(emissions, exit_code, cache_file, run_was_called, job, mocker):
    mocker.patch.object(type(job.signal), 'emissions', PropertyMock(return_value=emissions))
    mocker.patch.object(type(job), 'exit_code', PropertyMock(return_value=exit_code))
    mocker.patch.object(type(job), 'cache_file', PropertyMock(return_value=cache_file))
    mocker.patch.object(job, '_run_was_called', run_was_called)
    open_mock = mocker.patch('upsies.jobs.base.open')
    job._write_cache()
    assert open_mock.call_args_list == []

def test__write_cache_writes_signal_emissions(job, mocker, tmp_path):
    mocker.patch.object(job, '_run_was_called', True)
    mocker.patch.object(type(job.signal), 'emissions', PropertyMock(return_value='emissions mock'))
    mocker.patch.object(type(job), 'exit_code', PropertyMock(return_value=0))
    cache_file = tmp_path / 'cache.file'
    mocker.patch.object(type(job), 'cache_file', PropertyMock(return_value=str(cache_file)))

    job._write_cache()
    serialized_emissions = open(job.cache_file, 'rb').read()
    assert job._deserialize_cached(serialized_emissions) == 'emissions mock'

def test__write_cache_fails_to_write_cache_file(job, mocker, tmp_path):
    mocker.patch.object(job, '_run_was_called', True)
    mocker.patch.object(type(job.signal), 'emissions', PropertyMock(return_value='emissions mock'))
    mocker.patch.object(type(job), 'exit_code', PropertyMock(return_value=0))
    cache_file = tmp_path / 'cache.file'
    mocker.patch.object(type(job), 'cache_file', PropertyMock(return_value=str(cache_file)))
    cache_file.write_bytes(b'existing cached data')
    cache_file.chmod(0o000)
    try:
        with pytest.raises(RuntimeError, match=(
                rf'^Unable to write cache {re.escape(job.cache_file)}: Permission denied$'
        )):
            job._write_cache()
    finally:
        cache_file.chmod(0o200)


@pytest.mark.parametrize(
    argnames='ignore_cache, cache_file, cache_file_exists',
    argvalues=(
        (True, 'path/to/cache_file', True),
        (1, 'path/to/cache_file', True),
        (False, '', True),
        (False, None, True),
        (1, 'path/to/cache_file', False),
    ),
)
def test__read_cache_does_nothing(ignore_cache, cache_file, cache_file_exists, job, mocker):
    mocker.patch.object(job, '_ignore_cache', ignore_cache)
    mocker.patch.object(type(job), 'cache_file', PropertyMock(return_value=cache_file))
    mocker.patch('os.path.exists', Mock(return_value=cache_file_exists))
    open_mock = mocker.patch('upsies.jobs.base.open')
    assert job._read_cache() is False
    assert open_mock.call_args_list == []

@pytest.mark.parametrize(
    argnames='exception, exp_error',
    argvalues=(
        (OSError('No such file'), 'No such file'),
        (OSError(errno.EISDIR, 'Is directory'), 'Is directory'),
    ),
)
def test__read_cache_fails_to_read_cache_file(exception, exp_error, job, mocker):
    mocker.patch('os.path.exists', return_value=True)
    open_mock = mocker.patch('upsies.jobs.base.open', side_effect=exception)
    with pytest.raises(RuntimeError, match=rf'^Unable to read cache {job.cache_file}: {exp_error}$'):
        job._read_cache()
    assert open_mock.call_args_list == [call(job.cache_file, 'rb')]

def test__read_cache_replays_signal_emissions(job, mocker):
    mocker.patch.object(job, '_ignore_cache', False)
    mocker.patch.object(type(job), 'cache_file', PropertyMock(return_value='path/to/cache'))
    mocker.patch('os.path.exists', Mock(return_value=True))
    open_mock = mocker.patch('upsies.jobs.base.open', mocker.mock_open(read_data=b'cached emissions'))
    mocker.patch.object(job, '_deserialize_cached', side_effect=lambda cache: b'deserialized:' + cache)
    mocker.patch.object(job.signal, 'replay')
    assert job._read_cache() is True
    assert open_mock.call_args_list == [call(job.cache_file, 'rb')]
    assert job._deserialize_cached.call_args_list == [call(b'cached emissions')]
    assert job.signal.replay.call_args_list == [call(b'deserialized:cached emissions')]

def test__read_cache_ignores_empty_cache_file(job, mocker):
    mocker.patch.object(job, '_ignore_cache', False)
    mocker.patch.object(type(job), 'cache_file', PropertyMock(return_value='path/to/cache'))
    mocker.patch('os.path.exists', Mock(return_value=True))
    open_mock = mocker.patch('upsies.jobs.base.open', mocker.mock_open(read_data=b''))
    mocker.patch.object(job, '_deserialize_cached', side_effect=lambda cache: '')
    mocker.patch.object(job.signal, 'replay')
    assert job._read_cache() is False
    assert open_mock.call_args_list == [call(job.cache_file, 'rb')]
    assert job._deserialize_cached.call_args_list == [call(b'')]
    assert job.signal.replay.call_args_list == []


def test__serialize_cached(job, mocker):
    dumps_mock = mocker.patch('pickle.dumps')
    job._serialize_cached('mock emissions')
    assert dumps_mock.call_args_list == [
        call('mock emissions', protocol=0, fix_imports=False),
    ]


def test__deserialize_cached(job, mocker):
    loads_mock = mocker.patch('pickle.loads')
    job._deserialize_cached('mock serialized emissions')
    assert loads_mock.call_args_list == [
        call('mock serialized emissions')
    ]


def test_cache_file_when_cache_id_is_None(job, mocker):
    mocker.patch.object(type(job), 'cache_id', PropertyMock(return_value=None))
    assert job.cache_file is None

@pytest.mark.parametrize('cache_id_value', ('', {}, ()), ids=lambda v: repr(v))
def test_cache_file_when_cache_id_is_falsy(cache_id_value, job, mocker):
    mocker.patch.object(type(job), 'cache_id', PropertyMock(return_value=cache_id_value))
    assert job.cache_file == os.path.join(job.cache_directory, f'{job.name}.out')

def test_cache_file_when_cache_id_is_too_long(job, mocker):
    job._max_filename_len = 20
    long_cache_id = ''.join(str(n % 10) for n in range(job._max_filename_len))
    print(long_cache_id)
    mocker.patch.object(type(job), 'cache_id', PropertyMock(return_value=long_cache_id))
    mocker.patch.object(type(job), '_cache_id_as_string', Mock(return_value=f'as_string:{long_cache_id}'))
    assert job.cache_file == os.path.join(job.cache_directory, f'{job.name}.as_st…56789.out')
    assert job._cache_id_as_string.call_args_list == [call(long_cache_id)]

def test_cache_file_when_cache_id_is_not_too_long(job, mocker):
    mocker.patch.object(type(job), 'cache_id', PropertyMock(return_value='something'))
    mocker.patch.object(type(job), '_cache_id_as_string', Mock(return_value='as_string:something'))
    assert job.cache_file == os.path.join(job.cache_directory, f'{job.name}.as_string:something.out')
    assert job._cache_id_as_string.call_args_list == [call('something')]


@pytest.mark.parametrize(
    argnames='cache_id_argument, exp_cache_id',
    argvalues=(
        ('<not provided>', ''),
        (None, None),
        ('my_cache_id', 'my_cache_id'),
    )
)
def test_cache_id(cache_id_argument, exp_cache_id, tmp_path):
    kwargs = {
        'home_directory': tmp_path,
        'cache_directory': tmp_path,
    }
    if cache_id_argument != '<not provided>':
        kwargs['cache_id'] = cache_id_argument
    job = FooJob(**kwargs)
    assert job.cache_id == exp_cache_id


@pytest.mark.parametrize('value', (object(), print, lambda: None), ids=lambda v: str(v))
def test__cache_id_as_string_when_cache_id_is_mapping_with_nonstringable_key(value, job, mocker):
    with pytest.raises(RuntimeError, match=rf'^{re.escape(str(type(value)))} has no string representation$'):
        job._cache_id_as_string({'a': 'foo', value: 'bar', 'c': 'baz'})

@pytest.mark.parametrize('value', (object(), print, lambda: None), ids=lambda v: str(v))
def test__cache_id_as_string_when_cache_id_is_mapping_with_nonstringable_value(value, job, mocker):
    with pytest.raises(RuntimeError, match=rf'^{re.escape(str(type(value)))} has no string representation$'):
        job._cache_id_as_string({'a': 'foo', 'b': value, 'c': 'baz'})

@pytest.mark.parametrize(
    argnames='value, exp_string',
    argvalues=(
        ('bar', 'bar'),
        (123, '123'),
        (1.23, '1.23'),
        ([1, 2, 3], '1,2,3')
    ),
    ids=lambda v: str(v),
)
def test__cache_id_as_string_when_cache_id_is_mapping_with_all_stringable_values(value, exp_string, job, mocker):
    assert job._cache_id_as_string({'a': 'foo', 'b': value, 'c': 'baz'}) == f'a=foo,b={exp_string},c=baz'

@pytest.mark.parametrize('value', (object(), print, lambda: None), ids=lambda v: str(v))
@pytest.mark.parametrize('type_', (list, tuple, iter), ids=lambda v: v.__name__)
def test__cache_id_as_string_when_cache_id_is_iterable_with_nonstringable_value(value, type_, job, mocker):
    sequence = ('foo', value, 'baz')
    iterable = type_(sequence)
    with pytest.raises(RuntimeError, match=rf'^{re.escape(str(type(value)))} has no string representation$'):
        job._cache_id_as_string(iterable)

@pytest.mark.parametrize(
    argnames='value, exp_string',
    argvalues=(
        ('bar', 'bar'),
        (123, '123'),
        (1.23, '1.23'),
        ([1, 2, 3], '1,2,3')
    ),
    ids=lambda v: str(v),
)
def test__cache_id_as_string_when_cache_id_is_iterable_with_all_stringable_values(value, exp_string, job, mocker):
    assert job._cache_id_as_string(['foo', value, 'baz']) == f'foo,{exp_string},baz'

def test__cache_id_as_string_normalizes_existing_paths(tmp_path):
    some_dir = tmp_path / 'foo' / 'bar'
    some_path = some_dir / 'baz.txt'
    some_dir.mkdir(parents=True)
    some_path.write_text('some thing')
    abs_path = some_path
    rel_path = some_path.relative_to(tmp_path)
    orig_cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        job1 = FooJob(home_directory=tmp_path, cache_directory=tmp_path)
        job2 = FooJob(home_directory=tmp_path, cache_directory=tmp_path)
        assert job1._cache_id_as_string(abs_path) == job2._cache_id_as_string(rel_path)
    finally:
        os.chdir(orig_cwd)

def test__cache_id_as_string_normalizes_multibyte_characters(job, mocker):
    mocker.patch.object(type(job), 'cache_id', PropertyMock(return_value='kožušček'))
    assert job.cache_file == os.path.join(job.cache_directory, f'{job.name}.kozuscek.out')
