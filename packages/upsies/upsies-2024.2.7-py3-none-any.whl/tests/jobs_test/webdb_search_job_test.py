import asyncio
from unittest.mock import AsyncMock, Mock, PropertyMock, call

import pytest

from upsies import errors
from upsies.jobs import webdb
from upsies.utils.webdbs import Query, WebDbApiBase


@pytest.fixture
def foodb():
    class FooDb(WebDbApiBase):
        name = 'foodb'
        label = 'FooDB'
        default_config = {}
        sanitize_query = Mock(return_value=Query('sanitized query'))
        get_id_from_text = Mock(return_value=None)
        search = AsyncMock()
        cast = AsyncMock()
        creators = AsyncMock()
        _countries = AsyncMock()
        directors = AsyncMock()
        genres = AsyncMock()
        poster_url = AsyncMock()
        rating = AsyncMock()
        rating_min = 0
        rating_max = 10
        _runtimes = AsyncMock()
        summary = AsyncMock()
        _title_original = AsyncMock()
        _titles_english = AsyncMock()
        type = AsyncMock()
        url = AsyncMock()
        year = AsyncMock()

    return FooDb()


@pytest.fixture
def job(foodb, tmp_path, mocker):
    mocker.patch('upsies.jobs.webdb._InfoCallbacks')
    return webdb.WebDbSearchJob(
        home_directory=tmp_path,
        cache_directory=tmp_path,
        db=foodb,
        query=Query('Mock Title'),
    )


def test_WebDbSearchJob_name(job):
    assert job.name == 'foodb-id'


def test_WebDbSearchJob_label(job):
    assert job.label == 'FooDB ID'


def test_WebDbSearchJob_cache_id(job):
    assert job.cache_id == job.query


def test_WebDbSearchJob_db(job):
    assert job.db is job._db


def test_WebDbSearchJob_query(job):
    assert job.query is job._query


@pytest.mark.parametrize(
    argnames='value, exp_value',
    argvalues=(
        (True, True),
        (False, False),
        (None, False),
        (1, True),
    ),
)
def test_WebDbSearchJob_no_id_ok(value, exp_value, job):
    assert job.no_id_ok is False
    job.no_id_ok = value
    assert job.no_id_ok is exp_value


def test_WebDbSearchJob_is_searching(job, mocker):
    mocker.patch.object(job, '_is_searching', object())
    assert job.is_searching is job._is_searching


@pytest.mark.parametrize(
    argnames='query, exp_from_any_called',
    argvalues=(
        (Query('a query instance'), False),
        ('not a query instance', True),
    ),
    ids=lambda v: repr(v),
)
def test_WebDbSearchJob_initialize_sets_query(query, exp_from_any_called, foodb, mocker, tmp_path):
    mocks = Mock()
    mocks.attach_mock(mocker.patch('upsies.jobs.webdb.webdbs.Query.from_any'), 'from_any')
    mocks.attach_mock(foodb.sanitize_query, 'sanitize_query')
    mocks.sanitize_query.return_value = Query('sanitized query')

    job = webdb.WebDbSearchJob(
        home_directory=tmp_path,
        cache_directory=tmp_path,
        db=foodb,
        query=query,
    )

    if exp_from_any_called:
        exp_mock_calls = [
            call.from_any(query),
            call.sanitize_query(mocks.from_any.return_value),
        ]
    else:
        exp_mock_calls = [
            call.sanitize_query(query),
        ]
    assert mocks.mock_calls == exp_mock_calls
    assert job._query is mocks.sanitize_query.return_value
    assert job._query.signal.signals['changed'] == [job.search]


def test_WebDbSearchJob_initialize_adds_signals(tmp_path, foodb):
    job = webdb.WebDbSearchJob(
        home_directory=tmp_path,
        cache_directory=tmp_path,
        db=foodb,
        query=Query(title='The Foo', year=2010),
    )
    for name in (
            'search_results',
            'searching_status',
            'info_updating',
            'info_updated',
            'query_updated',
            'selected',
    ):
        assert name in job.signal.signals
    for name in (
            'selected',
    ):
        assert name in job.signal.recording


@pytest.mark.parametrize(
    argnames='no_id_ok, exp_no_id_ok',
    argvalues=(
        (True, True),
        (False, False),
        (None, False),
        (1, True),
    ),
)
def test_WebDbSearchJob_initialize_sets_no_id_ok(no_id_ok, exp_no_id_ok, tmp_path, foodb):
    job = webdb.WebDbSearchJob(
        home_directory=tmp_path,
        cache_directory=tmp_path,
        db=foodb,
        query=Query(title='The Foo', year=2010),
        no_id_ok=no_id_ok,
    )
    assert job.no_id_ok == exp_no_id_ok


def test_WebDbSearchJob_initialize_sets_internal_state(tmp_path, foodb):
    job = webdb.WebDbSearchJob(
        home_directory=tmp_path,
        cache_directory=tmp_path,
        db=foodb,
        query=Query(title='The Foo', year=2010),
    )
    assert job._is_searching is False
    assert job._search_task is None
    assert job._info_callbacks_task is None
    assert job._selected == {}


def test_WebDbSearchJob_initialize_handles_selected_signal(tmp_path, foodb):
    job = webdb.WebDbSearchJob(
        home_directory=tmp_path,
        cache_directory=tmp_path,
        db=foodb,
        query=Query(title='The Foo', year=2010),
    )
    assert job.selected == {}
    job.signal.emit('selected', {'foo': 'bar'})
    assert job.selected == {'foo': 'bar'}
    assert id(job.selected) != id(job.selected)


def test_WebDbSearchJob_initialize_creates_info_callbacks(tmp_path, mocker, foodb):
    _InfoCallbacks_mock = mocker.patch('upsies.jobs.webdb._InfoCallbacks')
    _make_update_info_func_mock = mocker.patch(
        'upsies.jobs.webdb.WebDbSearchJob._make_update_info_func',
        Mock(
            side_effect=(
                'id function',
                'summary function',
                'title_original function',
                'title_english function',
                'genres function',
                'directors function',
                'cast function',
                'countries function',
            ),
        )
    )

    job = webdb.WebDbSearchJob(
        home_directory=tmp_path,
        cache_directory=tmp_path,
        db=foodb,
        query=Query(title='The Foo', year=2010),
    )
    assert job._info_callbacks is _InfoCallbacks_mock.return_value
    assert _InfoCallbacks_mock.call_args_list == [call(
        callbacks={
            'id': 'id function',
            'summary': 'summary function',
            'title_original': 'title_original function',
            'title_english': 'title_english function',
            'genres': 'genres function',
            'directors': 'directors function',
            'cast': 'cast function',
            'countries': 'countries function',
        },
        error_callback=job.warn,
    )]
    assert _make_update_info_func_mock.call_args_list == [
        call('id'),
        call('summary'),
        call('title_original'),
        call('title_english'),
        call('genres'),
        call('directors'),
        call('cast'),
        call('countries'),
    ]


def test_WebDbSearchJob__make_update_info_func(job, mocker):
    mocker.patch.object(job, '_update_info_value')
    func = job._make_update_info_func('my key')
    func('value 1')
    assert job._update_info_value.call_args_list == [
        call('my key', 'value 1'),
    ]
    func('value 2')
    assert job._update_info_value.call_args_list == [
        call('my key', 'value 1'),
        call('my key', 'value 2'),
    ]


def test_WebDbSearchJob__update_info_value(job):
    mocks = Mock()
    job.signal.register('info_updating', mocks.info_updating)
    job.signal.register('info_updated', mocks.info_updated)

    for key in ('title', 'year'):
        for value in ('foo', 'bar', 'baz'):
            job._update_info_value(key, Ellipsis)
            assert mocks.mock_calls[-1] == call.info_updating(key)

            job._update_info_value(key, value)
            assert mocks.mock_calls[-1] == call.info_updated(key, value)

    assert mocks.mock_calls == [
        call.info_updating('title'),
        call.info_updated('title', 'foo'),
        call.info_updating('title'),
        call.info_updated('title', 'bar'),
        call.info_updating('title'),
        call.info_updated('title', 'baz'),
        call.info_updating('year'),
        call.info_updated('year', 'foo'),
        call.info_updating('year'),
        call.info_updated('year', 'bar'),
        call.info_updating('year'),
        call.info_updated('year', 'baz'),
    ]


@pytest.mark.asyncio
async def test_WebDbSearchJob_run(job, mocker):
    mocks = Mock()
    mocks.attach_mock(mocker.patch.object(job, 'search'), 'search')
    mocks.attach_mock(mocker.patch.object(job, 'finalization'), 'finalization')

    asyncio.get_running_loop().call_soon(job.finalize)
    await job.run()

    assert mocks.mock_calls == [
        call.search(job.query),
        call.finalization(),
    ]


@pytest.mark.parametrize('results', ((), ('foo', 'bar', 'baz')), ids=('results found', 'no results found'))
@pytest.mark.asyncio
async def test_WebDbSearchJob__search_calls_search_and__run_info_callbacks(results, job, mocker):
    mocks = Mock()
    mocks.attach_mock(mocker.patch.object(job, '_set_state'), '_set_state')
    mocks.attach_mock(mocker.patch.object(job._db, 'search', return_value=results), 'search')
    mocks.attach_mock(mocker.patch.object(job, '_run_info_callbacks'), '_run_info_callbacks')
    mocks.attach_mock(mocker.patch.object(job, 'warn'), 'warn')

    await job._search('mock query')

    assert mocks.mock_calls == [
        call._set_state(is_searching=True, results=()),
        call.search('mock query'),
        call._set_state(is_searching=False, results=results),
        call._run_info_callbacks(results[0] if results else None),
        call._set_state(is_searching=False),
    ]


@pytest.mark.asyncio
async def test_WebDbSearchJob__search_catches_exception_from_search(job, mocker):
    mocks = Mock()
    mocks.attach_mock(mocker.patch.object(job, '_set_state'), '_set_state')
    mocks.attach_mock(mocker.patch.object(job._db, 'search', side_effect=errors.RequestError('network error')), 'search')
    mocks.attach_mock(mocker.patch.object(job, '_run_info_callbacks'), '_run_info_callbacks')
    mocks.attach_mock(mocker.patch.object(job, 'warn'), 'warn')

    await job._search('mock query')

    assert mocks.mock_calls == [
        call._set_state(is_searching=True, results=()),
        call.search('mock query'),
        call.warn(errors.RequestError('network error')),
        call._set_state(is_searching=False),
    ]


@pytest.mark.parametrize(
    argnames='kwargs, exp_attrs, exp_emit_calls',
    argvalues=(
        ({}, {}, []),
        (
            {'is_searching': 1},
            {'is_searching': True},
            [
                call('searching_status', True),
            ],
        ),
        (
            {'is_searching': 0, 'results': ()},
            {'is_searching': False},
            [
                call('searching_status', False),
                call('search_results', ()),
            ],
        ),
        (
            {'is_searching': False, 'results': ('foo', 'bar', 'baz')},
            {'is_searching': False},
            [
                call('searching_status', False),
                call('search_results', ('foo', 'bar', 'baz')),
            ],
        ),
    ),
    ids=lambda v: repr(v),
)
def test_WebDbSearchJob__set_state(kwargs, exp_attrs, exp_emit_calls, job, mocker):
    mocker.patch.object(job.signal, 'emit')

    job._set_state(**kwargs)

    for name, value in exp_attrs.items():
        assert getattr(job, name) == value

    assert job.signal.emit.call_args_list == exp_emit_calls


@pytest.mark.parametrize('info_callbacks_task', (Mock(), None), ids=('with previous task', 'without previous task'))
def test_WebDbSearchJob__run_info_callbacks(info_callbacks_task, job, mocker):
    mocker.patch.object(job, '_info_callbacks_task', info_callbacks_task)
    mocker.patch.object(job, '_info_callbacks', Mock())
    mocker.patch.object(job, 'add_task')

    job._run_info_callbacks('mock result')

    if info_callbacks_task:
        assert info_callbacks_task.cancel.call_args_list == [call()]

    assert job._info_callbacks_task == job.add_task.return_value
    assert job.add_task.call_args_list == [call(
        job._info_callbacks.return_value,
        callback=job._unset_info_callbacks_task,
    )]


def test_WebDbSearchJob__unset_info_callbacks_task(job, mocker):
    mocker.patch.object(job, '_info_callbacks_task', Mock())
    job._unset_info_callbacks_task('ignored task result')
    assert job._info_callbacks_task is None


@pytest.mark.parametrize('search_task', (Mock(), None), ids=('with search task', 'without search task'))
@pytest.mark.parametrize('info_callbacks_task', (Mock(), None), ids=('with info task', 'without info task'))
def test_WebDbSearchJob__cancel_tasks(search_task, info_callbacks_task, job, mocker):
    if search_task:
        search_task.reset_mock()
        mocker.patch.object(job, '_search_task', search_task)
    if info_callbacks_task:
        info_callbacks_task.reset_mock()
        mocker.patch.object(job, '_info_callbacks_task', info_callbacks_task)

    job._cancel_tasks()

    if search_task:
        assert search_task.cancel.call_args_list == [call()]
    if info_callbacks_task:
        assert info_callbacks_task.cancel.call_args_list == [call()]

    assert job._search_task is None
    assert job._info_callbacks_task is None


@pytest.mark.parametrize('was_started', (True, False), ids=('was_started=True', 'was_started=False'))
def test_WebDbSearchJob_search(was_started, job, mocker):
    mocker.patch.object(type(job), 'was_started', PropertyMock(return_value=was_started))
    mocks = Mock()
    mocks.attach_mock(mocker.patch.object(job, '_cancel_tasks'), '_cancel_tasks')
    mocks.attach_mock(mocker.patch.object(job, 'clear_warnings'), 'clear_warnings')
    mocks.attach_mock(mocker.patch.object(job._db, 'sanitize_query'), 'sanitize_query')
    mocks.attach_mock(mocker.patch('upsies.utils.webdbs.common.Query.from_any'), 'from_any')
    mocks.attach_mock(mocker.patch.object(job.query, 'update'), 'update')
    mocks.attach_mock(mocker.patch.object(job.signal, 'emit'), 'emit')
    mocks.attach_mock(mocker.patch.object(job, '_search', Mock()), '_search')
    mocks.attach_mock(mocker.patch.object(job, 'add_task'), 'add_task')

    job.search('mock query')

    exp_mock_calls = [
        call._cancel_tasks(),
        call.clear_warnings(),
        call.from_any('mock query'),
        call.sanitize_query(mocks.from_any.return_value),
        call.update(mocks.sanitize_query.return_value, silent=True),
        call.emit('query_updated', job.query),
    ]
    if was_started:
        exp_mock_calls += [
            call._search(mocks.sanitize_query.return_value),
            call.add_task(
                job._search.return_value,
                callback=job._unset_search_task,
            ),
        ]
    assert mocks.mock_calls == exp_mock_calls


def test_WebDbSearchJob__unset_search_task(job, mocker):
    mocker.patch.object(job, '_search_task', Mock())
    job._unset_search_task('ignored task result')
    assert job._search_task is None


def test_WebDbSearchJob_result_focused(job, mocker):
    mocker.patch.object(job, '_run_info_callbacks')
    job.result_focused('mock result')
    assert job._run_info_callbacks.call_args_list == [call('mock result')]


@pytest.mark.parametrize(
    argnames='result, is_searching, no_id_ok, exp_mock_calls',
    argvalues=(
        (
            Mock(id='123', title='My Title', type='the.type', url='http://webdb/123', year='2012'),
            True,
            False,
            [],
        ),
        (
            Mock(id='123', title='My Title', type='the.type', url='http://webdb/123', year='2012'),
            False,
            False,
            [
                call.emit('selected', {
                    'id': '123',
                    'title': 'My Title',
                    'type': 'the.type',
                    'url': 'http://webdb/123',
                    'year': '2012',
                }),
                call.send('123'),
                call._cancel_tasks(),
                call.finalize(),
            ],
        ),
        (
            None,
            False,
            False,
            [
            ],
        ),
        (
            None,
            False,
            True,
            [
                call._cancel_tasks(),
                call.finalize(),
            ],
        ),
    ),
    ids=lambda v: repr(v),
)
def test_WebDbSearchJob_result_selected(result, is_searching, no_id_ok, exp_mock_calls, job, mocker):
    mocks = Mock()
    mocks.attach_mock(mocker.patch.object(job.signal, 'emit'), 'emit')
    mocks.attach_mock(mocker.patch.object(job, 'send'), 'send')
    mocks.attach_mock(mocker.patch.object(job, '_cancel_tasks'), '_cancel_tasks')
    mocks.attach_mock(mocker.patch.object(job, 'finalize'), 'finalize')
    mocker.patch.object(type(job), 'is_searching', PropertyMock(return_value=is_searching))
    mocker.patch.object(type(job), 'no_id_ok', PropertyMock(return_value=no_id_ok))

    job.result_selected(result)

    assert mocks.mock_calls == exp_mock_calls


@pytest.mark.parametrize(
    argnames='parent_exit_code, no_id_ok, exp_exit_code',
    argvalues=(
        (None, False, None),
        (None, True, None),
        (0, False, 0),
        (0, True, 0),
        (1, False, 1),
        (1, True, 0),
    ),
)
def test_WebDbSearchJob_exit_code(parent_exit_code, no_id_ok, exp_exit_code, mocker, job):
    mocker.patch('upsies.jobs.base.JobBase.exit_code', PropertyMock(return_value=parent_exit_code))
    mocker.patch.object(type(job), 'no_id_ok', PropertyMock(return_value=no_id_ok))
    assert job.exit_code is exp_exit_code


@pytest.fixture
def info_callbacks():
    return webdb._InfoCallbacks(
        callbacks={},
        error_callback=Mock(),
    )


@pytest.mark.parametrize('result', (None, ''))
@pytest.mark.asyncio
async def test__InfoCallbacks___call___is_called_with_falsy_result(result, info_callbacks, mocker):
    mocks = Mock()
    mocks.attach_mock(mocker.patch.object(info_callbacks, '_update_text_values'), '_update_text_values')
    mocks.attach_mock(mocker.patch.object(info_callbacks, '_update_awaitable_values'), '_update_awaitable_values')
    info_callbacks._callbacks = {
        'title': mocks.title,
        'year': mocks.year,
        'genre': mocks.genre,
    }

    await info_callbacks(result)

    assert mocks.mock_calls == [
        call.title(''),
        call.year(''),
        call.genre(''),
    ]


@pytest.mark.asyncio
async def test__InfoCallbacks___call___is_called_with_truthy_result(info_callbacks, mocker):
    mocks = Mock()
    mocks.attach_mock(mocker.patch.object(info_callbacks, '_update_text_values'), '_update_text_values')
    mocks.attach_mock(mocker.patch.object(info_callbacks, '_update_awaitable_values'), '_update_awaitable_values')
    info_callbacks._callbacks = {
        'title': mocks.title,
        'year': mocks.year,
        'genre': mocks.genre,
    }

    result = 'mock result'
    await info_callbacks(result)

    assert mocks.mock_calls == [
        call._update_text_values(result),
        call._update_awaitable_values(result),
    ]


def test__InfoCallbacks__update_text_values(info_callbacks, mocker):
    mocks = Mock()
    mocker.patch.object(info_callbacks, '_value_as_string', side_effect=lambda v: f'as_string:{v}')
    info_callbacks._callbacks = {
        'title': mocks.title,
        'year': mocks.year,
        'genre': mocks.genre,
        'description': mocks.description,
        'cast': mocks.cast,
        'director': mocks.director,
    }

    async def get_description():
        return 'my description'

    async def get_director():
        return 'mister dude'

    result = Mock(
        title='My Title',
        year='2012',
        genre='llamadrama',
        description=get_description,
        cast=('her', 'that guy'),
        director=get_director,
    )

    info_callbacks._update_text_values(result)

    assert mocks.mock_calls == [
        call.title('as_string:My Title'),
        call.year('as_string:2012'),
        call.genre('as_string:llamadrama'),
        call.cast("as_string:('her', 'that guy')"),
    ]


@pytest.mark.asyncio
async def test__InfoCallbacks__update_awaitable_values(info_callbacks, mocker):
    mocks = Mock()
    info_callbacks._callbacks = {
        'title': mocks.title,
        'year': mocks.year,
        'genre': mocks.genre,
        'description': mocks.description,
        'cast': mocks.cast,
        'director': mocks.director,
    }
    mocker.patch.object(info_callbacks, '_call_callback')

    async def get_description():
        return 'my description'

    async def get_director():
        return 'mister dude'

    result = Mock(
        title='My Title',
        year='2012',
        genre='llamadrama',
        description=get_description,
        cast=('her', 'that guy'),
        director=get_director,
    )

    await info_callbacks._update_awaitable_values(result)

    assert info_callbacks._call_callback.call_args_list == [
        call(
            value_getter=get_description,
            callback=info_callbacks._callbacks['description'],
            cache_key=(result.id, 'description'),
        ),
        call(
            value_getter=get_director,
            callback=info_callbacks._callbacks['director'],
            cache_key=(result.id, 'director'),
        ),
    ]


@pytest.mark.asyncio
async def test__InfoCallbacks__call_callback_gets_value_from_cache(info_callbacks, mocker):
    mocks = Mock(
        value_getter=AsyncMock(return_value='The Value'),
        callback=Mock(),
    )
    mocks.attach_mock(mocker.patch('asyncio.sleep'), 'sleep')

    info_callbacks._cache[('id', 'key')] = 'The Cached Value'

    await info_callbacks._call_callback(
        callback=mocks.callback,
        value_getter=mocks.value_getter,
        cache_key=('id', 'key'),
    )
    assert mocks.mock_calls == [
        call.callback('The Cached Value'),
    ]
    assert info_callbacks._cache[('id', 'key')] == 'The Cached Value'


@pytest.mark.asyncio
async def test__InfoCallbacks__call_callback_gets_value_from_value_getter(info_callbacks, mocker):
    mocks = Mock(
        value_getter=AsyncMock(return_value='The Value'),
        callback=Mock(),
    )
    mocks.attach_mock(mocker.patch('asyncio.sleep'), 'sleep')

    info_callbacks._cache.clear()
    await info_callbacks._call_callback(
        cache_key=('id', 'key'),
        value_getter=mocks.value_getter,
        callback=mocks.callback,
    )

    assert mocks.mock_calls == [
        call.callback(Ellipsis),
        call.sleep(info_callbacks._delay_between_updates),
        call.value_getter(),
        call.callback('The Value'),
    ]
    assert info_callbacks._cache[('id', 'key')] == 'The Value'


@pytest.mark.asyncio
async def test__InfoCallbacks__call_callback_handles_RequestError(info_callbacks, mocker):
    mocks = Mock(
        value_getter=AsyncMock(side_effect=errors.RequestError('Nah')),
        callback=Mock(),
    )
    mocks.attach_mock(mocker.patch('asyncio.sleep'), 'sleep')
    info_callbacks._error_callback = mocks.error_callback

    info_callbacks._cache.clear()
    await info_callbacks._call_callback(
        callback=mocks.callback,
        value_getter=mocks.value_getter,
        cache_key=('id', 'key'),
    )
    assert mocks.mock_calls == [
        call.callback(Ellipsis),
        call.sleep(info_callbacks._delay_between_updates),
        call.value_getter(),
        call.callback(''),
        call.error_callback(errors.RequestError('Nah')),
    ]
    assert info_callbacks._cache == {}


def test__InfoCallbacks__value_as_string_with_string(info_callbacks):
    assert info_callbacks._value_as_string('foo bar baz') == 'foo bar baz'

def test__InfoCallbacks__value_as_string_with_iterable(info_callbacks):
    assert info_callbacks._value_as_string(('foo', 'bar', 'baz')) == 'foo, bar, baz'
    assert info_callbacks._value_as_string(['foo', 2, {3}]) == 'foo, 2, {3}'

def test__InfoCallbacks__value_as_string_with_other_type(info_callbacks):
    assert info_callbacks._value_as_string(type) == str(type)
