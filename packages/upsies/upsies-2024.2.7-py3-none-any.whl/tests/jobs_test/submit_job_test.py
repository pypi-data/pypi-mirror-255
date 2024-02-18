import itertools
from unittest.mock import AsyncMock, Mock, PropertyMock, call

import pytest

from upsies import errors
from upsies.jobs.submit import SubmitJob
from upsies.trackers import TrackerBase, TrackerJobsBase


@pytest.fixture
def make_SubmitJob(tracker, tracker_jobs, tmp_path):
    def make_SubmitJob(**kwargs):
        return SubmitJob(
            home_directory=tmp_path,
            cache_directory=tmp_path,
            tracker=tracker,
            tracker_jobs=tracker_jobs,
            **kwargs,
        )

    return make_SubmitJob


@pytest.fixture
def job(make_SubmitJob):
    return make_SubmitJob()


@pytest.fixture
def tracker():
    class TestTracker(TrackerBase):
        name = 'test'
        label = 'TeST'
        TrackerConfig = 'tracker config class'
        TrackerJobs = 'tracker jobs class'
        login = AsyncMock()
        logout = AsyncMock()
        _login = AsyncMock()
        _logout = AsyncMock()
        is_logged_in = PropertyMock()
        get_announce_url = AsyncMock()
        upload = AsyncMock()

    return TestTracker()

@pytest.fixture
def tracker_jobs(tracker):
    kwargs = {
        'content_path': 'content/path',
        'tracker': tracker,
        'btclient': Mock(),
        'torrent_destination': 'torrent/destination',
        'image_hosts': (Mock(),),
        'common_job_args': {},
    }

    class TestTrackerJobs(TrackerJobsBase):
        def __init__(self, **kw):
            return super().__init__(**{**kwargs, **kw})

        jobs_before_upload = PropertyMock()
        jobs_after_upload = PropertyMock()
        submission_ok = PropertyMock(return_value=False)

    return TestTrackerJobs()


def test_cache_id(job):
    assert job.cache_id is None


@pytest.mark.asyncio
async def test_initialize_creates_enabled_jobs_after_upload(make_SubmitJob, mocker):
    logged = []

    def create_jobs(msg):
        logged.append(msg)

    mocker.patch('upsies.jobs.submit.SubmitJob.enabled_jobs_after_upload', PropertyMock(
        side_effect=lambda: create_jobs('Creating jobs_after_upload'),
    ))

    make_SubmitJob()

    assert logged == ['Creating jobs_after_upload']


@pytest.mark.asyncio
async def test_initialize_registers_to_tracker_and_tracker_jobs_signals(job):
    for t in (job._tracker, job._tracker_jobs):
        assert job.warn in t.signal.signals['warning']
        assert job.error in t.signal.signals['error']
        assert job.exception in t.signal.signals['exception']


@pytest.mark.asyncio
async def test_initialize_starts_enabled_jobs_after_upload_on_output(job, mocker):
    mocker.patch.object(type(job._tracker_jobs), 'jobs_after_upload', PropertyMock(
        return_value=[Mock(), Mock(), Mock()],
    ))

    assert len(job.enabled_jobs_after_upload) > 0
    for j in job.enabled_jobs_after_upload:
        assert j.start.call_args_list == []

    job.start()
    try:
        job.send('mock output')

        for j in job.enabled_jobs_after_upload:
            assert j.start.call_args_list == [call()]
    finally:
        await job.wait()


@pytest.mark.parametrize('signal', ('finished', 'error'))
def test_info_is_cleared(signal, job, mocker):
    job.info = 'foo'
    assert job.info == 'foo'

    job.signal.emit(signal, 'foo')

    assert job.info == ''


class MockJob:
    instances = {}

    def __init__(self, name, start, actions):
        self.name = name
        self._actions = list(actions)
        self._was_started = start
        self._is_finished = False
        self.wait_calls = 0
        type(self).instances[name] = self

    async def wait(self):
        self.wait_calls += 1
        print(f'=== {self.name}, {self.wait_calls=} ===============================')

        if self._actions:
            name, action = self._actions.pop(0).split('.')
            if action:
                attr, value = action.split('=')
                job = type(self).instances[name]
                setattr(job, attr, eval(value))

        for job in type(self).instances.values():
            print('   ', job)

    @property
    def was_started(self):
        return self._was_started

    @property
    def is_finished(self):
        return self._is_finished

    def __repr__(self):
        return f'<MockJob {self.name}, {self.was_started=}, {self.is_finished=})'


@pytest.mark.asyncio
async def test_run_keeps_waiting_for_jobs_until_all_are_finished(job, mocker):
    jobs = {
        'a': MockJob('a', start=True, actions=(
            '.',
            'b._was_started=True',
            'a._is_finished=True',
        )),

        'b': MockJob('b', start=False, actions=(
            '.',
            '.',
            'c._was_started=True',
            '.',
            '.',
            'b._is_finished=True',
        )),

        'c': MockJob('c', start=False, actions=(
            '.',
            '.',
            '.',
            'c._is_finished=True',
        )),
    }

    mocker.patch.object(type(job), 'enabled_jobs_before_upload', PropertyMock(side_effect=itertools.chain(
        # Only one job at first
        ((jobs['a'],),),
        # Job "b" was added
        ((jobs['a'], jobs['b']),),
        ((jobs['a'], jobs['b']),),
        # Job "c" was added
        itertools.repeat(
            (jobs['a'], jobs['b'], jobs['c']),
            100,
        ),
    )))

    await job.run()

    assert jobs['a'].wait_calls == 3
    assert jobs['b'].wait_calls == 6
    assert jobs['c'].wait_calls == 4


@pytest.mark.parametrize('submission_ok', ('submission_ok=True', 'submission_ok=False'))
@pytest.mark.asyncio
async def test_run_makes_calls_in_corret_order(submission_ok, job, mocker):
    jobs = {
        'a': MockJob('a', start=True, actions=(
            'a._is_finished=True',
        )),

        'b': MockJob('b', start=True, actions=(
            'b._is_finished=True',
        )),

        'c': MockJob('c', start=True, actions=(
            'c._is_finished=True',
        )),
    }

    mocker.patch.object(type(job), 'enabled_jobs_before_upload', PropertyMock(side_effect=itertools.chain(
        itertools.repeat(
            (jobs['a'], jobs['b'], jobs['c']),
            100,
        ),
    )))

    mocks = Mock()
    # Mock each job's wait() so we can record it, but still call the original
    # wait() by passing it as a side_effect.
    mocks.attach_mock(mocker.patch.object(jobs['a'], 'wait', AsyncMock(side_effect=jobs['a'].wait)), 'wait_a')
    mocks.attach_mock(mocker.patch.object(jobs['b'], 'wait', AsyncMock(side_effect=jobs['b'].wait)), 'wait_b')
    mocks.attach_mock(mocker.patch.object(jobs['c'], 'wait', AsyncMock(side_effect=jobs['c'].wait)), 'wait_c')
    mocks.attach_mock(mocker.patch.object(job._tracker, 'await_tasks'), 'await_tasks')
    mocks.attach_mock(mocker.patch.object(job, '_submit'), '_submit')
    mocker.patch.object(type(job._tracker_jobs), 'submission_ok', PropertyMock(return_value=submission_ok))

    await job.run()

    exp_mock_calls = [
        call.wait_a(),
        call.wait_b(),
        call.wait_c(),
        call.await_tasks(),
    ]
    if submission_ok:
        exp_mock_calls.append(call._submit())

    assert mocks.mock_calls == exp_mock_calls


@pytest.mark.parametrize('torrent_page_url', ('http:/foo?torrent_id=123', ''))
@pytest.mark.parametrize('error_method', ('login', 'upload', 'logout'))
@pytest.mark.asyncio
async def test__submit_handles_RequestError_from_tracker_coro(error_method, torrent_page_url, job, mocker):
    mocks = Mock()
    mocker.patch.object(job._tracker, error_method, AsyncMock(
        side_effect=errors.RequestError(f'{error_method}: No connection'),
    ))
    if error_method != 'upload':
        job._tracker.upload.return_value = torrent_page_url

    mocks.attach_mock(getattr(job._tracker, 'login'), 'login')
    mocks.attach_mock(getattr(job._tracker, 'logout'), 'logout')
    mocks.attach_mock(getattr(job._tracker, 'upload'), 'upload')
    mocks.attach_mock(mocker.patch.object(job, 'send'), 'send')
    mocks.attach_mock(mocker.patch.object(job, 'error'), 'error')

    assert job.output == ()
    assert job.errors == ()

    await job._submit()

    exp_mock_calls = [
        call.login(),
    ]

    if error_method == 'login':
        exp_mock_calls.append(call.error(errors.RequestError(f'{error_method}: No connection')))

    elif error_method == 'upload':
        exp_mock_calls.append(call.upload(job._tracker_jobs))
        exp_mock_calls.append(call.logout())
        exp_mock_calls.append(call.error(errors.RequestError(f'{error_method}: No connection')))

    else:
        exp_mock_calls.append(call.upload(job._tracker_jobs))
        if torrent_page_url:
            exp_mock_calls.append(call.send(torrent_page_url))
        exp_mock_calls.append(call.logout())
        exp_mock_calls.append(call.error(errors.RequestError(f'{error_method}: No connection')))

    assert mocks.mock_calls == exp_mock_calls


@pytest.mark.asyncio
async def test__submit_calls_methods_and_callbacks_in_correct_order(job, mocker):
    mocks = Mock()
    mocks.attach_mock(job._tracker.login, 'login')
    mocks.attach_mock(job._tracker.logout, 'logout')
    mocks.attach_mock(job._tracker.upload, 'upload')
    mocks.attach_mock(mocker.patch.object(job, 'send'), 'send')

    job.signal.register('logging_in', mocks.logging_in_cb)
    job.signal.register('logged_in', mocks.logged_in_cb)
    job.signal.register('uploading', mocks.uploading_cb)
    job.signal.register('uploaded', mocks.uploaded_cb)
    job.signal.register('logging_out', mocks.logging_out_cb)
    job.signal.register('logged_out', mocks.logged_out_cb)

    await job._submit()

    assert mocks.method_calls == [
        call.logging_in_cb(),
        call.login(),
        call.logged_in_cb(),

        call.uploading_cb(),
        call.upload(job._tracker_jobs),
        call.send(mocks.upload.return_value),
        call.uploaded_cb(),

        call.logging_out_cb(),
        call.logout(),
        call.logged_out_cb(),
    ]

@pytest.mark.parametrize(
    argnames='torrent_url, exp_send_calls',
    argvalues=(
        ('http://torrent.url', [call('http://torrent.url')]),
        ('', []),
        (None, []),
    ),
)
@pytest.mark.asyncio
async def test__submit_sends_upload_return_value_as_output(torrent_url, exp_send_calls, job, mocker):
    mocker.patch.object(job, 'send')
    mocker.patch.object(job._tracker, 'upload', return_value=torrent_url)
    await job._submit()
    assert job.send.call_args_list == exp_send_calls


@pytest.mark.asyncio
async def test__submit_sets_info_property_to_current_status(job, mocker):
    exp_infos = [
        'Logging in',
        'Logged in',
        'Uploading',
        'Uploaded',
        'Logging out',
        '',
    ]

    def info_cb():
        assert job.info == exp_infos.pop(0)

    job.signal.register('logging_in', info_cb)
    job.signal.register('logged_in', info_cb)
    job.signal.register('uploading', info_cb)
    job.signal.register('uploaded', info_cb)
    job.signal.register('logging_out', info_cb)
    job.signal.register('logged_out', info_cb)

    mocker.patch.object(job, 'send')
    await job._submit()

    assert exp_infos == []


def test_enabled_jobs_before_upload(job, mocker):
    jobs_before_upload = {
        'a': None,
        'b': Mock(is_enabled=False),
        'c': None,
        'd': Mock(is_enabled=True),
        'e': None,
        'f': Mock(is_enabled=False),
        'g': None,
        'h': Mock(is_enabled=True),
    }
    mocker.patch.object(type(job._tracker_jobs), 'jobs_before_upload', PropertyMock(return_value=jobs_before_upload.values()))

    assert job.enabled_jobs_before_upload == (
        jobs_before_upload['d'],
        jobs_before_upload['h'],
    )


def test_enabled_jobs_after_upload(job, mocker):
    jobs_after_upload = {
        'a': None,
        'b': Mock(is_enabled=False),
        'c': None,
        'd': Mock(is_enabled=True),
        'e': None,
        'f': Mock(is_enabled=False),
        'g': None,
        'h': Mock(is_enabled=True),
    }
    mocker.patch.object(type(job._tracker_jobs), 'jobs_after_upload', PropertyMock(return_value=jobs_after_upload.values()))

    assert job.enabled_jobs_after_upload == (
        jobs_after_upload['d'],
        jobs_after_upload['h'],
    )


@pytest.mark.parametrize('submission_ok, exp_hidden', ((False, True), (True, False)))
def test_hidden_property(submission_ok, exp_hidden, job, mocker):
    mocker.patch.object(type(job._tracker_jobs), 'submission_ok', PropertyMock(return_value=submission_ok))
    assert job.hidden is exp_hidden


@pytest.mark.parametrize(
    argnames='submission_ok, jobs, exp_final_job',
    argvalues=(
        (True, (), None),
        (False, (Mock(is_finished=True), Mock(is_finished=False), Mock(is_finished=True)), None),
        (False, (Mock(is_finished=True, id='a'), Mock(is_finished=True, id='b'), Mock(is_finished=True, id='c')), 'c'),
    ),
)
def test_final_job_before_upload_property(submission_ok, jobs, exp_final_job, job, mocker):
    mocker.patch.object(type(job._tracker_jobs), 'submission_ok', PropertyMock(return_value=submission_ok))
    mocker.patch.object(type(job), 'enabled_jobs_before_upload', PropertyMock(return_value=jobs))
    if not exp_final_job:
        assert job.final_job_before_upload is None
    else:
        assert job.final_job_before_upload.id == exp_final_job


@pytest.mark.parametrize(
    argnames='own_output, final_job_before_upload, exp_output',
    argvalues=(
        (('torrent url',), None, ('torrent url',)),
        (('torrent url',), Mock(output=('description',)), ('description',)),
    ),
    ids=lambda v: repr(v),
)
def test_output_property(own_output, final_job_before_upload, exp_output, job, mocker):
    parent_class = type(job).mro()[1]
    mocker.patch.object(parent_class, 'output', PropertyMock(return_value=own_output))
    mocker.patch.object(type(job), 'final_job_before_upload', PropertyMock(return_value=final_job_before_upload))
    assert job.output == exp_output


@pytest.mark.parametrize(
    argnames='own_exit_code, final_job_before_upload, exp_exit_code',
    argvalues=(
        (123, None, 123),
        (123, Mock(exit_code=456), 456),
    ),
)
def test_exit_code_property(own_exit_code, final_job_before_upload, exp_exit_code, job, mocker):
    parent_class = type(job).mro()[1]
    mocker.patch.object(parent_class, 'exit_code', PropertyMock(return_value=own_exit_code))
    mocker.patch.object(type(job), 'final_job_before_upload', PropertyMock(return_value=final_job_before_upload))
    assert job.exit_code == exp_exit_code
