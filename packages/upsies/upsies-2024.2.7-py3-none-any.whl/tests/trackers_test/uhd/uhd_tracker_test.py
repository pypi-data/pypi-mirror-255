import datetime
import re
from unittest.mock import AsyncMock, Mock, PropertyMock, call

import bs4
import pytest

from upsies import __project_name__, errors
from upsies.trackers.uhd import UhdTracker, UhdTrackerConfig, UhdTrackerJobs


@pytest.fixture
def make_tracker():
    def make_tracker(**kwargs):
        options = {
            'username': 'bunny',
            'password': 'hunter2',
            'base_url': 'http://uhd.local',
        }
        options.update(kwargs)
        return UhdTracker(options=options)

    return make_tracker


@pytest.fixture
def tracker(make_tracker):
    return make_tracker()


def test_name_attribute():
    assert UhdTracker.name == 'uhd'


def test_label_attribute():
    assert UhdTracker.label == 'UHD'


def test_TrackerConfig_attribute():
    assert UhdTracker.TrackerConfig is UhdTrackerConfig


def test_TrackerJobs_attribute():
    assert UhdTracker.TrackerJobs is UhdTrackerJobs


def test_base_url_attribute(make_tracker):
    tracker = make_tracker(base_url='http://foo.local')
    assert tracker._base_url == 'http://foo.local'


def test_login_url_attribute(make_tracker):
    tracker = make_tracker(base_url='http://foo.local')
    assert tracker._login_url == 'http://foo.local/login.php'


def test_logout_url_attribute(make_tracker):
    tracker = make_tracker(base_url='http://foo.local')
    assert tracker._logout_url == 'http://foo.local/logout.php'


def test_ajax_url_attribute(make_tracker):
    tracker = make_tracker(base_url='http://foo.local')
    assert tracker._ajax_url == 'http://foo.local/ajax.php'


def test_upload_url_attribute(make_tracker):
    tracker = make_tracker(base_url='http://foo.local')
    assert tracker._upload_url == 'http://foo.local/upload.php'


def test_torrents_url_attribute(make_tracker):
    tracker = make_tracker(base_url='http://foo.local')
    assert tracker._torrents_url == 'http://foo.local/torrents.php'


@pytest.mark.parametrize('method', ('POST', 'Get'))
@pytest.mark.parametrize(
    argnames='exception, error_prefix, exp_exception',
    argvalues=(
        (None, 'Oh no', None),
        (errors.RequestError('Upload failed'), 'Oh no', errors.RequestError('Oh no: Upload failed')),
        (errors.RequestError('Upload failed'), '', errors.RequestError('Upload failed')),
        (RuntimeError('Everything failed'), 'OMG', RuntimeError('Everything failed')),
    ),
    ids=lambda v: repr(v),
)
@pytest.mark.asyncio
async def test__request(
        method,
        exception, error_prefix, exp_exception,
        tracker, mocker,
):
    kwargs = {'foo': 'bar'}

    mocks = Mock()
    mocks.attach_mock(mocker.patch('upsies.utils.http.get', AsyncMock(return_value='GET response')), 'get')
    mocks.attach_mock(mocker.patch('upsies.utils.http.post', AsyncMock(return_value='POST response')), 'post')

    if exp_exception:
        getattr(mocks, method.lower()).side_effect = exception
        with pytest.raises(type(exp_exception), match=rf'^{re.escape(str(exp_exception))}$'):
            await tracker._request(method, 'asdf', error_prefix=error_prefix, **kwargs)
    else:
        return_value = await tracker._request(method, 'asdf', error_prefix=error_prefix, **kwargs)
        assert return_value == f'{method.upper()} response'

    assert mocks.mock_calls == [
        getattr(call, method.lower())('asdf', user_agent=True, cache=False, foo='bar')
    ]


@pytest.mark.asyncio
async def test__failed_to_find_error(tracker, mocker):
    msg_prefix = 'WTF'
    doc = Mock()
    exp_filepath = 'WTF.uhd.html'
    exp_msg = (
        f'{msg_prefix}: '
        f'No error message found (dumped HTML response to {exp_filepath})'
    )

    html_dump_mock = mocker.patch('upsies.utils.html.dump')

    with pytest.raises(RuntimeError, match=rf'^{re.escape(exp_msg)}$'):
        tracker._failed_to_find_error(doc, msg_prefix)

    html_dump_mock.call_args_list == [call(doc, exp_filepath)]


@pytest.fixture
def mocks_for_login(tracker, mocker):
    mocks = Mock()
    mocks.attach_mock(mocker.patch.object(tracker, '_request'), '_request')
    mocks.attach_mock(mocker.patch.object(tracker, '_confirm_login'), '_confirm_login')
    return mocks

@pytest.mark.asyncio
async def test_login_without_username(mocks_for_login, tracker):
    del tracker.options['username']
    with pytest.raises(errors.RequestError, match=r'^Login failed: No username configured$'):
        await tracker._login()
    assert mocks_for_login.mock_calls == []

@pytest.mark.asyncio
async def test_login_without_password(mocks_for_login, tracker):
    del tracker.options['password']
    with pytest.raises(errors.RequestError, match=r'^Login failed: No password configured$'):
        await tracker._login()
    assert mocks_for_login.mock_calls == []

@pytest.mark.asyncio
async def test_login_succeeds(mocks_for_login, tracker):
    await tracker._login()
    assert mocks_for_login.mock_calls == [
        call._request(
            method='POST',
            url=tracker._login_url,
            data={
                'username': tracker.options['username'],
                'password': tracker.options['password'],
                'two_step': '',  # 2FA
                'login': 'Log in',
            },
            error_prefix='Login failed',
        ),
        call._confirm_login(mocks_for_login._request.return_value),
    ]


@pytest.mark.parametrize(
    argnames='response, exp_result, exp_failed_to_find_error_called, exp_auth',
    argvalues=(
        (
            '<a href="logout.php?foo=bar&auth=d34db33f">Logout</a>',
            None,
            False,
            'd34db33f',
        ),
        (
            '<html></html>',
            RuntimeError('Login failed: No error message found'),
            True,
            None,
        ),
        (
            (
                '<form action="login.php">'
                '<span class="warning"><br/>Authentication failed<br /><br /></span>'
                '<br/>You have <span class="info">5</span> attempts remaining.<br /><br />'
                '<strong>WARNING:</strong> You will be banned for 6 hours after your attempts run out!<br /><br />'
                '<table class="layout">'
                'IGNORED MORE TEXT'
                '</table>'
            ),
            errors.RequestError(
                'Login failed: Authentication failed\n'
                'You have 5 attempts remaining.\n'
                'WARNING: You will be banned for 6 hours after your attempts run out!'
            ),
            False,
            None,
        ),
    ),
    ids=lambda v: repr(v),
)
def test__confirm_login(response, exp_result, exp_failed_to_find_error_called, exp_auth, tracker, mocker):
    mocker.patch.object(tracker, '_failed_to_find_error')
    exp_doc = bs4.BeautifulSoup(response, features='html.parser')

    if isinstance(exp_result, Exception):
        tracker._failed_to_find_error.side_effect = exp_result
        with pytest.raises(type(exp_result), match=rf'^{re.escape(str(exp_result))}$'):
            tracker._confirm_login(response)
    else:
        return_value = tracker._confirm_login(response)
        assert return_value == exp_result

    if exp_failed_to_find_error_called:
        assert tracker._failed_to_find_error.call_args_list == [
            call(exp_doc, 'Login failed'),
        ]
    else:
        assert tracker._failed_to_find_error.call_args_list == []

    if exp_auth is None:
        assert not hasattr(tracker, '_auth')
    else:
        assert tracker._auth == exp_auth


@pytest.mark.parametrize(
    argnames='request_exception',
    argvalues=(
        None,
        errors.RequestError('Connection refused'),
        RuntimeError('Connection exploded'),
    ),
    ids=lambda v: repr(v),
)
@pytest.mark.asyncio
async def test__logout(request_exception, tracker, mocker):
    mocker.patch.object(tracker, '_request', side_effect=request_exception)
    auth = tracker._auth = 'd34db33f'

    if request_exception:
        with pytest.raises(type(request_exception), match=rf'^{re.escape(str(request_exception))}$'):
            await tracker._logout()
    else:
        await tracker._logout()

    assert tracker._request.call_args_list == [call(
        method='GET',
        url=tracker._logout_url,
        params={'auth': auth},
        error_prefix='Logout failed',
    )]
    assert not hasattr(tracker, '_auth')


@pytest.mark.asyncio
async def test_get_announce_url_from_config(tracker, mocker):
    mocks = Mock()
    mocks.attach_mock(mocker.patch.object(tracker, 'login'), 'login')
    mocks.attach_mock(mocker.patch.object(tracker, '_request'), '_request')
    mocker.patch.object(type(tracker), 'options', PropertyMock(return_value={
        'announce_url': 'http://foo.bar/announce',
    }))

    announce_url = await tracker.get_announce_url()
    assert announce_url == 'http://foo.bar/announce'
    assert mocks.mock_calls == []


@pytest.mark.parametrize(
    argnames='html, exp_result',
    argvalues=(
        (
            '<html><input value="http://foo.local:123/announce" /></html>',
            'http://foo.local:123/announce',
        ),
        (
            '<html><input value="https://foo.local:123/announce?d34db33f" /></html>',
            'https://foo.local:123/announce?d34db33f',
        ),
        (
            '<html><input value="https://foo.local:123/announce/d34db33f" /></html>',
            'https://foo.local:123/announce/d34db33f',
        ),
        (
            '<html><input value="https://foo.local:123/d34db33f/announce" /></html>',
            'https://foo.local:123/d34db33f/announce',
        ),
        (
            '<html><input value="https://foo.local:123/anon" /></html>',
            errors.RequestError(
                'Failed to find announce URL - set it manually: '
                f'{__project_name__} set trackers.uhd.announce_url YOUR_URL',
            ),
        ),
        (
            '<html><input value="" /></html>',
            errors.RequestError(
                'Failed to find announce URL - set it manually: '
                f'{__project_name__} set trackers.uhd.announce_url YOUR_URL',
            ),
        ),
        (
            '<html><input /></html>',
            errors.RequestError(
                'Failed to find announce URL - set it manually: '
                f'{__project_name__} set trackers.uhd.announce_url YOUR_URL',
            ),
        ),
        (
            '<html><div>hello</div></html>',
            errors.RequestError(
                'Failed to find announce URL - set it manually: '
                f'{__project_name__} set trackers.uhd.announce_url YOUR_URL',
            ),
        ),
    ),
)
@pytest.mark.asyncio
async def test_get_announce_url_from_website(html, exp_result, tracker, mocker):
    mocks = Mock()
    mocks.attach_mock(mocker.patch.object(tracker, 'login'), 'login')
    mocks.attach_mock(mocker.patch.object(tracker, '_request', return_value=html), '_request')
    tracker.options.pop('announce_url', None)

    if isinstance(exp_result, BaseException):
        with pytest.raises(type(exp_result), match=rf'^{re.escape(str(exp_result))}$'):
            await tracker.get_announce_url()
    else:
        return_value = await tracker.get_announce_url()
        assert return_value == exp_result

    assert mocks.mock_calls == [
        call.login(),
        call._request(method='GET', url=tracker._upload_url),
    ]


@pytest.fixture
def mocks_for_get_uhd_info(tracker, mocker):
    mocks = Mock()
    mocks.attach_mock(mocker.patch.object(tracker, '_get_uhd_info'), '_get_uhd_info')
    mocks.attach_mock(mocker.patch('asyncio.sleep'), 'sleep')
    return mocks

@pytest.mark.asyncio
async def test_get_uhd_info_with_unknown_imdb_id(mocks_for_get_uhd_info, tracker):
    with pytest.raises(AssertionError, match=r'^IMDb ID is not available yet$'):
        await tracker.get_uhd_info(None)
    assert mocks_for_get_uhd_info.mock_calls == []

@pytest.mark.asyncio
async def test_get_uhd_info_with_readily_available_info(mocks_for_get_uhd_info, tracker):
    imdb_id = 'tt123456'
    mocks_for_get_uhd_info._get_uhd_info.return_value = {'error': '0', 'the': 'info'}

    return_value = await tracker.get_uhd_info(imdb_id)
    assert return_value == {'error': '0', 'the': 'info'}
    assert mocks_for_get_uhd_info.mock_calls == [
        call._get_uhd_info(imdb_id),
    ]

@pytest.mark.parametrize(
    argnames='imdb_id, responses, exp_mock_calls',
    argvalues=(
        (
            'tt123456',
            (
                {'error': '1', 'message': 'Fetching'},
                {'error': '0', 'the': 'info'},
            ),
            [
                call._get_uhd_info('tt123456'),
                call.sleep(6),
                call._get_uhd_info('tt123456'),
            ],
        ),
        (
            'tt123456',
            (
                {'error': '1', 'message': 'Fetching'},
                {'error': '1', 'message': 'Loading'},
                {'error': '0', 'the': 'info'},
            ),
            [
                call._get_uhd_info('tt123456'),
                call.sleep(6),
                call._get_uhd_info('tt123456'),
                call.sleep(5),
                call._get_uhd_info('tt123456'),
            ],
        ),
        (
            'tt123456',
            (
                {'error': '1', 'message': 'Fetching'},
                {'error': '1', 'message': 'Loading'},
                {'error': '1', 'message': 'Still loading'},
                {'error': '0', 'the': 'info'},
            ),
            [
                call._get_uhd_info('tt123456'),
                call.sleep(6),
                call._get_uhd_info('tt123456'),
                call.sleep(5),
                call._get_uhd_info('tt123456'),
                call.sleep(4),
                call._get_uhd_info('tt123456'),
            ],
        ),
        (
            'tt123456',
            (
                {'error': '1', 'message': 'Fetching'},
                {'error': '1', 'message': 'Loading'},
                {'error': '1', 'message': 'Still loading'},
                {'error': '1', 'message': '...'},
                {'error': '0', 'the': 'info'},
            ),
            [
                call._get_uhd_info('tt123456'),
                call.sleep(6),
                call._get_uhd_info('tt123456'),
                call.sleep(5),
                call._get_uhd_info('tt123456'),
                call.sleep(4),
                call._get_uhd_info('tt123456'),
                call.sleep(3),
                call._get_uhd_info('tt123456'),
            ],
        ),
        (
            'tt123456',
            (
                {'error': '1', 'message': 'Fetching'},
                {'error': '1', 'message': 'Loading'},
                {'error': '1', 'message': 'Still loading'},
                {'error': '1', 'message': '...'},
                {'error': '1', 'message': '!!!'},
                {'error': '0', 'the': 'info'},
            ),
            [
                call._get_uhd_info('tt123456'),
                call.sleep(6),
                call._get_uhd_info('tt123456'),
                call.sleep(5),
                call._get_uhd_info('tt123456'),
                call.sleep(4),
                call._get_uhd_info('tt123456'),
                call.sleep(3),
                call._get_uhd_info('tt123456'),
                call.sleep(3),
                call._get_uhd_info('tt123456'),
            ],
        ),
    ),
    ids=lambda v: repr(v),
)
@pytest.mark.asyncio
async def test_get_uhd_info_with_info_getting_fetched_by_server(
        imdb_id, responses, exp_mock_calls,
        mocks_for_get_uhd_info, tracker,
):
    mocks_for_get_uhd_info._get_uhd_info.side_effect = responses

    return_value = await tracker.get_uhd_info(imdb_id)
    assert return_value == responses[-1]
    assert mocks_for_get_uhd_info.mock_calls == exp_mock_calls

@pytest.mark.asyncio
async def test_get_uhd_info_with_server_fetching_too_long(mocks_for_get_uhd_info, tracker):
    imdb_id = 'tt123456'
    mocks_for_get_uhd_info._get_uhd_info.side_effect = (
        {'error': '1', 'message': 'Fetching'},
        {'error': '1', 'message': 'Fetching'},
        {'error': '1', 'message': 'Fetching'},
        {'error': '1', 'message': 'Fetching'},
        {'error': '1', 'message': 'Fetching'},
        {'error': '1', 'message': 'Fetching'},
        {'error': '1', 'message': 'Fetching'},
        {'error': '1', 'message': 'Fetching'},
        {'error': '1', 'message': 'Fetching'},
        {'error': '1', 'message': 'Fetching'},
        {'error': '1', 'message': 'Fetching'},
        {'error': '1', 'message': 'Fetching'},
    )

    return_value = await tracker.get_uhd_info(imdb_id)
    assert return_value == {}
    assert mocks_for_get_uhd_info.mock_calls == [
        call._get_uhd_info(imdb_id),
        call.sleep(6),
        call._get_uhd_info(imdb_id),
        call.sleep(5),
        call._get_uhd_info(imdb_id),
        call.sleep(4),
        call._get_uhd_info(imdb_id),
        call.sleep(3),
        call._get_uhd_info(imdb_id),
        call.sleep(3),
        call._get_uhd_info(imdb_id),
        call.sleep(3),
        call._get_uhd_info(imdb_id),
        call.sleep(3),
        call._get_uhd_info(imdb_id),
        call.sleep(3),
        call._get_uhd_info(imdb_id),
        call.sleep(3),
        call._get_uhd_info(imdb_id),
    ]

@pytest.mark.asyncio
async def test_get_uhd_info_with_server_request_error(mocks_for_get_uhd_info, tracker):
    imdb_id = 'tt123456'
    mocks_for_get_uhd_info._get_uhd_info.side_effect = (
        {'error': '1', 'message': 'Fetching'},
        errors.RequestError('Connection refused'),
    )

    return_value = await tracker.get_uhd_info(imdb_id)
    assert return_value == {}
    assert mocks_for_get_uhd_info.mock_calls == [
        call._get_uhd_info(imdb_id),
        call.sleep(6),
        call._get_uhd_info(imdb_id),
    ]


@pytest.mark.asyncio
async def test__get_uhd_info(tracker, mocker):
    imdb_id = 'tt123456'
    mocks = Mock()
    mocks.response.json.return_value = {'the': 'info'}
    mocks.now.return_value = datetime.datetime(2012, 11, 10, 9, 8, 7, 654321)
    mocker.patch('datetime.datetime', Mock(now=mocks.now))
    mocks.attach_mock(mocker.patch.object(tracker, '_request', return_value=mocks.response), '_request')

    return_value = await tracker._get_uhd_info(imdb_id)
    assert return_value == {'the': 'info'}
    assert mocks.mock_calls == [
        call.now(datetime.timezone.utc),
        call._request(
            method='GET',
            url=tracker._ajax_url,
            params={
                'action': 'imdb_fetch',
                'imdbid': imdb_id,
                '_': int(mocks.now.return_value.timestamp() * 1000),
            },
        ),
        call.response.json(),
    ]


@pytest.fixture
def mocks_for_upload(tracker, mocker):
    tracker_jobs = Mock(
        post_data={'post': 'data'},
        post_files={'post': 'files'},
    )
    mocker.patch.object(type(tracker), 'is_logged_in', PropertyMock(return_value=True))
    mocker.patch.object(type(tracker), '_auth', PropertyMock(return_value='d34db33f'), create=True)
    mocks = Mock()
    mocks.attach_mock(mocker.patch.object(tracker, '_request'), '_request')
    mocks.attach_mock(mocker.patch.object(tracker, '_handle_upload_response'), '_handle_upload_response')
    return mocks, tracker_jobs

@pytest.mark.asyncio
async def test_upload_if_not_logged_in(mocks_for_upload, tracker, mocker):
    mocks, tracker_jobs = mocks_for_upload
    mocker.patch.object(type(tracker), 'is_logged_in', PropertyMock(return_value=False))
    with pytest.raises(AssertionError):
        await tracker.upload(tracker_jobs)
    assert mocks.mock_calls == []

@pytest.mark.asyncio
async def test_upload_if_logged_in(mocks_for_upload, tracker):
    mocks, tracker_jobs = mocks_for_upload
    await tracker.upload(tracker_jobs)
    assert mocks.mock_calls == [
        call._request(
            method='POST',
            url=tracker._upload_url,
            data=tracker_jobs.post_data,
            files=tracker_jobs.post_files,
            follow_redirects=False,
        ),
        call._handle_upload_response(mocks._request.return_value),
    ]


class MockResponse(str):
    def __new__(cls, *args, headers={}, **kwargs):
        self = super().__new__(cls, *args, **kwargs)
        self.headers = headers
        return self

@pytest.fixture
def mocks_for__handle_post_response(tracker, mocker):
    mocks = Mock()
    mocks.attach_mock(mocker.patch.object(tracker, '_failed_to_find_error'), '_failed_to_find_error')
    return mocks

@pytest.mark.parametrize('parameters_prefix', ('torrents.php', '{tracker._torrents_url}'))
def test__handle_upload_response_with_redirect_response_to_torrent_url(
        parameters_prefix,
        mocks_for__handle_post_response, tracker, mocker,
):
    response = MockResponse(
        headers={'Location': parameters_prefix.format(tracker=tracker) + '?id=123456'}
    )
    return_value = tracker._handle_upload_response(response)
    assert return_value == tracker._torrents_url + '?id=123456'
    assert mocks_for__handle_post_response.mock_calls == []

def test__handle_upload_response_with_redirect_response_to_nontorrent_url(mocks_for__handle_post_response, tracker, mocker):
    response = MockResponse(
        '<html></html>',
        headers={'Location': 'https://evil.org' + '?id=123456'}
    )
    return_value = tracker._handle_upload_response(response)
    assert return_value is None
    assert mocks_for__handle_post_response.mock_calls == [
        call._failed_to_find_error(bs4.BeautifulSoup(response, features='html.parser'), 'Upload failed'),
    ]

def test__handle_upload_response_without_redirect_response_and_error_message_found(
        mocks_for__handle_post_response, tracker, mocker,
):
    response = MockResponse(
        '<html>'
        '  <div id="scontent">'
        '    <div class="thin">'
        '      <p>Your personal announce URL is ...</p>'
        '      <p>This is <b>the</b> error message!</p>'
        '    </div>'
        '  </div>'
        '</html>'
    )
    exp_msg = 'Upload failed: This is the error message!'
    with pytest.raises(errors.RequestError, match=rf'^{re.escape(exp_msg)}$'):
        tracker._handle_upload_response(response)
    assert mocks_for__handle_post_response.mock_calls == []

def test__handle_upload_response_without_redirect_response_and_no_error_message_found(
        mocks_for__handle_post_response, tracker, mocker,
):
    response = MockResponse(
        '<html>'
        '  <div id="scontent">'
        '    <div class="wide">'
        '      Something that is not an error message.'
        '    </div>'
        '  </div>'
        '</html>'
    )
    tracker._handle_upload_response(response)
    assert mocks_for__handle_post_response.mock_calls == [
        call._failed_to_find_error(bs4.BeautifulSoup(response, features='html.parser'), 'Upload failed'),
    ]
