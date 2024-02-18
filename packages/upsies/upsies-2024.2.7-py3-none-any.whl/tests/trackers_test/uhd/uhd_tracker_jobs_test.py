import re
from unittest.mock import AsyncMock, Mock, PropertyMock, call

import pytest

from upsies import __homepage__, __project_name__, errors, utils
from upsies.trackers import uhd


@pytest.fixture
def tracker():
    tracker = Mock()
    tracker.name = 'uhd'
    return tracker


@pytest.fixture
def imghost():
    class MockImageHost(utils.imghosts.base.ImageHostBase):
        name = 'mock image host'
        default_config = {}
        _upload_image = AsyncMock()

    return MockImageHost()


@pytest.fixture
def uhd_tracker_jobs(imghost, tracker, tmp_path, mocker):
    content_path = tmp_path / 'Foo 2000 1080p BluRay x264-ASDF'

    uhd_tracker_jobs = uhd.UhdTrackerJobs(
        content_path=str(content_path),
        tracker=tracker,
        image_hosts=(imghost,),
        btclient=Mock(),
        torrent_destination=str(tmp_path / 'destination'),
        common_job_args={
            'home_directory': str(tmp_path / 'home_directory'),
            'ignore_cache': True,
        },
        options=None,
    )

    return uhd_tracker_jobs


@pytest.fixture
def mock_job_attributes(uhd_tracker_jobs, mocker):
    job_attrs = (
        # Interactive jobs
        'imdb_job',
        'type_job',
        'year_job',
        'quality_job',
        'version_job',
        'source_job',
        'codec_job',
        'hdr_format_job',
        'tags_job',
        'poster_job',
        'trailer_job',
        'season_job',
        'automerge_group_job',
        'scene_check_job',

        # Background jobs
        'create_torrent_job',
        'mediainfo_job',
        'screenshots_job',
        'upload_screenshots_job',
        'description_job',
    )
    for job_attr in job_attrs:
        mocker.patch.object(
            type(uhd_tracker_jobs),
            job_attr,
            PropertyMock(return_value=Mock(attr=job_attr, prejobs=())),
        )


def test_jobs_before_upload_items(uhd_tracker_jobs, mock_job_attributes, mocker):
    assert tuple(job.attr for job in uhd_tracker_jobs.jobs_before_upload) == (
        # Interactive jobs
        'imdb_job',
        'type_job',
        'year_job',
        'quality_job',
        'version_job',
        'source_job',
        'codec_job',
        'hdr_format_job',
        'tags_job',
        'poster_job',
        'trailer_job',
        'season_job',
        'automerge_group_job',
        'scene_check_job',

        # Background jobs
        'create_torrent_job',
        'mediainfo_job',
        'screenshots_job',
        'upload_screenshots_job',
        'description_job',
    )
    assert uhd_tracker_jobs.poster_job.prejobs == (
        uhd_tracker_jobs.imdb_job,
    )


def test_isolated_jobs__only_description(uhd_tracker_jobs, mock_job_attributes, mocker):
    mocker.patch.object(type(uhd_tracker_jobs), 'options', PropertyMock(return_value={'only_description': True}))
    mocker.patch.object(uhd_tracker_jobs, 'get_job_and_dependencies')
    assert uhd_tracker_jobs.isolated_jobs is uhd_tracker_jobs.get_job_and_dependencies.return_value
    assert uhd_tracker_jobs.get_job_and_dependencies.call_args_list == [
        call(uhd_tracker_jobs.description_job, uhd_tracker_jobs.screenshots_job)
    ]

def test_isolated_jobs__no_isolated_jobs(uhd_tracker_jobs, mock_job_attributes, mocker):
    mocker.patch.object(type(uhd_tracker_jobs), 'options', PropertyMock(return_value={}))
    mocker.patch.object(uhd_tracker_jobs, 'get_job_and_dependencies')
    assert uhd_tracker_jobs.isolated_jobs == ()
    assert uhd_tracker_jobs.get_job_and_dependencies.call_args_list == []


def test_type_job(uhd_tracker_jobs, mocker):
    mocker.patch.object(type(uhd_tracker_jobs), 'imdb_job', PropertyMock())
    ChoiceJob_mock = mocker.patch('upsies.jobs.dialog.ChoiceJob')
    mocker.patch.object(uhd_tracker_jobs, 'get_job_name')
    mocker.patch.object(uhd_tracker_jobs, 'make_precondition')
    mocker.patch.object(uhd_tracker_jobs, 'common_job_args', return_value={'common_job_arg': 'common job argument'})

    assert uhd_tracker_jobs.type_job is ChoiceJob_mock.return_value
    assert ChoiceJob_mock.call_args_list == [call(
        name=uhd_tracker_jobs.get_job_name.return_value,
        label='Type',
        precondition=uhd_tracker_jobs.make_precondition.return_value,
        prejobs=(
            uhd_tracker_jobs.imdb_job,
        ),
        autodetect=uhd_tracker_jobs.autodetect_type,
        autofinish=True,
        options=(
            ('Movie', '0'),
            ('TV', '2'),
        ),
        common_job_arg='common job argument',
    )]
    assert uhd_tracker_jobs.get_job_name.call_args_list == [call('type')]
    assert uhd_tracker_jobs.make_precondition.call_args_list == [call('type_job')]
    assert uhd_tracker_jobs.common_job_args.call_args_list == [call(ignore_cache=True)]


@pytest.mark.parametrize(
    argnames='imdb_job, imdb, exp_return_value, exp_type_calls',
    argvalues=(
        (
            Mock(is_finished=True, output=()),
            Mock(type=AsyncMock(return_value=utils.release.ReleaseType.movie)),
            None,
            [],
        ),
        (
            Mock(output=('tt123456',)),
            Mock(type=AsyncMock(return_value=utils.release.ReleaseType.movie)),
            'Movie',
            [call('tt123456')],
        ),
        (
            Mock(output=('tt123456',)),
            Mock(type=AsyncMock(return_value=utils.release.ReleaseType.season)),
            'TV',
            [call('tt123456')],
        ),
        (
            Mock(output=('tt123456',)),
            Mock(type=AsyncMock(return_value=utils.release.ReleaseType.episode)),
            'TV',
            [call('tt123456')],
        ),
        (
            Mock(output=('tt123456',)),
            Mock(type=AsyncMock(return_value=utils.release.ReleaseType.unknown)),
            None,
            [call('tt123456')],
        ),
    ),
    ids=lambda v: str(v),
)
@pytest.mark.asyncio
async def test_autodetect_type(
        imdb_job, imdb,
        exp_return_value, exp_type_calls,
        uhd_tracker_jobs, mocker,
):
    mocker.patch.object(type(uhd_tracker_jobs), 'imdb_job', PropertyMock(return_value=imdb_job))
    mocker.patch.object(type(uhd_tracker_jobs), 'imdb', PropertyMock(return_value=imdb))

    return_value = await uhd_tracker_jobs.autodetect_type('job_')
    assert return_value == exp_return_value
    assert uhd_tracker_jobs.imdb.type.call_args_list == exp_type_calls


@pytest.mark.parametrize(
    argnames='type_job, exp_return_value',
    argvalues=(
        (
            Mock(is_finished=False, output=('Movie',)),
            None,
        ),
        (
            Mock(is_finished=True, output=()),
            None,
        ),
        (
            Mock(is_finished=True, output=('Movie',)),
            utils.release.ReleaseType.movie,
        ),
        (
            Mock(is_finished=True, output=('TV',)),
            utils.release.ReleaseType.season,
        ),
    ),
    ids=('Undetermined', 'Undetermined', 'Movie', 'TV'),
)
def test_user_confirmed_type(
        type_job, exp_return_value,
        uhd_tracker_jobs, mocker,
):
    mocker.patch.object(type(uhd_tracker_jobs), 'type_job', PropertyMock(return_value=type_job))
    return_value = uhd_tracker_jobs.user_confirmed_type
    assert return_value == exp_return_value


def test_year_job(uhd_tracker_jobs, mocker):
    mocker.patch.object(type(uhd_tracker_jobs), 'imdb_job', PropertyMock())
    TextFieldJob_mock = mocker.patch('upsies.jobs.dialog.TextFieldJob')
    mocker.patch.object(uhd_tracker_jobs, 'get_job_name')
    mocker.patch.object(uhd_tracker_jobs, 'make_precondition')
    mocker.patch.object(uhd_tracker_jobs, 'get_job_and_dependencies')
    mocker.patch.object(uhd_tracker_jobs, 'common_job_args', return_value={'common_job_arg': 'common job argument'})

    assert uhd_tracker_jobs.year_job is TextFieldJob_mock.return_value
    assert TextFieldJob_mock.call_args_list == [call(
        name=uhd_tracker_jobs.get_job_name.return_value,
        label='Year',
        precondition=uhd_tracker_jobs.make_precondition.return_value,
        prejobs=(
            uhd_tracker_jobs.imdb_job,
        ),
        text=uhd_tracker_jobs.autodetect_year,
        nonfatal_exceptions=(
            errors.RequestError,
        ),
        normalizer=uhd_tracker_jobs.normalize_year,
        validator=uhd_tracker_jobs.validate_year,
        finish_on_success=True,
        common_job_arg='common job argument',
    )]
    assert uhd_tracker_jobs.get_job_name.call_args_list == [call('year')]
    assert uhd_tracker_jobs.make_precondition.call_args_list == [call('year_job')]
    assert uhd_tracker_jobs.common_job_args.call_args_list == [call()]


@pytest.mark.parametrize(
    argnames=(
        'imdb_id, uhd_info, imdb_year,'
        'exp_return_value, exp_mock_calls,'
    ),
    argvalues=(
        (
            'tt123456',
            {'year': '2012'},
            '2013',
            '2012',
            [
                call.get_uhd_info('tt123456'),
            ],
        ),
        (
            'tt123456',
            {'year': ''},
            '2013',
            '2013',
            [
                call.get_uhd_info('tt123456'),
                call.imdb_year('tt123456'),
            ],
        ),
        (
            'tt123456',
            {},
            '2013',
            '2013',
            [
                call.get_uhd_info('tt123456'),
                call.imdb_year('tt123456'),
            ],
        ),
        (
            'tt123456',
            {},
            '',
            None,
            [
                call.get_uhd_info('tt123456'),
                call.imdb_year('tt123456'),
            ],
        ),
    ),
    ids=lambda v: str(v),
)
@pytest.mark.asyncio
async def test_autodetect_year(
        imdb_id, uhd_info, imdb_year,
        exp_return_value, exp_mock_calls,
        uhd_tracker_jobs, mocker,
):
    mocks = Mock()
    mocker.patch.object(type(uhd_tracker_jobs), 'imdb_job', PropertyMock(return_value=Mock(is_finished=True)))
    mocker.patch.object(type(uhd_tracker_jobs), 'imdb_id', PropertyMock(return_value=imdb_id)),
    mocks.attach_mock(
        mocker.patch.object(uhd_tracker_jobs.tracker, 'get_uhd_info', AsyncMock(return_value=uhd_info)),
        'get_uhd_info',
    )
    mocks.attach_mock(
        mocker.patch.object(uhd_tracker_jobs.imdb, 'year', AsyncMock(return_value=imdb_year)),
        'imdb_year',
    )

    return_value = await uhd_tracker_jobs.autodetect_year()
    assert return_value == exp_return_value
    assert mocks.mock_calls == exp_mock_calls


@pytest.mark.parametrize(
    argnames='text, exp_return_value',
    argvalues=(
        ('123', '123'),
        (' 123  ', '123'),
        (' \n 123 \t ', '123'),
        ('\n\nfoo\t\t', 'foo'),
    ),
    ids=lambda v: str(v),
)
def test_normalize_year(text, exp_return_value, uhd_tracker_jobs):
    return_value = uhd_tracker_jobs.normalize_year(text)
    assert return_value == exp_return_value


@pytest.mark.parametrize(
    argnames='text, exp_exception',
    argvalues=(
        ('', ValueError('Year must not be empty.')),
        ('123foo', ValueError('Year must be a number.')),
        ('123.5', ValueError('Year must be a number.')),
        ('1799', ValueError('Year is not reasonable.')),
        ('2100', ValueError('Year is not reasonable.')),
        ('2012', None),
    ),
    ids=lambda v: str(v),
)
def test_validate_year(text, exp_exception, uhd_tracker_jobs):
    if exp_exception:
        with pytest.raises(type(exp_exception), match=rf'^{re.escape(str(exp_exception))}$'):
            uhd_tracker_jobs.validate_year(text)
    else:
        return_value = uhd_tracker_jobs.validate_year(text)
        assert return_value is None


def test_season_job(uhd_tracker_jobs, mocker):
    mocker.patch.object(type(uhd_tracker_jobs), 'imdb_job', PropertyMock())
    mocker.patch.object(type(uhd_tracker_jobs), 'type_job', PropertyMock())
    TextFieldJob_mock = mocker.patch('upsies.jobs.dialog.TextFieldJob')
    mocker.patch.object(uhd_tracker_jobs, 'get_job_name')
    mocker.patch.object(uhd_tracker_jobs, 'make_precondition')
    mocker.patch.object(uhd_tracker_jobs, 'get_job_and_dependencies')
    mocker.patch.object(uhd_tracker_jobs, 'common_job_args', return_value={'common_job_arg': 'common job argument'})

    assert uhd_tracker_jobs.season_job is TextFieldJob_mock.return_value
    assert TextFieldJob_mock.call_args_list == [call(
        name=uhd_tracker_jobs.get_job_name.return_value,
        label='Season',
        precondition=uhd_tracker_jobs.make_precondition.return_value,
        prejobs=(
            uhd_tracker_jobs.imdb_job,
            uhd_tracker_jobs.type_job,
        ),
        hidden=uhd_tracker_jobs.season_job_is_hidden,
        text=uhd_tracker_jobs.autodetect_season,
        normalizer=uhd_tracker_jobs.normalize_season,
        validator=uhd_tracker_jobs.validate_season,
        finish_on_success=True,
        common_job_arg='common job argument',
    )]
    assert uhd_tracker_jobs.get_job_name.call_args_list == [call('season')]
    assert uhd_tracker_jobs.make_precondition.call_args_list == [call('season_job')]
    assert uhd_tracker_jobs.common_job_args.call_args_list == [call()]


@pytest.mark.parametrize(
    argnames='user_confirmed_type, exp_return_value',
    argvalues=(
        (None, True),
        (utils.release.ReleaseType.season, False),
        (utils.release.ReleaseType.episode, False),
        (utils.release.ReleaseType.movie, True),

    ),
    ids=lambda v: str(v),
)
def test_season_job_is_hidden(user_confirmed_type, exp_return_value, uhd_tracker_jobs, mocker):
    mocker.patch.object(type(uhd_tracker_jobs), 'user_confirmed_type', PropertyMock(return_value=user_confirmed_type))
    return_value = uhd_tracker_jobs.season_job_is_hidden()
    assert return_value is exp_return_value


@pytest.mark.parametrize(
    argnames=(
        'user_confirmed_type, release_name,'
        'exp_return_value,'
    ),
    argvalues=(
        (
            utils.release.ReleaseType.season,
            Mock(only_season=None),
            None,
        ),
        (
            utils.release.ReleaseType.season,
            Mock(only_season=''),
            None,
        ),
        (
            utils.release.ReleaseType.season,
            Mock(only_season='12'),
            '12',
        ),
        (
            utils.release.ReleaseType.movie,
            Mock(only_season='12'),
            '',
        ),
    ),
    ids=lambda v: str(v),
)
@pytest.mark.asyncio
async def test_autodetect_season(
        user_confirmed_type, release_name,
        exp_return_value,
        uhd_tracker_jobs, mocker,
):
    mocker.patch.object(type(uhd_tracker_jobs), 'user_confirmed_type', PropertyMock(return_value=user_confirmed_type))
    mocker.patch.object(type(uhd_tracker_jobs), 'release_name', PropertyMock(return_value=release_name))

    return_value = await uhd_tracker_jobs.autodetect_season()
    assert return_value == exp_return_value


@pytest.mark.parametrize(
    argnames='text, exp_return_value',
    argvalues=(
        ('3', '3'),
        (' 3  ', '3'),
        (' \n 3 \t ', '3'),
        ('\n\nfoo\t\t', 'foo'),
    ),
    ids=lambda v: str(v),
)
def test_normalize_season(text, exp_return_value, uhd_tracker_jobs):
    return_value = uhd_tracker_jobs.normalize_season(text)
    assert return_value == exp_return_value


@pytest.mark.parametrize(
    argnames='text, exp_exception',
    argvalues=(
        ('', None),
        ('123foo', ValueError('Season must be a number.')),
        ('123.5', ValueError('Season must be a number.')),
        ('101', ValueError('Season is not reasonable.')),
        ('-1', ValueError('Season is not reasonable.')),
        ('0', None),
        ('1', None),
        ('99', None),
    ),
    ids=lambda v: str(v),
)
def test_validate_season(text, exp_exception, uhd_tracker_jobs):
    if exp_exception:
        with pytest.raises(type(exp_exception), match=rf'^{re.escape(str(exp_exception))}$'):
            uhd_tracker_jobs.validate_season(text)
    else:
        return_value = uhd_tracker_jobs.validate_season(text)
        assert return_value is None


@pytest.mark.parametrize(
    argnames='season_job, exp_return_value',
    argvalues=(
        (Mock(is_finished=False), None),
        (Mock(is_finished=True, output=()), None),
        (Mock(is_finished=True, output=('',)), None),
        (Mock(is_finished=True, output=('0',)), 0),
        (Mock(is_finished=True, output=('3',)), 3),
    ),
    ids=lambda v: str(v),
)
def test_season_number(season_job, exp_return_value, uhd_tracker_jobs, mocker):
    mocker.patch.object(type(uhd_tracker_jobs), 'season_job', PropertyMock(return_value=season_job))
    return_value = uhd_tracker_jobs.season_number
    assert return_value == exp_return_value


def test_quality_job(uhd_tracker_jobs, mocker):
    ChoiceJob_mock = mocker.patch('upsies.jobs.dialog.ChoiceJob')
    mocker.patch.object(uhd_tracker_jobs, 'get_job_name')
    mocker.patch.object(uhd_tracker_jobs, 'make_precondition')
    mocker.patch.object(uhd_tracker_jobs, 'get_job_and_dependencies')
    mocker.patch.object(uhd_tracker_jobs, 'common_job_args', return_value={'common_job_arg': 'common job argument'})

    assert uhd_tracker_jobs.quality_job is ChoiceJob_mock.return_value
    assert ChoiceJob_mock.call_args_list == [call(
        name=uhd_tracker_jobs.get_job_name.return_value,
        label='Quality',
        precondition=uhd_tracker_jobs.make_precondition.return_value,
        autodetect=uhd_tracker_jobs.autodetect_quality,
        autofinish=True,
        options=(
            ('mHD', 'mHD'),
            ('720p', '720p'),
            ('1080p', '1080p'),
            ('1080i', '1080i'),
            ('2160p', '2160p'),
            ('Other', 'Others'),
        ),
        common_job_arg='common job argument',
    )]
    assert uhd_tracker_jobs.get_job_name.call_args_list == [call('quality')]
    assert uhd_tracker_jobs.make_precondition.call_args_list == [call('quality_job')]
    assert uhd_tracker_jobs.common_job_args.call_args_list == [call()]


@pytest.mark.parametrize(
    argnames='resolution, exp_return_value',
    argvalues=(
        ('4320p', 'Other'),
        ('2160p', '2160p'),
        ('1080i', '1080i'),
        ('1080p', '1080p'),
        ('720p', '720p'),
        ('480p', 'Other'),
    ),
    ids=lambda v: str(v),
)
@pytest.mark.asyncio
async def test_autodetect_quality(
        resolution, exp_return_value,
        uhd_tracker_jobs, mocker,
):
    mocks = Mock()
    mocks.attach_mock(mocker.patch('upsies.utils.video.resolution', return_value=resolution), 'resolution')

    return_value = await uhd_tracker_jobs.autodetect_quality('job_')
    assert return_value == exp_return_value


def test_version_job(uhd_tracker_jobs, mocker):
    CustomJob_mock = mocker.patch('upsies.jobs.custom.CustomJob')
    mocker.patch.object(uhd_tracker_jobs, 'get_job_name')
    mocker.patch.object(uhd_tracker_jobs, 'make_precondition')
    mocker.patch.object(uhd_tracker_jobs, 'common_job_args', return_value={'common_job_arg': 'common job argument'})

    assert uhd_tracker_jobs.version_job is CustomJob_mock.return_value
    assert CustomJob_mock.call_args_list == [call(
        name=uhd_tracker_jobs.get_job_name.return_value,
        label='Version',
        precondition=uhd_tracker_jobs.make_precondition.return_value,
        worker=uhd_tracker_jobs.autodetect_version,
        no_output_is_ok=True,
        common_job_arg='common job argument',
    )]
    assert uhd_tracker_jobs.get_job_name.call_args_list == [call('version')]
    assert uhd_tracker_jobs.make_precondition.call_args_list == [call('version_job')]
    assert uhd_tracker_jobs.common_job_args.call_args_list == [call(ignore_cache=True)]


@pytest.mark.asyncio
async def test_autodetect_version(uhd_tracker_jobs, mocker):
    mocks = Mock(
        uncut=Mock(return_value=True),
        dc=Mock(return_value=False),
        extended=Mock(return_value=True),
        hybrid=Mock(return_value=False),
    )
    mocker.patch.object(uhd_tracker_jobs, 'version_map', {
        'Uncut': mocks.uncut,
        'DC': mocks.dc,
        'B&W': None,  # No autodetection
        'Extended': mocks.extended,
        'Hybrid': mocks.hybrid,
    })

    return_value = await uhd_tracker_jobs.autodetect_version('job_')
    assert return_value == {'Uncut', 'Extended'}


@pytest.mark.parametrize(
    argnames='version, release, exp_return_value',
    argvalues=(
        ("Director's Cut", Mock(edition=['foo', 'bar', 'baz']), False),
        ("Director's Cut", Mock(edition=['foo', "Director's Cut", 'baz']), True),
        ('Theatrical', Mock(edition=['foo', 'bar', 'baz']), False),
        ('Theatrical', Mock(edition=['foo', 'Theatrical Cut', 'baz']), True),
        ('Extended', Mock(edition=['foo', 'bar', 'baz']), False),
        ('Extended', Mock(edition=['foo', 'Extended Cut', 'baz']), True),
        ('IMAX', Mock(edition=['foo', 'bar', 'baz']), False),
        ('IMAX', Mock(edition=['foo', 'IMAX', 'baz']), True),
        ('Uncut', Mock(edition=['foo', 'bar', 'baz']), False),
        ('Uncut', Mock(edition=['foo', 'Uncut', 'baz']), True),
        ('TV Cut', Mock(), None),
        ('Unrated', Mock(edition=['foo', 'bar', 'baz']), False),
        ('Unrated', Mock(edition=['foo', 'Unrated', 'baz']), True),
        ('Remastered', Mock(edition=['foo', 'bar', 'baz']), False),
        ('Remastered', Mock(edition=['foo', 'Remastered', 'baz']), True),
        ('4K Remaster', Mock(edition=['foo', 'bar', 'baz']), False),
        ('4K Remaster', Mock(edition=['foo', '4k Remastered', 'baz']), True),
        ('4K Restoration', Mock(edition=['foo', 'bar', 'baz']), False),
        ('4K Restoration', Mock(edition=['foo', '4k Restored', 'baz']), True),
        ('B&W Version', Mock(), None),
        ('Criterion', Mock(edition=['foo', 'bar', 'baz']), False),
        ('Criterion', Mock(edition=['foo', 'Criterion Collection', 'baz']), True),
        ('2in1', Mock(edition=['foo', 'bar', 'baz']), False),
        ('2in1', Mock(edition=['foo', '2in1', 'baz']), True),
        ('3in1', Mock(edition=['foo', 'bar', 'baz']), False),
        ('3in1', Mock(edition=['foo', '3in1', 'baz']), True),
        ('Hybrid', Mock(source='BluRay'), False),
        ('Hybrid', Mock(source='Hybrid BluRay'), True),
        ('10-bit', Mock(path='path/to/release/content'), False),  # Tested in separate test
        ('Extras', Mock(), None),
    ),
    ids=lambda v: str(v),
)
def test_version_map(version, release, exp_return_value, uhd_tracker_jobs):
    if exp_return_value is None:
        assert uhd_tracker_jobs.version_map[version] is None
    else:
        is_version = uhd_tracker_jobs.version_map[version]
        assert is_version(release) is exp_return_value

@pytest.mark.parametrize(
    argnames='bit_depth, exp_return_value',
    argvalues=(
        (0, False),
        (8, False),
        (10, True),
        (11, False),
    ),
    ids=lambda v: str(v),
)
def test_version_map_bit_depth(bit_depth, exp_return_value, uhd_tracker_jobs, mocker):
    release = Mock(path='path/to/content')
    bit_depth_mock = mocker.patch('upsies.utils.video.bit_depth', return_value=bit_depth)
    is_version = uhd_tracker_jobs.version_map['10-bit']
    assert is_version(release) is exp_return_value
    assert bit_depth_mock.call_args_list == [call(release.path, default=None)]


def test_source_job(uhd_tracker_jobs, mocker):
    ChoiceJob_mock = mocker.patch('upsies.jobs.dialog.ChoiceJob')
    mocker.patch.object(uhd_tracker_jobs, 'get_job_name')
    mocker.patch.object(uhd_tracker_jobs, 'make_precondition')
    mocker.patch.object(uhd_tracker_jobs, 'common_job_args', return_value={'common_job_arg': 'common job argument'})

    assert uhd_tracker_jobs.source_job is ChoiceJob_mock.return_value
    assert ChoiceJob_mock.call_args_list == [call(
        name=uhd_tracker_jobs.get_job_name.return_value,
        label='Source',
        precondition=uhd_tracker_jobs.make_precondition.return_value,
        autodetect=uhd_tracker_jobs.autodetect_source,
        autofinish=True,
        options=(
            ('Blu-ray', 'Blu-ray'),
            ('Remux', 'Remux'),
            ('Encode', 'Encode'),
            ('WEB-DL', 'WEB-DL'),
            ('WEBRip', 'WEBRip'),
            ('HDRip', 'HDRip'),
            ('HDTV', 'HDTV'),
            ('Other', 'Others'),
        ),
        common_job_arg='common job argument',
    )]
    assert uhd_tracker_jobs.get_job_name.call_args_list == [call('source')]
    assert uhd_tracker_jobs.make_precondition.call_args_list == [call('source_job')]
    assert uhd_tracker_jobs.common_job_args.call_args_list == [call(ignore_cache=True)]


@pytest.mark.asyncio
async def test_autodetect_source(uhd_tracker_jobs, mocker):
    mocks = Mock(
        dvd=Mock(return_value=False),
        webrip=Mock(return_value=True),
        bluray=Mock(return_value=False),
        hdtv=Mock(return_value=True),
    )
    mocker.patch.object(uhd_tracker_jobs, 'source_map', {
        'DVD': mocks.dvd,
        'WEBRip': mocks.webrip,
        'BluRay': mocks.bluray,
        'HDTV': mocks.hdtv,
    })

    return_value = await uhd_tracker_jobs.autodetect_source('job_')
    assert return_value == 'WEBRip'

    mocks.webrip.return_value = False
    mocks.hdtv.return_value = False
    return_value = await uhd_tracker_jobs.autodetect_source('job_')
    assert return_value is None


@pytest.mark.parametrize(
    argnames='source, release, exp_return_value',
    argvalues=(
        ('Encode', Mock(source='foo BluRay baz'), True),
        ('Encode', Mock(source='foo BluRay baz'), True),
        ('Encode', Mock(source='foo bar baz'), False),
        ('Encode', Mock(source='foo HD-DVD baz'), True),
        ('WEB-DL', Mock(source='foo bar baz'), False),
        ('WEB-DL', Mock(source='foo WEB-DL baz'), True),
        ('WEBRip', Mock(source='foo bar baz'), False),
        ('WEBRip', Mock(source='foo WEBRip baz'), True),
    ),
    ids=lambda v: str(v),
)
def test_source_map(source, release, exp_return_value, uhd_tracker_jobs):
    is_source = uhd_tracker_jobs.source_map[source]
    assert is_source(release) is exp_return_value


def test_codec_job(uhd_tracker_jobs, mocker):
    ChoiceJob_mock = mocker.patch('upsies.jobs.dialog.ChoiceJob')
    mocker.patch.object(uhd_tracker_jobs, 'get_job_name')
    mocker.patch.object(uhd_tracker_jobs, 'make_precondition')
    mocker.patch.object(uhd_tracker_jobs, 'common_job_args', return_value={'common_job_arg': 'common job argument'})

    assert uhd_tracker_jobs.codec_job is ChoiceJob_mock.return_value
    assert ChoiceJob_mock.call_args_list == [call(
        name=uhd_tracker_jobs.get_job_name.return_value,
        label='Codec',
        precondition=uhd_tracker_jobs.make_precondition.return_value,
        autodetect=uhd_tracker_jobs.autodetect_codec,
        autofinish=True,
        options=(
            ('x264', 'x264'),
            ('x265', 'x265'),
            ('x266', 'x266'),
            ('H.264', 'H.264'),  # AVC aka H.264
            ('H.265', 'HEVC'),   # HEVC aka H.265
            ('AV1', 'AV1'),
            ('VC-1', 'VC-1'),
            ('MPEG-2', 'MPEG-2'),
        ),
        common_job_arg='common job argument',
    )]
    assert uhd_tracker_jobs.get_job_name.call_args_list == [call('codec')]
    assert uhd_tracker_jobs.make_precondition.call_args_list == [call('codec_job')]
    assert uhd_tracker_jobs.common_job_args.call_args_list == [call(ignore_cache=True)]


@pytest.mark.asyncio
async def test_autodetect_codec(uhd_tracker_jobs, mocker):
    mocks = Mock(
        x264=Mock(return_value=False),
        x265=Mock(return_value=True),
        h264=Mock(return_value=True),
        h265=Mock(return_value=False),
    )
    mocker.patch.object(uhd_tracker_jobs, 'codec_map', {
        'x264': mocks.x264,
        'x265': mocks.x265,
        'H.264': mocks.h264,
        'H.265': mocks.h265,
    })

    return_value = await uhd_tracker_jobs.autodetect_codec('job_')
    assert return_value == 'x265'

    mocks.x265.return_value = False
    mocks.h264.return_value = False
    return_value = await uhd_tracker_jobs.autodetect_codec('job_')
    assert return_value is None


@pytest.mark.parametrize(
    argnames='codec, release, exp_return_value',
    argvalues=(
        ('x264', Mock(video_format='foo'), False),
        ('x264', Mock(video_format='x264'), True),
        ('x265', Mock(video_format='foo'), False),
        ('x265', Mock(video_format='x265'), True),
        ('H.264', Mock(video_format='foo'), False),
        ('H.264', Mock(video_format='H.264'), True),
        ('H.265', Mock(video_format='foo'), False),
        ('H.265', Mock(video_format='H.265'), True),
    ),
    ids=lambda v: str(v),
)
def test_codec_map(codec, release, exp_return_value, uhd_tracker_jobs):
    is_codec = uhd_tracker_jobs.codec_map[codec]
    assert is_codec(release) is exp_return_value


def test_hdr_format_job(uhd_tracker_jobs, mocker):
    ChoiceJob_mock = mocker.patch('upsies.jobs.dialog.ChoiceJob')
    mocker.patch.object(uhd_tracker_jobs, 'get_job_name')
    mocker.patch.object(uhd_tracker_jobs, 'make_precondition')
    mocker.patch.object(uhd_tracker_jobs, 'common_job_args', return_value={'common_job_arg': 'common job argument'})

    assert uhd_tracker_jobs.hdr_format_job is ChoiceJob_mock.return_value
    assert ChoiceJob_mock.call_args_list == [call(
        name=uhd_tracker_jobs.get_job_name.return_value,
        label='HDR',
        precondition=uhd_tracker_jobs.make_precondition.return_value,
        autodetect=uhd_tracker_jobs.autodetect_hdr_format,
        autofinish=True,
        options=(
            ('No', 'No'),
            ('HDR10', 'HDR10'),
            ('HDR10+', 'HDR10+'),
            ('Dolby Vision', 'DoVi'),
        ),
        common_job_arg='common job argument',
    )]
    assert uhd_tracker_jobs.get_job_name.call_args_list == [call('hdr-format')]
    assert uhd_tracker_jobs.make_precondition.call_args_list == [call('hdr_format_job')]
    assert uhd_tracker_jobs.common_job_args.call_args_list == [call()]


@pytest.mark.asyncio
async def test_autodetect_hdr_format(uhd_tracker_jobs, mocker):
    mocks = Mock(
        no=Mock(return_value=False),
        hdr10=Mock(return_value=True),
        hdr10p=Mock(return_value=True),
        dovi=Mock(return_value=False),
    )
    mocker.patch.object(uhd_tracker_jobs, 'hdr_format_map', {
        'No': mocks.no,
        'HDR10': mocks.hdr10,
        'HDR10+': mocks.hdr10p,
        'Dolby Vision': mocks.dovi,
    })

    return_value = await uhd_tracker_jobs.autodetect_hdr_format('job_')
    assert return_value == 'HDR10'

    mocks.hdr10.return_value = False
    mocks.hdr10p.return_value = False
    return_value = await uhd_tracker_jobs.autodetect_hdr_format('job_')
    assert return_value is None


@pytest.mark.parametrize(
    argnames='hdr_format, release, exp_return_value',
    argvalues=(
        ('No', Mock(hdr_format='foo'), False),
        ('No', Mock(hdr_format=''), True),
        ('HDR10', Mock(hdr_format='foo'), False),
        ('HDR10', Mock(hdr_format='HDR10'), True),
        ('HDR10+', Mock(hdr_format='foo'), False),
        ('HDR10+', Mock(hdr_format='HDR10+'), True),
        ('Dolby Vision', Mock(hdr_format='foo'), False),
        ('Dolby Vision', Mock(hdr_format='DV'), True),
    ),
    ids=lambda v: str(v),
)
def test_hdr_format_map(hdr_format, release, exp_return_value, uhd_tracker_jobs):
    is_hdr_format = uhd_tracker_jobs.hdr_format_map[hdr_format]
    assert is_hdr_format(release) is exp_return_value


def test_tags_job(uhd_tracker_jobs, mocker):
    mocker.patch.object(type(uhd_tracker_jobs), 'imdb_job', PropertyMock())
    TextFieldJob_mock = mocker.patch('upsies.jobs.dialog.TextFieldJob')
    mocker.patch.object(uhd_tracker_jobs, 'get_job_name')
    mocker.patch.object(uhd_tracker_jobs, 'make_precondition')
    mocker.patch.object(uhd_tracker_jobs, 'common_job_args', return_value={'common_job_arg': 'common job argument'})

    assert uhd_tracker_jobs.tags_job is TextFieldJob_mock.return_value
    assert TextFieldJob_mock.call_args_list == [call(
        name=uhd_tracker_jobs.get_job_name.return_value,
        label='Tags',
        precondition=uhd_tracker_jobs.make_precondition.return_value,
        prejobs=(
            uhd_tracker_jobs.imdb_job,
        ),
        text=uhd_tracker_jobs.autodetect_tags,
        nonfatal_exceptions=(
            errors.RequestError,
        ),
        finish_on_success=True,
        normalizer=uhd_tracker_jobs.normalize_tags,
        validator=uhd_tracker_jobs.validate_tags,
        common_job_arg='common job argument',
    )]
    assert uhd_tracker_jobs.get_job_name.call_args_list == [call('tags')]
    assert uhd_tracker_jobs.make_precondition.call_args_list == [call('tags_job')]
    assert uhd_tracker_jobs.common_job_args.call_args_list == [call()]


@pytest.mark.parametrize(
    argnames='imdb_id, uhd_info, exp_return_value',
    argvalues=(
        ('tt123456', {}, ''),
        ('tt123456', {'tag': ''}, ''),
        ('tt123456', {'tag': 'fo&eacute;,, bar, baz,'}, 'foé,, bar, baz,'),
    ),
    ids=lambda v: str(v),
)
@pytest.mark.asyncio
async def test_autodetect_tags(
        imdb_id, uhd_info,
        exp_return_value,
        uhd_tracker_jobs, mocker,
):
    mocker.patch.object(type(uhd_tracker_jobs), 'imdb_id', PropertyMock(return_value=imdb_id))
    mocker.patch.object(uhd_tracker_jobs.tracker, 'get_uhd_info', AsyncMock(return_value=uhd_info))

    return_value = await uhd_tracker_jobs.autodetect_tags()
    assert return_value == exp_return_value
    assert uhd_tracker_jobs.tracker.get_uhd_info.call_args_list == [call(uhd_tracker_jobs.imdb_id)]


@pytest.mark.parametrize(
    argnames='max_tags_length, text, exp_return_value',
    argvalues=(
        (15, '', ''),
        (15, 'foo', 'foo'),
        (15, 'foo,bar,baz,foo', 'foo\nbar\nbaz'),
        (15, ',  ,, foo ,\nbar\t, \t\nbaz ,   ', 'foo\nbar\nbaz'),
        (15, 'foo,bar,baz,this', 'foo\nbar\nbaz'),
        (15, 'foo,bar,baz,thi', 'foo\nbar\nbaz\nthi'),
    ),
    ids=lambda v: str(v),
)
def test_normalize_tags(
        max_tags_length, text, exp_return_value,
        uhd_tracker_jobs, mocker,
):
    mocker.patch.object(uhd_tracker_jobs, 'max_tags_length', max_tags_length)
    return_value = uhd_tracker_jobs.normalize_tags(text)
    assert return_value == exp_return_value


@pytest.mark.parametrize(
    argnames='min_tags_count, text, exp_exception',
    argvalues=(
        (3, '', ValueError('At least 3 tags are required.')),
        (3, 'foo', ValueError('At least 3 tags are required.')),
        (3, 'foo\nbar', ValueError('At least 3 tags are required.')),
        (3, 'foo\nbar\nbaz', None),
    ),
    ids=lambda v: str(v),
)
def test_validate_tags(
        min_tags_count, text, exp_exception,
        uhd_tracker_jobs, mocker,
):
    mocker.patch.object(uhd_tracker_jobs, 'min_tags_count', min_tags_count)
    if isinstance(exp_exception, Exception):
        with pytest.raises(type(exp_exception), match=rf'^{re.escape(str(exp_exception))}$'):
            uhd_tracker_jobs.validate_tags(text)
    else:
        return_value = uhd_tracker_jobs.validate_tags(text)
        assert return_value is None


@pytest.mark.parametrize(
    argnames='uhd_info, exp_return_value',
    argvalues=(
        ({}, None),
        ({'photo': ''}, None),
        ({'photo': 'http://my/poster.jpg'}, {
            'poster': 'http://my/poster.jpg',
            'width': None,
            'height': None,
            'imghosts': (),
            'write_to': None,
        }),
    ),
    ids=lambda v: str(v),
)
@pytest.mark.asyncio
async def test_get_poster_from_tracker(
        uhd_info, exp_return_value,
        uhd_tracker_jobs, mocker,
):
    mocks = AsyncMock()
    mocker.patch.object(type(uhd_tracker_jobs), 'imdb_job', PropertyMock(return_value=Mock(wait=mocks.imdb_wait)))
    mocker.patch.object(type(uhd_tracker_jobs), 'imdb_id', PropertyMock(return_value='tt123456'))
    mocks.attach_mock(
        mocker.patch.object(uhd_tracker_jobs.tracker, 'get_uhd_info', AsyncMock(return_value=uhd_info)),
        'get_uhd_info',
    )

    return_value = await uhd_tracker_jobs.get_poster_from_tracker()
    assert return_value == exp_return_value

    assert mocks.mock_calls == [
        call.imdb_wait(),
        call.get_uhd_info(uhd_tracker_jobs.imdb_id),
    ]


def test_trailer_job(uhd_tracker_jobs, mocker):
    mocker.patch.object(type(uhd_tracker_jobs), 'imdb_job', PropertyMock())
    TextFieldJob_mock = mocker.patch('upsies.jobs.dialog.TextFieldJob')
    mocker.patch.object(uhd_tracker_jobs, 'get_job_name')
    mocker.patch.object(uhd_tracker_jobs, 'make_precondition')
    mocker.patch.object(uhd_tracker_jobs, 'common_job_args', return_value={'common_job_arg': 'common job argument'})

    assert uhd_tracker_jobs.trailer_job is TextFieldJob_mock.return_value
    assert TextFieldJob_mock.call_args_list == [call(
        name=uhd_tracker_jobs.get_job_name.return_value,
        label='Trailer',
        precondition=uhd_tracker_jobs.make_precondition.return_value,
        prejobs=(
            uhd_tracker_jobs.imdb_job,
        ),
        text=uhd_tracker_jobs.autodetect_trailer,
        nonfatal_exceptions=(
            errors.RequestError,
        ),
        finish_on_success=True,
        normalizer=uhd_tracker_jobs.normalize_trailer,
        validator=uhd_tracker_jobs.validate_trailer,
        common_job_arg='common job argument',
    )]
    assert uhd_tracker_jobs.get_job_name.call_args_list == [call('trailer')]
    assert uhd_tracker_jobs.make_precondition.call_args_list == [call('trailer_job')]
    assert uhd_tracker_jobs.common_job_args.call_args_list == [call(
        ignore_cache=bool('trailer' in uhd_tracker_jobs.options),
    )]


@pytest.mark.parametrize(
    argnames='options, imdb_id, uhd_info, exp_return_value, exp_mock_calls',
    argvalues=(
        (
            {'trailer': 'trailer_from_user'},
            'tt123456',
            {'trailer': 'trailer_from_uhd'},
            'trailer_from_user',
            [],
        ),
        (
            {'trailer': ''},
            'tt123456',
            {'trailer': 'trailer_from_uhd'},
            'trailer_from_uhd',
            [call.get_uhd_info('tt123456')],
        ),
        (
            {},
            'tt123456',
            {'trailer': 'trailer_from_uhd'},
            'trailer_from_uhd',
            [call.get_uhd_info('tt123456')],
        ),
        (
            {},
            'tt123456',
            {'trailer': ''},
            '',
            [call.get_uhd_info('tt123456')],
        ),
        (
            {},
            'tt123456',
            {},
            '',
            [call.get_uhd_info('tt123456')],
        ),
    ),
    ids=lambda v: str(v),
)
@pytest.mark.asyncio
async def test_autodetect_trailer(
        options, imdb_id, uhd_info,
        exp_return_value, exp_mock_calls,
        uhd_tracker_jobs, mocker,
):
    mocker.patch.object(type(uhd_tracker_jobs), 'options', PropertyMock(return_value=options))
    mocker.patch.object(type(uhd_tracker_jobs), 'imdb_job', PropertyMock(return_value=Mock(is_finished=True)))
    mocker.patch.object(type(uhd_tracker_jobs), 'imdb_id', PropertyMock(return_value=imdb_id))
    mocks = Mock()
    mocks.attach_mock(
        mocker.patch.object(uhd_tracker_jobs.tracker, 'get_uhd_info', AsyncMock(return_value=uhd_info)),
        'get_uhd_info',
    )

    return_value = await uhd_tracker_jobs.autodetect_trailer()
    assert return_value == exp_return_value
    assert mocks.mock_calls == exp_mock_calls


@pytest.mark.parametrize(
    argnames='text, get_youtube_id, exp_return_value',
    argvalues=(
        (
            'http://youtube.com/watch?v=d34db33f',
            Mock(return_value='d34db33f'),
            'https://youtu.be/d34db33f',
        ),
        (
            'http://example.org/watch?v=d34db33f',
            Mock(side_effect=ValueError('Invalid ID or URL')),
            'http://example.org/watch?v=d34db33f',
        ),
    ),
    ids=lambda v: str(v),
)
def test_normalize_trailer(
        text, get_youtube_id,
        exp_return_value,
        uhd_tracker_jobs, mocker,
):
    mocker.patch.object(uhd_tracker_jobs, 'get_youtube_id', get_youtube_id),

    return_value = uhd_tracker_jobs.normalize_trailer(text)
    assert return_value == exp_return_value
    assert uhd_tracker_jobs.get_youtube_id.call_args_list == [
        call.get_youtube_id(text),
    ]


@pytest.mark.parametrize(
    argnames='text, get_youtube_id, exp_result, exp_mock_calls',
    argvalues=(
        (
            'http://youtu.be/d34db33f',
            Mock(return_value='d34db33f'),
            None,
            [call.get_youtube_id('http://youtu.be/d34db33f')],
        ),
        (
            'http://youtu.be/d34db33f',
            Mock(side_effect=ValueError('Invalid ID or URL')),
            ValueError('Invalid ID or URL'),
            [call.get_youtube_id('http://youtu.be/d34db33f')],
        ),
        (
            '',
            Mock(return_value='d34db33f'),
            None,
            [],
        ),
        (
            '',
            Mock(side_effect=ValueError('Invalid ID or URL')),
            None,
            [],
        ),
    ),
    ids=lambda v: str(v),
)
def test_validate_trailer(
        text, get_youtube_id,
        exp_result, exp_mock_calls,
        uhd_tracker_jobs, mocker,
):
    mocker.patch.object(uhd_tracker_jobs, 'get_youtube_id', get_youtube_id),

    if isinstance(exp_result, Exception):
        with pytest.raises(type(exp_result), match=rf'^{re.escape(str(exp_result))}$'):
            uhd_tracker_jobs.validate_trailer(text)
    else:
        return_value = uhd_tracker_jobs.validate_trailer(text)
        assert return_value == exp_result

    assert uhd_tracker_jobs.get_youtube_id.call_args_list == exp_mock_calls


@pytest.mark.parametrize('scheme', ('http', 'https'))
@pytest.mark.parametrize('host', ('www.youtube.com', 'youtube.com', 'youtu.be', 'youtube.fi'))
@pytest.mark.parametrize(
    argnames='url, default, exp_result',
    argvalues=(
        # Valid URLs
        ('{scheme}://{host}/watch?v=d34d-b33f_&feature=feedrec_grec_index', None, 'd34d-b33f_'),
        ('{scheme}://{host}/v/d34d-b33f_?fs=1&amp;hl=en_US&amp;rel=0', None, 'd34d-b33f_'),
        ('{scheme}://{host}/watch?v=d34d-b33f_#t=0m10s', None, 'd34d-b33f_'),
        ('{scheme}://{host}/embed/d34d-b33f_?rel=0', None, 'd34d-b33f_'),
        ('{scheme}://{host}/watch?v=d34d-b33f_', None, 'd34d-b33f_'),
        ('{scheme}://{host}/d34d-b33f_', None, 'd34d-b33f_'),
        ('d34d-b33f_', None, 'd34d-b33f_'),
        # Invalid URLs without default value
        ('{scheme}://{host}/', uhd.UhdTrackerJobs._YOUTUBE_ID_NO_DEFAULT, ValueError('Not a YouTube ID or URL.')),
        ('/d34d-b33f_/', uhd.UhdTrackerJobs._YOUTUBE_ID_NO_DEFAULT, ValueError('Not a YouTube ID or URL.')),
        ('http://example.org/v/d34d-b33f_', uhd.UhdTrackerJobs._YOUTUBE_ID_NO_DEFAULT, ValueError('Not a YouTube ID or URL.')),
        ('http://example.org/watch?v=d34d-b33f_', uhd.UhdTrackerJobs._YOUTUBE_ID_NO_DEFAULT, ValueError('Not a YouTube ID or URL.')),
        # Invalid URLs with default value
        ('{scheme}://{host}/', None, None),
        ('/d34d-b33f_/', '', ''),
        ('http://example.org/v/d34d-b33f_', 0, 0),
        ('http://example.org/watch?v=d34d-b33f_', 'foo', 'foo'),
    ),
    ids=lambda v: str(v),
)
def test_get_youtube_id(scheme, host, url, default, exp_result, uhd_tracker_jobs):
    url = url.format(scheme=scheme, host=host)
    if isinstance(exp_result, Exception):
        with pytest.raises(type(exp_result), match=rf'^{re.escape(str(exp_result))}$'):
            uhd_tracker_jobs.get_youtube_id(url, default=default)
    else:
        return_value = uhd_tracker_jobs.get_youtube_id(url, default=default)
        assert return_value == exp_result


def test_description_job(uhd_tracker_jobs, mocker):
    mocker.patch.object(type(uhd_tracker_jobs), 'upload_screenshots_job', PropertyMock())
    mocker.patch.object(type(uhd_tracker_jobs), 'mediainfo_job', PropertyMock())
    TextFieldJob_mock = mocker.patch('upsies.jobs.dialog.TextFieldJob')
    mocker.patch.object(uhd_tracker_jobs, 'get_job_name')
    mocker.patch.object(uhd_tracker_jobs, 'make_precondition')
    mocker.patch.object(uhd_tracker_jobs, 'common_job_args', return_value={'common_job_arg': 'common job argument'})

    assert uhd_tracker_jobs.description_job is TextFieldJob_mock.return_value
    assert TextFieldJob_mock.call_args_list == [call(
        name=uhd_tracker_jobs.get_job_name.return_value,
        label='Description',
        precondition=uhd_tracker_jobs.make_precondition.return_value,
        prejobs=(
            uhd_tracker_jobs.upload_screenshots_job,
            uhd_tracker_jobs.mediainfo_job,
        ),
        text=uhd_tracker_jobs.generate_description,
        hidden=True,
        finish_on_success=True,
        read_only=True,
        common_job_arg='common job argument',
    )]
    assert uhd_tracker_jobs.get_job_name.call_args_list == [call('description')]
    assert uhd_tracker_jobs.make_precondition.call_args_list == [call('description_job')]
    assert uhd_tracker_jobs.common_job_args.call_args_list == [call(ignore_cache=True)]


def test_image_host_config(uhd_tracker_jobs):
    assert uhd_tracker_jobs.image_host_config == {
        'common': {'thumb_width': 350},
    }


@pytest.mark.parametrize('nfo', (None, '', '<nfo>'))
def test_generate_description(nfo, uhd_tracker_jobs, mocker):
    mocker.patch.object(uhd_tracker_jobs, 'generate_description_screenshots', return_value='<screenshots>')
    mocker.patch.object(uhd_tracker_jobs, 'generate_description_mediainfo', return_value='<mediainfo>')
    mocker.patch.object(uhd_tracker_jobs, 'generate_description_nfo', return_value=nfo)
    exp_promotion = (
        '[align=right][size=1]'
        f'Shared with [url={__homepage__}]{__project_name__}[/url]'
        '[/size][/align]'
    )
    return_value = uhd_tracker_jobs.generate_description()
    exp_return_value = (
        '<mediainfo>'
        + (f'\n\n{nfo}' if nfo else '')
        + '\n\n[center]<screenshots>[/center]'
        + f'\n{exp_promotion}'
    )
    assert return_value == exp_return_value
    assert uhd_tracker_jobs.generate_description_screenshots.call_args_list == [call()]
    assert uhd_tracker_jobs.generate_description_mediainfo.call_args_list == [call()]
    assert uhd_tracker_jobs.generate_description_nfo.call_args_list == [call()]


@pytest.mark.parametrize('mediainfo', ('<mediainfo>', '  <mediainfo>\n  \n\n'))
def test_generate_description_mediainfo(mediainfo, uhd_tracker_jobs, mocker):
    mocker.patch.object(type(uhd_tracker_jobs), 'mediainfo_job', PropertyMock(return_value=Mock(
        is_finished=True,
        output=(mediainfo,),
    )))

    return_value = uhd_tracker_jobs.generate_description_mediainfo()
    assert return_value == (
        '[spoiler=Mediainfo]'
        + '[code]'
        + mediainfo.strip()
        + '[/code]'
        + '[/spoiler]'
    )


def test_generate_description_screenshots(uhd_tracker_jobs, mocker):
    mocker.patch.object(type(uhd_tracker_jobs), 'upload_screenshots_job', PropertyMock(return_value=Mock(
        is_finished=True,
        uploaded_images=('this.png', 'that.png'),
    )))
    mocker.patch.object(uhd_tracker_jobs, 'make_screenshots_grid')

    return_value = uhd_tracker_jobs.generate_description_screenshots()
    assert return_value is uhd_tracker_jobs.make_screenshots_grid.return_value
    assert uhd_tracker_jobs.make_screenshots_grid.call_args_list == [
        call(
            screenshots=uhd_tracker_jobs.upload_screenshots_job.uploaded_images,
            columns=2,
            horizontal_spacer='   ',
            vertical_spacer='\n\n',
        ),
    ]


@pytest.mark.parametrize(
    argnames='nfo, exp_return_value',
    argvalues=(
        ('', None),
        ('<nfo>', '[spoiler=NFO][code]<nfo>[/code][/spoiler]'),
    ),
    ids=lambda v: repr(v),
)
def test_generate_description_nfo(nfo, exp_return_value, uhd_tracker_jobs, mocker):
    mocker.patch.object(uhd_tracker_jobs, 'read_nfo', return_value=nfo)

    return_value = uhd_tracker_jobs.generate_description_nfo()
    assert return_value == exp_return_value
    assert uhd_tracker_jobs.read_nfo.call_args_list == [call(strip=True)]


def test_automerge_group_job(uhd_tracker_jobs, mocker):
    mocker.patch.object(type(uhd_tracker_jobs), 'imdb_job', PropertyMock())
    mocker.patch.object(type(uhd_tracker_jobs), 'type_job', PropertyMock())
    mocker.patch.object(type(uhd_tracker_jobs), 'season_job', PropertyMock())
    ChoiceJob_mock = mocker.patch('upsies.jobs.dialog.ChoiceJob')
    mocker.patch.object(uhd_tracker_jobs, 'get_job_name')
    mocker.patch.object(uhd_tracker_jobs, 'make_precondition')
    mocker.patch.object(uhd_tracker_jobs, 'common_job_args', return_value={'common_job_arg': 'common job argument'})

    assert uhd_tracker_jobs.automerge_group_job is ChoiceJob_mock.return_value
    assert ChoiceJob_mock.call_args_list == [call(
        name=uhd_tracker_jobs.get_job_name.return_value,
        label='Automerge Group',
        precondition=uhd_tracker_jobs.make_precondition.return_value,
        prejobs=(
            uhd_tracker_jobs.imdb_job,
            uhd_tracker_jobs.type_job,
            uhd_tracker_jobs.season_job,
        ),
        autodetect=uhd_tracker_jobs.autodetect_automerge_group,
        autofinish=True,
        options=(
            ('Yes', True),
            ('No', False),
        ),
        common_job_arg='common job argument',
    )]
    assert uhd_tracker_jobs.get_job_name.call_args_list == [call('automerge-group')]
    assert uhd_tracker_jobs.make_precondition.call_args_list == [call('automerge_group_job')]
    assert uhd_tracker_jobs.common_job_args.call_args_list == [call(ignore_cache=True)]


@pytest.mark.parametrize(
    argnames='season_number, group_names, exp_return_value',
    argvalues=(
        (
            3,
            [],
            'No',
        ),
        (
            3,
            ['foo season 01', 'foo season 02', 'foo season 03'],
            'Yes',
        ),
        (
            3,
            ['foo season 01', 'foo season 02', 'foo season 03 / aka le foo'],
            'Yes',
        ),
        (
            3,
            ['season 01', 'season 02', 'season 03 / aka le foo'],
            'No',
        ),
        (
            4,
            ['foo season 01', 'foo season 02', 'foo season 03'],
            'No',
        ),
        (
            0,
            ['foo season 00', 'foo season 01', 'foo season 02'],
            'Yes',
        ),
        (
            0,
            ['foo season 01', 'foo season 02', 'foo season 03'],
            'No',
        ),
        (
            None,
            ['irrelevant'],
            'Yes',
        ),
    ),
    ids=lambda v: repr(v),
)
@pytest.mark.asyncio
async def test_autodetect_automerge_group_with_season_number(
        season_number, group_names,
        exp_return_value,
        uhd_tracker_jobs, mocker,
):
    mocker.patch.object(uhd_tracker_jobs, '_get_season_group_names', AsyncMock(return_value=group_names))
    mocker.patch.object(type(uhd_tracker_jobs), 'season_number', PropertyMock(return_value=season_number))
    mocker.patch.object(type(uhd_tracker_jobs), 'season_job', PropertyMock(return_value=Mock(
        is_finished=True,
    )))

    return_value = await uhd_tracker_jobs.autodetect_automerge_group('ignored job')
    assert return_value == exp_return_value
    if season_number is not None:
        assert uhd_tracker_jobs._get_season_group_names.call_args_list == [call()]
    else:
        assert uhd_tracker_jobs._get_season_group_names.call_args_list == []


@pytest.mark.parametrize(
    argnames='html, exp_group_names',
    argvalues=(
        (
            (
                '<html><body>'
                '<a class="torrent_name"> <b> Foo Season 01 </b> </a>'
                '<a class="torrent_name"> <b> Fóǫ Season 02 </b> </a>'
                '<a class="torrent_name"> <b> Föö Season 03 </b> </a>'
                '</body></html>'
            ),
            [
                'foo season 01',
                'foo season 02',
                'foo season 03',
            ],
        ),
        (
            (
                '<html><body>'
                '<a>foo</a>'
                '<a>bar</a>'
                '<a>baz</a>'
                '</body></html>'
            ),
            [],
        ),
    ),
)
@pytest.mark.asyncio
async def test__get_season_group_names(html, exp_group_names, uhd_tracker_jobs, mocker):
    mocks = Mock()
    mocks.attach_mock(mocker.patch.object(uhd_tracker_jobs.tracker, 'login', AsyncMock()), 'login')
    mocks.attach_mock(mocker.patch.object(uhd_tracker_jobs.tracker, '_request', AsyncMock(return_value=html)), '_request')
    mocker.patch.object(type(uhd_tracker_jobs), 'imdb_id', PropertyMock(return_value='tt123456'))
    mocker.patch.object(
        type(uhd_tracker_jobs._tracker), '_torrents_url', PropertyMock(return_value='http://torrents.php'),
        create=True,
    )

    return_value = await uhd_tracker_jobs._get_season_group_names()
    assert return_value == exp_group_names
    assert mocks.mock_calls == [
        call.login(),
        call._request(
            method='GET',
            url=uhd_tracker_jobs._tracker._torrents_url,
            params={
                'searchstr': uhd_tracker_jobs.imdb_id,
            },
            error_prefix='Automerge group check failed',
        )
    ]


def test_release_name_translation(uhd_tracker_jobs):
    assert uhd_tracker_jobs.release_name_translation == {
        'group': {
            re.compile(r'^NOGROUP$'): 'Unknown',
        },
    }


@pytest.mark.parametrize('season_number', (None, 0, 3))
@pytest.mark.parametrize('is_scene, exp_scene', ((False, None), (True, '1')), ids=('!Scene', 'Scene'))
@pytest.mark.parametrize('automerge_group, exp_auto_merge_group', ((False, None), (True, 'on')), ids=('!Automerge', 'Automerge'))
@pytest.mark.parametrize('internal, exp_internal', ((False, None), (True, 'on')), ids=('!Internal', 'Internal'))
@pytest.mark.parametrize('_3d, exp_3d', ((False, None), (True, '1')), ids=('!3D', '3D'))
@pytest.mark.parametrize('vie, exp_vie', ((False, None), (True, '1')), ids=('!Vie', 'Vie'))
@pytest.mark.parametrize('anonymous, exp_anonymous', ((False, None), (True, '1')), ids=('!Anonymous', 'Anonymous'))
def test_post_data(
        season_number,
        is_scene, exp_scene,
        automerge_group, exp_auto_merge_group,
        internal, exp_internal,
        _3d, exp_3d,
        vie, exp_vie,
        anonymous, exp_anonymous,
        uhd_tracker_jobs, mock_job_attributes, mocker,
):
    job_outputs = {
        uhd_tracker_jobs.imdb_job: 'tt123456',
        uhd_tracker_jobs.year_job: '2012',
        uhd_tracker_jobs.quality_job: '720p',
        uhd_tracker_jobs.version_job: ('Uncut', 'Extended'),
        uhd_tracker_jobs.source_job: 'BluRay',
        uhd_tracker_jobs.codec_job: 'x264',
        uhd_tracker_jobs.hdr_format_job: 'HDR10',
        uhd_tracker_jobs.tags_job: 'drama\ncomedy\nhorror',
        uhd_tracker_jobs.poster_job: 'http://my.poster.jpg',
        uhd_tracker_jobs.trailer_job: 'https://youtu.be/MnT0nGmFkJ-IqOe',
        uhd_tracker_jobs.mediainfo_job: '[mediainfo]...[/mediainfo]',
        uhd_tracker_jobs.description_job: '[description]...[/description]',
    }

    def get_job_output(job, **__):
        if job is not None:
            print('!!!', job_outputs[job])
            return job_outputs[job]

    mocker.patch.object(uhd_tracker_jobs, 'get_job_output', side_effect=get_job_output)

    job_attributes = {
        uhd_tracker_jobs.type_job: {'choice': '0 or 2'},
        uhd_tracker_jobs.automerge_group_job: {'choice': automerge_group},
        uhd_tracker_jobs.scene_check_job: {'is_scene_release': is_scene},
    }

    def get_job_attribute(job, attribute):
        if job is not None:
            return job_attributes[job][attribute]

    mocker.patch.object(uhd_tracker_jobs, 'get_job_attribute', side_effect=get_job_attribute)

    mocker.patch.object(type(uhd_tracker_jobs), 'options', PropertyMock(return_value={
        'internal': internal,
        '3d': _3d,
        'vie': vie,
        'anonymous': anonymous,
    }))
    mocker.patch.object(type(uhd_tracker_jobs), 'release_name', PropertyMock(return_value=Mock(
        title='Original Title',
        title_aka='Also Known As',
        group='ASDF',
    )))
    mocker.patch.object(type(uhd_tracker_jobs), 'season_number', PropertyMock(return_value=season_number))

    assert uhd_tracker_jobs.post_data == {
        'submit': 'true',
        'type': job_attributes[uhd_tracker_jobs.type_job]['choice'],
        'imdbid': job_outputs[uhd_tracker_jobs.imdb_job],
        'title': uhd_tracker_jobs.release_name.title,
        'OtherTitle': uhd_tracker_jobs.release_name.title_aka,
        'smalldesc': '',
        'year': job_outputs[uhd_tracker_jobs.year_job],
        'season': season_number,
        'format': job_outputs[uhd_tracker_jobs.quality_job],
        'team': uhd_tracker_jobs.release_name.group,
        'Version': ' / '.join(job_outputs[uhd_tracker_jobs.version_job]),
        'media': job_outputs[uhd_tracker_jobs.source_job],
        'codec': job_outputs[uhd_tracker_jobs.codec_job],
        'hdr': job_outputs[uhd_tracker_jobs.hdr_format_job],
        'genre_tags': '---',
        'tags': ','.join(job_outputs[uhd_tracker_jobs.tags_job].split('\n')),
        'image': job_outputs[uhd_tracker_jobs.poster_job],
        'trailer': 'MnT0nGmFkJ-IqOe',
        'mediainfo': job_outputs[uhd_tracker_jobs.mediainfo_job],
        'release_desc': job_outputs[uhd_tracker_jobs.description_job],
        'auto_merge_group': exp_auto_merge_group,
        'internal': exp_internal,
        'd3d': exp_3d,
        'vie': exp_vie,
        'scene': exp_scene,
        'anonymous': exp_anonymous,
    }

    exp_get_job_output_calls = [
        call(uhd_tracker_jobs.imdb_job, slice=0),
        call(uhd_tracker_jobs.year_job, slice=0),
        call(uhd_tracker_jobs.quality_job, slice=0),
        call(uhd_tracker_jobs.version_job),
        call(uhd_tracker_jobs.source_job, slice=0),
        call(uhd_tracker_jobs.codec_job, slice=0),
        call(uhd_tracker_jobs.hdr_format_job, slice=0),
        call(uhd_tracker_jobs.tags_job, slice=0),
        call(uhd_tracker_jobs.poster_job, slice=0),
        call(uhd_tracker_jobs.trailer_job, slice=0),
        call(uhd_tracker_jobs.mediainfo_job, slice=0),
        call(uhd_tracker_jobs.description_job, slice=0),
    ]
    assert uhd_tracker_jobs.get_job_output.call_args_list == exp_get_job_output_calls

    assert uhd_tracker_jobs.get_job_attribute.call_args_list == [
        call(uhd_tracker_jobs.type_job, 'choice'),
        call(uhd_tracker_jobs.automerge_group_job, 'choice'),
        call(uhd_tracker_jobs.scene_check_job, 'is_scene_release'),
    ]


def test_post_files(uhd_tracker_jobs, mocker):
    mocker.patch.object(type(uhd_tracker_jobs), 'torrent_filepath', PropertyMock(return_value='path/to/file.torrent'))

    assert uhd_tracker_jobs.post_files == {
        'file_input': {
            'file': 'path/to/file.torrent',
            'mimetype': 'application/x-bittorrent',
        },
    }
