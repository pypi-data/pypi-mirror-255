import asyncio
import re
from unittest.mock import AsyncMock, Mock, PropertyMock, call

import pytest

from upsies.uis.tui.tui import TUI


class Job:
    def __init__(self, name, **kwargs):
        self.name = name
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self):
        return f'<{type(self).__name__} {self.name!r}>'


class JobInfo:
    def __init__(self, *, job=None, widget=None, container=None):
        self.job = job
        self.widget = widget
        self.container = container

    def __repr__(self):
        return f'<{type(self).__name__} {self.job.name!r}>'


@pytest.fixture
def tui(event_loop):
    tui = TUI()
    assert tui._loop is event_loop
    return tui


def test_uncaught_exception(tui, mocker):
    mocker.patch.object(tui, '_exit')

    counter = 0

    def bad_callback(task):
        nonlocal counter
        counter += 1
        raise RuntimeError(f'bad, bad, bad: {counter}')

    async def with_running_loop():
        for _ in range(3):
            task = asyncio.create_task(AsyncMock()())
            task.add_done_callback(bad_callback)
            await task

    tui._loop.run_until_complete(with_running_loop())

    assert type(tui._exception) is RuntimeError
    assert str(tui._exception) == 'bad, bad, bad: 1'
    assert tui._exit.call_args_list == [call(), call(), call()]


def test_add_jobs(tui, mocker):
    jobs = {
        'a': Job(name='a'),
        'b': Job(name='b'),
        'c': Job(name='c'),
    }

    mocks = Mock()
    mocks.attach_mock(mocker.patch.object(tui, '_add_job'), '_add_job')
    mocks.attach_mock(mocker.patch.object(tui, '_update_jobs_container'), '_update_jobs_container')
    mocks.attach_mock(mocker.patch.object(tui, '_connect_jobs'), '_connect_jobs')

    tui.add_jobs(*jobs.values())

    assert mocks.mock_calls == [
        call._add_job(jobs['a']),
        call._add_job(jobs['b']),
        call._add_job(jobs['c']),
        call._update_jobs_container(),
        call._connect_jobs((jobs['a'], jobs['b'], jobs['c'])),
    ]


def test__add_job_detects_job_name_duplicate(tui, mocker):
    mocker.patch('upsies.uis.tui.jobwidgets.JobWidget')
    mocker.patch('upsies.uis.tui.tui.to_container')

    tui._add_job(Job(name='a'))
    tui._add_job(Job(name='b'))
    with pytest.raises(RuntimeError, match=r'^Conflicting job name: b$'):
        tui._add_job(Job(name='b'))


def test__add_job_gracefully_ignores_adding_exact_job_duplicate(tui, mocker):
    mocker.patch('upsies.uis.tui.jobwidgets.JobWidget')
    mocker.patch('upsies.uis.tui.tui.to_container')

    jobs = {
        'a': Job(name='a'),
        'b': Job(name='b'),
        'c': Job(name='c'),
        'd': Job(name='d'),
    }

    tui._add_job(jobs['a'])
    tui._add_job(jobs['b'])
    tui._add_job(jobs['c'])
    tui._add_job(jobs['b'])
    tui._add_job(jobs['d'])
    assert list(tui._jobs) == list(jobs)
    assert [jobinfo.job for jobinfo in tui._jobs.values()] == list(jobs.values())


def test__add_job_creates_JobWidget_and_Container(tui, mocker):
    JobWidget_mock = mocker.patch('upsies.uis.tui.jobwidgets.JobWidget')
    to_container_mock = mocker.patch('upsies.uis.tui.tui.to_container')
    job = Job(name='a')
    tui._add_job(job)
    assert tuple(tui._jobs) == (job.name,)
    assert tui._jobs[job.name].widget == JobWidget_mock.return_value
    assert tui._jobs[job.name].container == to_container_mock.return_value
    assert JobWidget_mock.call_args_list == [call(job, tui._app)]
    assert to_container_mock.call_args_list == [call(JobWidget_mock.return_value)]


def test__update_jobs_container(tui, mocker):
    tui._jobs = {
        # Interactive jobs
        'ai': JobInfo(job=Job('a', is_enabled=False, was_started=False, is_finished=False, errors=()), widget=Mock(is_interactive=True), container=Mock(id='aw')),
        'bi': JobInfo(job=Job('b', is_enabled=False, was_started=True, is_finished=False, errors=()), widget=Mock(is_interactive=True), container=Mock(id='bw')),
        'ci': JobInfo(job=Job('c', is_enabled=True, was_started=False, is_finished=False, errors=()), widget=Mock(is_interactive=True), container=Mock(id='cw')),
        'di': JobInfo(job=Job('d', is_enabled=True, was_started=True, is_finished=False, errors=()), widget=Mock(is_interactive=True), container=Mock(id='dw')),
        'ei': JobInfo(job=Job('e', is_enabled=True, was_started=True, is_finished=False, errors=()), widget=Mock(is_interactive=True), container=Mock(id='ew')),

        # Background jobs
        '1b': JobInfo(job=Job('1', is_enabled=False, was_started=False, is_finished=False, errors=()), widget=Mock(is_interactive=False), container=Mock(id='1w')),
        '2b': JobInfo(job=Job('2', is_enabled=False, was_started=True, is_finished=False, errors=()), widget=Mock(is_interactive=False), container=Mock(id='2w')),
        '3b': JobInfo(job=Job('3', is_enabled=True, was_started=False, is_finished=False, errors=()), widget=Mock(is_interactive=False), container=Mock(id='3w')),
        '4b': JobInfo(job=Job('4', is_enabled=True, was_started=True, is_finished=False, errors=()), widget=Mock(is_interactive=False), container=Mock(id='4w')),
        '5b': JobInfo(job=Job('5', is_enabled=True, was_started=True, is_finished=False, errors=()), widget=Mock(is_interactive=False), container=Mock(id='5w')),
    }
    jobs_container_id = id(tui._jobs_container)

    # tui._layout.focus() may raise ValueError, which should be ignored.
    def layout_focus(container):
        if container in (
                tui._jobs['bi'].container,
                tui._jobs['ei'].container,
                tui._jobs['2b'].container,
                tui._jobs['4b'].container,
        ):
            raise ValueError(f'Unfocusable container: {container!r}')

    mocker.patch.object(tui._layout, 'focus', side_effect=layout_focus)

    def assert_jobs_container(*children, focused):
        tui._update_jobs_container()

        exp_children = [tui._jobs[child].container for child in children]
        assert tui._jobs_container.children == exp_children
        assert id(tui._jobs_container) == jobs_container_id

        if focused:
            focused_jobinfo = tui._jobs[focused]
            assert tui._focused_jobinfo is focused_jobinfo
            assert tui._layout.focus.call_args_list == [call(focused_jobinfo.container)]
        else:
            assert tui._focused_jobinfo is None
            assert tui._layout.focus.call_args_list == []
        tui._layout.focus.reset_mock()

    # First interactive, started and unfinished job is focused.
    # Enabled background jobs are listed.
    assert_jobs_container('di', '3b', '4b', '5b', focused='di')

    # Finishing background job should have no effect
    tui._jobs['2b'].job.is_enabled = True
    assert_jobs_container('di', '2b', '3b', '4b', '5b', focused='di')

    # Finishing focused job should focus next interactive job.
    tui._jobs['di'].job.is_finished = True
    assert_jobs_container('di', 'ei', '2b', '3b', '4b', '5b', focused='ei')

    # Finishing focused job should unfocus if there is no interactive, started
    # and unfinished jobs.
    tui._jobs['ei'].job.is_finished = True
    assert_jobs_container('di', 'ei', '2b', '3b', '4b', '5b', focused=None)

    # Enabling another interactive, started and unfinished job should display it
    # in order of the job list.
    tui._jobs['bi'].job.is_enabled = True
    assert_jobs_container('bi', 'di', 'ei', '2b', '3b', '4b', '5b', focused='bi')

    # Enabling another interactive, started and unfinished job should have no
    # effect until the focused job finishes. (Focus should not be stolen.)
    tui._jobs['ai'].job.is_enabled = True
    tui._jobs['ai'].job.was_started = True
    assert_jobs_container('bi', 'di', 'ei', '2b', '3b', '4b', '5b', focused='bi')

    # As soon as the focused job finishes, the previously enabled job may now
    # grab focus.
    tui._jobs['bi'].job.is_finished = True
    assert_jobs_container('ai', 'bi', 'di', 'ei', '2b', '3b', '4b', '5b', focused='ai')

    # Start and finish all remaining background jobs.
    tui._jobs['1b'].job.is_enabled = True
    assert_jobs_container('ai', 'bi', 'di', 'ei', '1b', '2b', '3b', '4b', '5b', focused='ai')
    tui._jobs['5b'].job.is_finished = True
    assert_jobs_container('ai', 'bi', 'di', 'ei', '1b', '2b', '3b', '4b', '5b', focused='ai')
    tui._jobs['3b'].job.is_finished = True
    assert_jobs_container('ai', 'bi', 'di', 'ei', '1b', '2b', '3b', '4b', '5b', focused='ai')
    tui._jobs['1b'].job.is_finished = True
    assert_jobs_container('ai', 'bi', 'di', 'ei', '1b', '2b', '3b', '4b', '5b', focused='ai')
    tui._jobs['2b'].job.is_finished = True
    assert_jobs_container('ai', 'bi', 'di', 'ei', '1b', '2b', '3b', '4b', '5b', focused='ai')
    tui._jobs['4b'].job.is_finished = True
    assert_jobs_container('ai', 'bi', 'di', 'ei', '1b', '2b', '3b', '4b', '5b', focused='ai')

    # The last interactive job finishes and focus should be null.
    tui._jobs['ai'].job.is_finished = True
    assert_jobs_container('ai', 'bi', 'di', 'ei', '1b', '2b', '3b', '4b', '5b', focused=None)


def test__connect_jobs(tui):
    mocks = Mock()
    jobs = [
        mocks.foo,
        mocks.bar,
        mocks.baz,
    ]
    tui._connect_jobs(jobs)
    assert mocks.mock_calls == [
        call.foo.signal.register('finished', tui._handle_job_finished),
        call.foo.signal.register('refresh_job_list', tui._refresh_jobs),
        call.bar.signal.register('finished', tui._handle_job_finished),
        call.bar.signal.register('refresh_job_list', tui._refresh_jobs),
        call.baz.signal.register('finished', tui._handle_job_finished),
        call.baz.signal.register('refresh_job_list', tui._refresh_jobs),
    ]


@pytest.mark.parametrize(
    argnames='finished_job, enabled_jobs, exp_mock_calls',
    argvalues=(
        pytest.param(
            Job(name='x', exit_code=1, is_finished=True),
            [
                Job(name='foo', is_finished=False),
            ],
            [call._refresh_jobs(), call._exit()],
            id='Finished job failed',
        ),
        pytest.param(
            Job(name='x', exit_code=0, is_finished=True),
            [
                Job(name='foo', is_finished=False),
            ],
            [call._refresh_jobs()],
            id='Finished job succeeded, only other job is not finished',
        ),
        pytest.param(
            Job(name='x', exit_code=0, is_finished=True),
            [
                Job(name='foo', is_finished=True),
            ],
            [call._refresh_jobs(), call._exit()],
            id='Finished job succeeded, only other job is finished',
        ),
        pytest.param(
            Job(name='x', exit_code=0, is_finished=True),
            [
                Job(name='foo', is_finished=True),
                Job(name='bar', is_finished=True),
                Job(name='baz', is_finished=True),
            ],
            [call._refresh_jobs(), call._exit()],
            id='Finished job succeeded, all other jobs are finished',
        ),
        pytest.param(
            Job(name='x', exit_code=0, is_finished=True),
            [
                Job(name='foo', is_finished=True),
                Job(name='bar', is_finished=False),
                Job(name='baz', is_finished=True),
            ],
            [call._refresh_jobs()],
            id='Finished job succeeded, one other job is not finished',
        ),
    ),
)
def test__handle_job_finished(finished_job, enabled_jobs, exp_mock_calls, tui, mocker):
    mocks = Mock()
    mocker.patch.object(type(tui), '_enabled_jobs', PropertyMock(return_value=[
        Mock(job=job) for job in enabled_jobs
    ]))
    mocks.attach_mock(mocker.patch.object(tui, '_exit'), '_exit')
    mocks.attach_mock(mocker.patch.object(tui, '_refresh_jobs'), '_refresh_jobs')

    tui._handle_job_finished(finished_job)

    assert mocks.mock_calls == exp_mock_calls


def test__refresh_jobs(tui, mocker):
    enabled_jobs = [
        Job(name='foo'),
        Job(name='bar'),
        Job(name='baz'),
    ]

    mocks = Mock()
    mocker.patch.object(type(tui), '_enabled_jobs', PropertyMock(return_value=[
        JobInfo(job=job) for job in enabled_jobs
    ]))
    mocks.attach_mock(mocker.patch.object(tui, '_start_enabled_jobs'), '_start_enabled_jobs')
    mocks.attach_mock(mocker.patch.object(tui, '_update_jobs_container'), '_update_jobs_container')
    mocks.attach_mock(mocker.patch.object(tui._app, 'invalidate'), 'invalidate')

    tui._refresh_jobs()

    assert mocks.mock_calls == [
        call._start_enabled_jobs(),
        call._update_jobs_container(),
        call.invalidate(),
    ]


def test__start_enabled_jobs(tui, mocker):
    mocks = Mock()
    jobinfos = {
        'a': JobInfo(job=Job(name='a', was_started=False, autostart=False, start=mocks.start_a)),
        'b': JobInfo(job=Job(name='b', was_started=False, autostart=True, start=mocks.start_b)),
        'c': JobInfo(job=Job(name='c', was_started=True, autostart=False, start=mocks.start_c)),
        'd': JobInfo(job=Job(name='d', was_started=True, autostart=True, start=mocks.start_d)),
        'e': JobInfo(job=Job(name='e', was_started=True, autostart=True, start=mocks.start_e)),
        'f': JobInfo(job=Job(name='f', was_started=True, autostart=False, start=mocks.start_f)),
        'g': JobInfo(job=Job(name='g', was_started=False, autostart=True, start=mocks.start_g)),
        'h': JobInfo(job=Job(name='h', was_started=False, autostart=False, start=mocks.start_h)),
    }

    mocker.patch.object(type(tui), '_enabled_jobs', tuple(jobinfos.values()))

    tui._start_enabled_jobs()

    assert mocks.mock_calls == [
        call.start_b(),
        call.start_g(),
    ]


def test__enabled_jobs(tui, mocker):
    jobinfos = {
        'a': JobInfo(job=Job(name='a', is_enabled=False)),
        'b': JobInfo(job=Job(name='b', is_enabled=False)),
        'c': JobInfo(job=Job(name='c', is_enabled=True)),
        'd': JobInfo(job=Job(name='d', is_enabled=True)),
        'e': JobInfo(job=Job(name='e', is_enabled=False)),
        'f': JobInfo(job=Job(name='f', is_enabled=True)),
    }

    mocker.patch.object(tui, '_jobs', jobinfos)

    assert tui._enabled_jobs == (
        jobinfos['c'],
        jobinfos['d'],
        jobinfos['f'],
    )


def test__all_jobs_finished(tui, mocker):
    jobinfos = {
        'a': JobInfo(job=Job(name='a', is_finished=False)),
        'b': JobInfo(job=Job(name='b', is_finished=False)),
        'c': JobInfo(job=Job(name='c', is_finished=True)),
        'd': JobInfo(job=Job(name='d', is_finished=True)),
        'e': JobInfo(job=Job(name='e', is_finished=False)),
        'f': JobInfo(job=Job(name='f', is_finished=True)),
    }
    mocker.patch.object(type(tui), '_enabled_jobs', PropertyMock(return_value=tuple(jobinfos.values())))

    assert tui._all_jobs_finished is False
    jobinfos['a'].job.is_finished = True
    assert tui._all_jobs_finished is False
    jobinfos['b'].job.is_finished = True
    assert tui._all_jobs_finished is False
    jobinfos['c'].job.is_finished = True
    assert tui._all_jobs_finished is False
    jobinfos['e'].job.is_finished = True
    assert tui._all_jobs_finished is True


@pytest.mark.parametrize(
    argnames='exception_from_jobs, exit_codes, exp_result',
    argvalues=(
        (None, [0, 0, 0], 0),
        (None, [0, 3, 4], 3),
        (RuntimeError('very bad'), [0, 0, 0], RuntimeError('very bad')),
    ),
    ids=lambda v: repr(v),
)
def test_run(exception_from_jobs, exit_codes, exp_result, tui, mocker):
    mocks = Mock(
        wait_a=AsyncMock(),
        wait_b=AsyncMock(),
        wait_c=AsyncMock(),
        wait_d=AsyncMock(),
        wait_e=AsyncMock(),
        wait_f=AsyncMock(),
        wait_g=AsyncMock(),
        wait_h=AsyncMock(),
    )
    mocks.attach_mock(mocker.patch.object(tui, 'add_jobs'), 'add_jobs')
    mocks.attach_mock(mocker.patch.object(tui, '_run'), '_run')
    mocks.attach_mock(
        mocker.patch.object(tui, '_get_exception', return_value=exception_from_jobs),
        '_get_exception',
    )
    jobinfos = {
        'a': JobInfo(job=Job(name='a', exit_code=exit_codes[0])),
        'b': JobInfo(job=Job(name='b', exit_code=exit_codes[1])),
        'c': JobInfo(job=Job(name='c', exit_code=exit_codes[2])),
    }
    mocker.patch.object(type(tui), '_enabled_jobs', tuple(jobinfos.values()))
    jobs = tuple(jobinfo.job for jobinfo in jobinfos.values())

    if isinstance(exp_result, Exception):
        with pytest.raises(type(exp_result), match=rf'^{re.escape(str(exp_result))}$'):
            tui.run(jobs)
    else:
        return_value = tui.run(jobs)
        assert return_value == exp_result

    assert mocks.mock_calls == [
        call.add_jobs(*jobs),
        call._run(),
        call._get_exception(),
    ]


@pytest.mark.parametrize(
    argnames='run_async_exception, exp_jobs_terminated, exp_exception',
    argvalues=(
        (None, False, None),
        (asyncio.CancelledError(), True, None),
        (RuntimeError('oh no'), True, RuntimeError('oh no')),
    ),
    ids=lambda v: repr(v),
)
@pytest.mark.asyncio
async def test__run(run_async_exception, exp_jobs_terminated, exp_exception, tui, mocker):
    mocks = Mock(
        wait_a=AsyncMock(),
        wait_b=AsyncMock(),
        wait_c=AsyncMock(),
        wait_d=AsyncMock(),
        wait_e=AsyncMock(),
        wait_f=AsyncMock(),
        wait_g=AsyncMock(),
        wait_h=AsyncMock(),
    )
    mocks.attach_mock(mocker.patch.object(tui, '_start_enabled_jobs'), '_start_enabled_jobs')
    mocks.attach_mock(mocker.patch.object(tui, '_terminate_jobs'), '_terminate_jobs')
    mocks.attach_mock(mocker.patch.object(tui._app, 'run_async'), 'run_async')
    mocks.run_async.side_effect = run_async_exception
    jobinfos = {
        'a': JobInfo(job=Job(name='a', was_started=False, is_finished=False, wait=mocks.wait_a)),
        'b': JobInfo(job=Job(name='b', was_started=False, is_finished=True, wait=mocks.wait_b)),
        'c': JobInfo(job=Job(name='c', was_started=True, is_finished=False, wait=mocks.wait_c)),
        'd': JobInfo(job=Job(name='d', was_started=True, is_finished=True, wait=mocks.wait_d)),
        'e': JobInfo(job=Job(name='e', was_started=True, is_finished=True, wait=mocks.wait_e)),
        'f': JobInfo(job=Job(name='f', was_started=True, is_finished=False, wait=mocks.wait_f)),
        'g': JobInfo(job=Job(name='g', was_started=False, is_finished=True, wait=mocks.wait_g)),
        'h': JobInfo(job=Job(name='h', was_started=False, is_finished=False, wait=mocks.wait_h)),
    }
    mocker.patch.object(type(tui), '_enabled_jobs', tuple(jobinfos.values()))

    exp_mock_calls = [
        call._start_enabled_jobs(),
        call.run_async(set_exception_handler=False),
    ]

    if exp_exception:
        with pytest.raises(type(exp_exception), match=rf'^{re.escape(str(exp_exception))}$'):
            await tui._run()
    else:
        await tui._run()

        if exp_jobs_terminated:
            exp_mock_calls.append(call._terminate_jobs())
        exp_mock_calls.append(call.wait_c())
        exp_mock_calls.append(call.wait_f())

    assert mocks.mock_calls == exp_mock_calls


def test__exit_when_run_task_is_already_cancelled(tui, mocker):
    mocks = Mock()
    mocks.attach_mock(mocker.patch.object(tui._loop, 'call_later'), 'call_later')
    tui._run_task = mocks._run_task
    tui._run_task_cancelled = True

    tui._exit()

    assert mocks.mock_calls == []

def test__exit_when_run_task_was_created(tui, mocker):
    mocks = Mock()
    mocks.attach_mock(mocker.patch.object(tui._loop, 'call_later'), 'call_later')
    tui._run_task = mocks._run_task
    tui._run_task_cancelled = False

    tui._exit()

    assert mocks.mock_calls == [call._run_task.cancel()]

def test__exit_when_run_task_was_not_created(tui, mocker):
    mocks = Mock()
    mocks.attach_mock(mocker.patch.object(tui._loop, 'call_later'), 'call_later')
    tui._run_task = None
    tui._run_task_cancelled = False

    tui._exit()

    assert mocks.mock_calls == [call.call_later(0, tui._exit)]


def test__terminate_jobs(tui, mocker):
    mocks = Mock()
    tui._jobs = {
        'a': JobInfo(job=Job(name='a', is_finished=False, terminate=mocks.terminate_a)),
        'b': JobInfo(job=Job(name='b', is_finished=False, terminate=mocks.terminate_b)),
        'c': JobInfo(job=Job(name='c', is_finished=True, terminate=mocks.terminate_c)),
        'd': JobInfo(job=Job(name='d', is_finished=True, terminate=mocks.terminate_d)),
        'e': JobInfo(job=Job(name='e', is_finished=False, terminate=mocks.terminate_e)),
        'f': JobInfo(job=Job(name='f', is_finished=False, terminate=mocks.terminate_f)),
        'g': JobInfo(job=Job(name='g', is_finished=True, terminate=mocks.terminate_g)),
        'h': JobInfo(job=Job(name='h', is_finished=True, terminate=mocks.terminate_h)),
    }

    tui._terminate_jobs()

    assert mocks.mock_calls == [
        call.terminate_a(),
        call.terminate_b(),
        call.terminate_e(),
        call.terminate_f(),
    ]


@pytest.mark.parametrize(
    argnames='uncaught_exception, jobs, exp_exception',
    argvalues=(
        (
            RuntimeError('Application went haywire'),
            {
                'a': JobInfo(job=Job(name='a', raised=None)),
                'c': JobInfo(job=Job(name='b', raised=ValueError('wrong value, mate'))),
                'f': JobInfo(job=Job(name='c', raised=None)),
            },
            RuntimeError('Application went haywire'),
        ),
        (
            None,
            {
                'a': JobInfo(job=Job(name='a', raised=None)),
                'b': JobInfo(job=Job(name='b', raised=None)),
                'c': JobInfo(job=Job(name='c', raised=ValueError('wrong value, mate'))),
                'd': JobInfo(job=Job(name='d', raised=None)),
                'e': JobInfo(job=Job(name='e', raised=TypeError('wrong type, dude'))),
                'f': JobInfo(job=Job(name='f', raised=None)),
            },
            ValueError('wrong value, mate'),
        ),
        (
            None,
            {
                'a': JobInfo(job=Job(name='a', raised=None)),
                'b': JobInfo(job=Job(name='b', raised=None)),
                'c': JobInfo(job=Job(name='c', raised=None)),
            },
            None,
        ),
    ),
    ids=lambda v: repr(v),
)
def test__get_exception(uncaught_exception, jobs, exp_exception, tui):
    tui._jobs = jobs
    tui._exception = uncaught_exception

    exception = tui._get_exception()
    if exp_exception:
        assert type(exception) is type(exp_exception)
        assert str(exception) is str(exp_exception)
    else:
        assert exception is None
