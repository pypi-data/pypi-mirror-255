import dataclasses
import re
from unittest.mock import AsyncMock, Mock, PropertyMock, call

import pytest

from upsies import errors, utils
from upsies.trackers import ptp


@pytest.fixture
def tracker():
    tracker = Mock()
    tracker.name = 'ptp'
    return tracker


@pytest.fixture
def ptp_tracker_jobs(tracker, tmp_path, mocker):
    content_path = tmp_path / 'Foo 2000 1080p BluRay x264-ASDF'

    ptp_tracker_jobs = ptp.PtpTrackerJobs(
        content_path=str(content_path),
        tracker=tracker,
        image_hosts=(Mock(), Mock()),
        btclient=Mock(),
        torrent_destination=str(tmp_path / 'destination'),
        common_job_args={
            'home_directory': str(tmp_path / 'home_directory'),
            'ignore_cache': True,
        },
        options=None,
    )

    return ptp_tracker_jobs


@pytest.fixture
def mock_job_attributes(mocker):
    def mock_job_attributes(ptp_tracker_jobs):
        job_attrs = (
            # Common interactive jobs
            'type_job',
            'imdb_job',
            'source_job',
            'scene_check_job',

            # Interactive jobs that only run if movie does not exists on PTP yet
            'title_job',
            'year_job',
            'edition_job',
            'plot_job',
            'tags_job',
            'poster_job',

            # Background jobs
            'create_torrent_job',
            'mediainfo_job',
            'screenshots_job',
            'upload_screenshots_job',
            'ptp_group_id_job',
            'description_job',
            'trumpable_job',
        )
        for job_attr in job_attrs:
            mocker.patch.object(
                type(ptp_tracker_jobs),
                job_attr,
                PropertyMock(return_value=Mock(attr=job_attr)),
            )

    return mock_job_attributes


def test_jobs_before_upload_items(ptp_tracker_jobs, mock_job_attributes, mocker):
    mock_job_attributes(ptp_tracker_jobs)

    assert tuple(job.attr for job in ptp_tracker_jobs.jobs_before_upload) == (
        # Common interactive jobs
        'type_job',
        'imdb_job',
        'source_job',
        'scene_check_job',

        # Interactive jobs that only run if movie does not exists on PTP yet
        'title_job',
        'year_job',
        'edition_job',
        'plot_job',
        'tags_job',
        'poster_job',

        # Background jobs
        'create_torrent_job',
        'mediainfo_job',
        'screenshots_job',
        'upload_screenshots_job',
        'ptp_group_id_job',
        'trumpable_job',
        'description_job',
    )


def test_isolated_jobs__only_description(ptp_tracker_jobs, mock_job_attributes, mocker):
    mock_job_attributes(ptp_tracker_jobs)
    mocker.patch.object(type(ptp_tracker_jobs), 'options', PropertyMock(return_value={'only_description': True}))
    mocker.patch.object(ptp_tracker_jobs, 'get_job_and_dependencies')
    assert ptp_tracker_jobs.isolated_jobs is ptp_tracker_jobs.get_job_and_dependencies.return_value
    assert ptp_tracker_jobs.get_job_and_dependencies.call_args_list == [
        call(ptp_tracker_jobs.description_job, ptp_tracker_jobs.screenshots_job)
    ]

def test_isolated_jobs__no_isolated_jobs(ptp_tracker_jobs, mock_job_attributes, mocker):
    mock_job_attributes(ptp_tracker_jobs)
    mocker.patch.object(type(ptp_tracker_jobs), 'options', PropertyMock(return_value={}))
    mocker.patch.object(ptp_tracker_jobs, 'get_job_and_dependencies')
    assert ptp_tracker_jobs.isolated_jobs == ()
    assert ptp_tracker_jobs.get_job_and_dependencies.call_args_list == []


def test_type_job(ptp_tracker_jobs, mocker):
    ChoiceJob_mock = mocker.patch('upsies.jobs.dialog.ChoiceJob')
    mocker.patch.object(ptp_tracker_jobs, 'get_job_name')
    mocker.patch.object(ptp_tracker_jobs, 'make_precondition')
    mocker.patch.object(ptp_tracker_jobs, 'common_job_args', return_value={'common_job_arg': 'common job argument'})

    assert ptp_tracker_jobs.type_job is ChoiceJob_mock.return_value
    assert ChoiceJob_mock.call_args_list == [call(
        name=ptp_tracker_jobs.get_job_name.return_value,
        label='Type',
        precondition=ptp_tracker_jobs.make_precondition.return_value,
        autodetect=ptp_tracker_jobs.autodetect_type,
        options=(
            ('Feature Film', 'Feature Film'),
            ('Short Film', 'Short Film'),
            ('Miniseries', 'Miniseries'),
            ('Stand-up Comedy', 'Stand-up Comedy'),
            ('Live Performance', 'Live Performance'),
            ('Movie Collection', 'Movie Collection'),
        ),
        callbacks={
            'finished': ptp_tracker_jobs.update_imdb_query,
        },
        common_job_arg='common job argument',
    )]
    assert ptp_tracker_jobs.get_job_name.call_args_list == [call('type')]
    assert ptp_tracker_jobs.make_precondition.call_args_list == [call('type_job')]
    assert ptp_tracker_jobs.common_job_args.call_args_list == [call()]


@pytest.mark.parametrize(
    argnames='release_type, main_video_duration, exp_return_value, exp_duration_calls',
    argvalues=(
        (utils.release.ReleaseType.season, 123, 'Miniseries', False),
        (utils.release.ReleaseType.movie, 45 * 60, 'Short Film', True),
        (utils.release.ReleaseType.movie, (45 * 60) + 1, None, True),
    ),
    ids=lambda v: str(v),
)
def test_autodetect_type(
        release_type, main_video_duration,
        exp_return_value, exp_duration_calls,
        ptp_tracker_jobs, mocker,
):
    mocker.patch.object(type(ptp_tracker_jobs), 'release_name', PropertyMock(return_value=Mock(
        type=release_type,
    )))

    mocks = Mock()
    mocks.attach_mock(
        mocker.patch('upsies.utils.video.find_videos', return_value=iter(
            ('Foo.S01E01.mkv', 'Foo.S01E02.mkv', 'Foo.S01E03.mkv', 'Foo.sample.mkv'),
        )),
        'find_videos',
    )
    mocks.attach_mock(
        mocker.patch('upsies.utils.video.filter_main_videos', return_value=iter(
            ('Foo.S01E01.mkv', 'Foo.S01E02.mkv', 'Foo.S01E03.mkv'),
        )),
        'filter_main_videos',
    )
    mocks.attach_mock(
        mocker.patch('upsies.utils.video.duration', return_value=main_video_duration),
        'duration',
    )

    return_value = ptp_tracker_jobs.autodetect_type('job_')
    assert return_value == exp_return_value

    if exp_duration_calls:
        assert mocks.mock_calls == [
            call.find_videos(ptp_tracker_jobs.content_path),
            call.filter_main_videos(('Foo.S01E01.mkv', 'Foo.S01E02.mkv', 'Foo.S01E03.mkv', 'Foo.sample.mkv')),
            call.duration('Foo.S01E01.mkv'),
        ]
    else:
        assert mocks.mock_calls == []


def test_imdb_job(ptp_tracker_jobs, mocker):
    mocker.patch('upsies.jobs.webdb.WebDbSearchJob')
    assert ptp_tracker_jobs.imdb_job.no_id_ok is True


@pytest.mark.parametrize(
    argnames='type_job_output, exp_query_type',
    argvalues=(
        ([], '<original query type>'),
        (['Feature Film'], utils.release.ReleaseType.movie),
        (['Miniseries'], utils.release.ReleaseType.season),
        (['<anything else>'], '<original query type>'),
    ),
    ids=lambda v: str(v),
)
def test_update_imdb_query(type_job_output, exp_query_type, ptp_tracker_jobs, mocker):
    mocker.patch.object(type(ptp_tracker_jobs), 'imdb_job', PropertyMock(return_value=Mock(
        query=Mock(
            type='<original query type>',
        ),
    )))
    mocker.patch.object(type(ptp_tracker_jobs), 'type_job', PropertyMock(return_value=Mock(
        is_finished=True,
        output=type_job_output,
    )))

    return_value = ptp_tracker_jobs.update_imdb_query('job_')
    assert return_value is None
    assert ptp_tracker_jobs.imdb_job.query.type == exp_query_type


def test_trumpable_job(ptp_tracker_jobs, mocker):
    CustomJob_mock = mocker.patch('upsies.jobs.custom.CustomJob')
    mocker.patch.object(ptp_tracker_jobs, 'get_job_name')
    mocker.patch.object(ptp_tracker_jobs, 'make_precondition')
    mocker.patch.object(ptp_tracker_jobs, 'common_job_args', return_value={'common_job_arg': 'common job argument'})

    assert ptp_tracker_jobs.trumpable_job is CustomJob_mock.return_value
    assert CustomJob_mock.call_args_list == [call(
        name=ptp_tracker_jobs.get_job_name.return_value,
        label='Trumpable',
        precondition=ptp_tracker_jobs.make_precondition.return_value,
        worker=ptp_tracker_jobs.autodetect_trumpable,
        no_output_is_ok=True,
        catch=(
            errors.ContentError,
        ),
        common_job_arg='common job argument',
    )]
    assert ptp_tracker_jobs.get_job_name.call_args_list == [call('trumpable')]
    assert ptp_tracker_jobs.make_precondition.call_args_list == [call('trumpable_job')]
    assert ptp_tracker_jobs.common_job_args.call_args_list == [call(ignore_cache=True)]


@pytest.mark.parametrize(
    argnames='options, exp_hardcoded_subtitles_from_options, exp_no_english_subtitles_from_options',
    argvalues=(
        ({}, None, None),
        ({'hardcoded_subtitles': None, 'no_english_subtitles': None}, None, None),
        ({'hardcoded_subtitles': None, 'no_english_subtitles': True}, None, True),
        ({'hardcoded_subtitles': None, 'no_english_subtitles': False}, None, False),
        ({'hardcoded_subtitles': True, 'no_english_subtitles': None}, True, None),
        ({'hardcoded_subtitles': False, 'no_english_subtitles': None}, False, None),
        ({'hardcoded_subtitles': False, 'no_english_subtitles': True}, False, True),
        ({'hardcoded_subtitles': True, 'no_english_subtitles': False}, True, False),
        ({'hardcoded_subtitles': True, 'no_english_subtitles': True}, True, True),
        ({'hardcoded_subtitles': False, 'no_english_subtitles': False}, False, False),
    ),
    ids=lambda v: str(v),
)
@pytest.mark.parametrize(
    argnames='audio_languages, subtitle_languages, exp_no_english_subtitles_from_autodetection, exp_prompt',
    argvalues=(
        pytest.param(
            None, None, False, False,
            id='Track detection fails',
        ),
        pytest.param(
            set(), set(), False, False,
            id='No audio tracks + No subtitle tracks',
        ),
        pytest.param(
            {'se'},
            {},
            True,
            False,
            id='No English audio + No subtitles',
        ),
        pytest.param(
            {'se'},
            {'se', 'en', 'dk', 'no'},
            False,
            False,
            id='No English audio + English subtitles',
        ),
        pytest.param(
            {'se', 'en'},
            {'se', 'dk', 'no'},
            False,
            False,
            id='English audio + No English subtitles',
        ),
        pytest.param(
            {'se', 'en'},
            {'en', 'se', 'dk', 'no'},
            False,
            False,
            id='English audio + English subtitles',
        ),
        pytest.param(
            {'se', ''},
            {'se', 'dk', 'no'},
            False,
            True,
            id='No English audio + No English subtitles + Unknown audio',
        ),
        pytest.param(
            {'se'},
            {'se', '', 'dk', 'no'},
            False,
            True,
            id='No English audio + No English subtitles + Unknown subtitles',
        ),
    ),
    ids=lambda v: str(v),
)
async def test_autodetect_trumpable(
        options,
        exp_hardcoded_subtitles_from_options, exp_no_english_subtitles_from_options,
        audio_languages, subtitle_languages,
        exp_no_english_subtitles_from_autodetection, exp_prompt,
        ptp_tracker_jobs, mocker,
):
    mocker.patch.object(type(ptp_tracker_jobs), 'options', PropertyMock(return_value=options))

    languages_mock = mocker.patch('upsies.utils.video.languages', return_value=(
        {'Audio': audio_languages}
        if audio_languages is not None else
        {}
    ))

    mocker.patch.object(type(ptp_tracker_jobs), 'subtitles', PropertyMock(return_value=(
        [
            Mock(language=language)
            for language in subtitle_languages
        ]
        if subtitle_languages is not None else
        []
    )))

    mocker.patch.object(ptp_tracker_jobs.trumpable_job, 'add_prompt')
    RadioListPrompt_mock = mocker.patch('upsies.uis.prompts.RadioListPrompt')

    reasons = await ptp_tracker_jobs.autodetect_trumpable('job_')

    exp_hardcoded_subtitles = (
        exp_hardcoded_subtitles_from_options
        if exp_hardcoded_subtitles_from_options is not None else
        False
    )

    exp_no_english_subtitles = (
        exp_no_english_subtitles_from_options
        if exp_no_english_subtitles_from_options is not None else
        exp_no_english_subtitles_from_autodetection
    )

    exp_reasons = []
    if exp_hardcoded_subtitles:
        exp_reasons.append(ptp.metadata.PtpTrumpableReason.HARDCODED_SUBTITLES)
    if exp_no_english_subtitles:
        exp_reasons.append(ptp.metadata.PtpTrumpableReason.NO_ENGLISH_SUBTITLES)

    assert reasons == exp_reasons

    if exp_no_english_subtitles_from_options is None:
        assert languages_mock.call_args_list == [
            call(ptp_tracker_jobs.content_path, default=''),
        ]

    if exp_prompt and exp_no_english_subtitles_from_options is None:
        assert ptp_tracker_jobs.trumpable_job.add_prompt.call_args_list == [
            call(RadioListPrompt_mock.return_value),
        ]
        assert RadioListPrompt_mock.call_args_list == [
            call(
                question='Does this release have at least one English audio or subtitle track?',
                options=(
                    (
                        'Yes',
                        None,
                    ),
                    (
                        'No',
                        ptp.metadata.PtpTrumpableReason.NO_ENGLISH_SUBTITLES,
                    ),
                ),
                callbacks=(
                    ptp_tracker_jobs.autodetect_trumpable_no_english_subtitles_prompt_callback,
                ),
            ),
        ]
    else:
        assert ptp_tracker_jobs.trumpable_job.add_prompt.call_args_list == []
        assert RadioListPrompt_mock.call_args_list == []


@pytest.mark.parametrize(
    argnames='trumpable_reason, exp_send_calls',
    argvalues=(
        (
            ('Text', ptp.metadata.PtpTrumpableReason.NO_ENGLISH_SUBTITLES),
            [
                call(ptp.metadata.PtpTrumpableReason.NO_ENGLISH_SUBTITLES),
            ],
        ),
        (
            ('Text', None),
            [],
        ),
    ),
    ids=lambda v: str(v),
)
async def test_autodetect_trumpable_no_english_subtitles_prompt_callback(
        trumpable_reason, exp_send_calls,
        ptp_tracker_jobs, mocker,
):
    mocker.patch.object(ptp_tracker_jobs.trumpable_job, 'send')

    ptp_tracker_jobs.autodetect_trumpable_no_english_subtitles_prompt_callback(trumpable_reason)
    assert ptp_tracker_jobs.trumpable_job.send.call_args_list == exp_send_calls


def test_description_job(ptp_tracker_jobs, mocker):
    mocker.patch.object(type(ptp_tracker_jobs), 'mediainfo_job', PropertyMock())
    mocker.patch.object(type(ptp_tracker_jobs), 'upload_screenshots_job', PropertyMock())
    mocker.patch.object(ptp_tracker_jobs, 'generate_description')
    TextFieldJob_mock = mocker.patch('upsies.jobs.dialog.TextFieldJob')
    mocker.patch.object(ptp_tracker_jobs, 'get_job_name')
    mocker.patch.object(ptp_tracker_jobs, 'make_precondition')
    mocker.patch.object(ptp_tracker_jobs, 'get_job_and_dependencies')
    mocker.patch.object(ptp_tracker_jobs, 'common_job_args', return_value={'common_job_arg': 'common job argument'})

    assert ptp_tracker_jobs.description_job is TextFieldJob_mock.return_value
    assert TextFieldJob_mock.call_args_list == [call(
        name=ptp_tracker_jobs.get_job_name.return_value,
        label='Description',
        precondition=ptp_tracker_jobs.make_precondition.return_value,
        prejobs=ptp_tracker_jobs.get_job_and_dependencies.return_value,
        text=ptp_tracker_jobs.generate_description,
        read_only=True,
        hidden=True,
        finish_on_success=True,
        common_job_arg='common job argument',
    )]
    assert ptp_tracker_jobs.get_job_name.call_args_list == [call('description')]
    assert ptp_tracker_jobs.make_precondition.call_args_list == [call('description_job')]
    assert ptp_tracker_jobs.get_job_and_dependencies.call_args_list == [call(
        ptp_tracker_jobs.mediainfo_job,
        ptp_tracker_jobs.upload_screenshots_job,
    )]
    assert ptp_tracker_jobs.common_job_args.call_args_list == [call(ignore_cache=True)]


@pytest.mark.parametrize(
    argnames='content_path, exp_original_release_name',
    argvalues=(
        ('path/to/Foo.2002.720p.x264-ASDF.mkv', 'Foo.2002.720p.x264-ASDF'),
        ('path/to/Foo.2002.720p.x264-ASDF', 'Foo.2002.720p.x264-ASDF'),
        ('Foo.2002.720p.x264-ASDF.mkv', 'Foo.2002.720p.x264-ASDF'),
        ('Foo.2002.720p.x264-ASDF', 'Foo.2002.720p.x264-ASDF'),
    ),
    ids=lambda v: str(v),
)
async def test_generate_description(content_path, exp_original_release_name, ptp_tracker_jobs, mocker):
    mocker.patch.object(type(ptp_tracker_jobs), 'content_path', PropertyMock(return_value=content_path))
    mocker.patch.object(type(ptp_tracker_jobs), 'mediainfos_and_screenshots', PropertyMock(return_value={
        'path/to/video1.mkv': {
            'mediainfo': '<mediainfo of path/to/video1.mkv>',
            'screenshot_urls': (
                'http://screenshot1.of.video1.mkv',
                'http://screenshot2.of.video1.mkv',
                'http://screenshot3.of.video1.mkv',
            ),
        },
        'path/to/video2.mkv': {
            'mediainfo': None,
            'screenshot_urls': (
                'http://screenshot1.of.video2.mkv',
                'http://screenshot2.of.video2.mkv',
            ),
        },
        'path/to/video3.mkv': {
            'mediainfo': '<mediainfo of path/to/video3.mkv>',
            'screenshot_urls': (),
        },
        'path/to/video4.mkv': {
            'mediainfo': None,
            'screenshot_urls': (),
        },
    }))

    description = await ptp_tracker_jobs.generate_description()
    assert description == (
        f'[size=4][b]{exp_original_release_name}[/b][/size]'
        '\n\n'
        '[mediainfo]<mediainfo of path/to/video1.mkv>[/mediainfo]'
        '[img=http://screenshot1.of.video1.mkv]\n'
        '[img=http://screenshot2.of.video1.mkv]\n'
        '[img=http://screenshot3.of.video1.mkv]'
        '\n[hr]\n'
        '[img=http://screenshot1.of.video2.mkv]\n'
        '[img=http://screenshot2.of.video2.mkv]'
    )


def test_mediainfo_from_all_videos(ptp_tracker_jobs):
    assert ptp_tracker_jobs.mediainfo_from_all_videos is True


def test_screenshots_from_all_videos(ptp_tracker_jobs):
    assert ptp_tracker_jobs.screenshots_from_all_videos is True


@pytest.mark.parametrize(
    argnames='options, filtered_video_files, exp_screenshots_count, exp_filter_calls',
    argvalues=(
        pytest.param(
            {'screenshots': 123, 'screenshots_from_movie': 456, 'screenshots_from_episode': 789},
            None,
            123,
            False,
            id='User-provided number of screenshots',
        ),
        pytest.param(
            {'screenshots_from_movie': 456, 'screenshots_from_episode': 789},
            ['file1.mkv'],
            456,
            True,
            id='Number of screenshots for movies',
        ),
        pytest.param(
            {'screenshots_from_movie': 456, 'screenshots_from_episode': 789},
            ['foo1.mkv', 'foo2.mkv'],
            789,
            True,
            id='Number of screenshots for episodes',
        ),
    ),
    ids=lambda v: str(v),
)
def test_screenshots_count(
        options, filtered_video_files,
        exp_screenshots_count, exp_filter_calls,
        ptp_tracker_jobs, mocker,
):
    mocks = Mock()
    mocks.attach_mock(mocker.patch('upsies.utils.torrent.filter_files'), 'filter_files')
    mocks.attach_mock(
        mocker.patch('upsies.utils.video.filter_main_videos', return_value=filtered_video_files),
        'filter_main_videos',
    )
    mocker.patch.object(type(ptp_tracker_jobs), 'options', PropertyMock(return_value=options))
    mocker.patch.object(type(ptp_tracker_jobs), 'content_path', PropertyMock())
    mocker.patch.object(type(ptp_tracker_jobs), 'exclude_files', PropertyMock())

    screenshots_count = ptp_tracker_jobs.screenshots_count
    assert screenshots_count == exp_screenshots_count

    if exp_filter_calls:
        assert mocks.mock_calls == [
            call.filter_files(ptp_tracker_jobs.content_path, exclude=ptp_tracker_jobs.exclude_files),
            call.filter_main_videos(mocks.filter_files.return_value),
        ]
    else:
        assert mocks.mock_calls == []


def test_ptp_group_id_job(ptp_tracker_jobs, mocker):
    mocker.patch.object(type(ptp_tracker_jobs), 'imdb_job', PropertyMock())
    mocker.patch.object(ptp_tracker_jobs, 'fetch_ptp_group_id')
    CustomJob_mock = mocker.patch('upsies.jobs.custom.CustomJob')
    mocker.patch.object(ptp_tracker_jobs, 'get_job_name')
    mocker.patch.object(ptp_tracker_jobs, 'make_precondition')
    mocker.patch.object(ptp_tracker_jobs, 'get_job_and_dependencies')
    mocker.patch.object(ptp_tracker_jobs, 'common_job_args', return_value={'common_job_arg': 'common job argument'})

    assert ptp_tracker_jobs.ptp_group_id_job is CustomJob_mock.return_value
    assert CustomJob_mock.call_args_list == [call(
        name=ptp_tracker_jobs.get_job_name.return_value,
        label='PTP Group ID',
        precondition=ptp_tracker_jobs.make_precondition.return_value,
        prejobs=ptp_tracker_jobs.get_job_and_dependencies.return_value,
        worker=ptp_tracker_jobs.fetch_ptp_group_id,
        catch=(
            errors.RequestError,
        ),
        common_job_arg='common job argument',
    )]
    assert ptp_tracker_jobs.get_job_name.call_args_list == [call('ptp-group-id')]
    assert ptp_tracker_jobs.make_precondition.call_args_list == [call('ptp_group_id_job')]
    assert ptp_tracker_jobs.get_job_and_dependencies.call_args_list == [call(
        ptp_tracker_jobs.imdb_job,
    )]
    assert ptp_tracker_jobs.common_job_args.call_args_list == [call()]


@pytest.mark.parametrize(
    argnames='group_id, exp_group_id',
    argvalues=(
        (None, ''),
        ('123456', '123456'),
    ),
    ids=lambda v: str(v),
)
async def test_fetch_ptp_group_id(group_id, exp_group_id, ptp_tracker_jobs, mocker):
    mocker.patch.object(type(ptp_tracker_jobs), 'imdb_job', PropertyMock(return_value=Mock(is_finished=True)))
    mocker.patch.object(type(ptp_tracker_jobs), 'imdb_id', PropertyMock(return_value='tt123456'))
    mocker.patch.object(ptp_tracker_jobs.tracker, 'get_ptp_group_id_by_imdb_id', AsyncMock(return_value=group_id))

    group_id = await ptp_tracker_jobs.fetch_ptp_group_id('ignored job')
    assert group_id == exp_group_id

    assert ptp_tracker_jobs.tracker.get_ptp_group_id_by_imdb_id.call_args_list == [call(ptp_tracker_jobs.imdb_id)]


@pytest.mark.parametrize(
    argnames='ptp_group_id_job, exp_ptp_group_id',
    argvalues=(
        (Mock(is_finished=False), None),
        (Mock(is_finished=True, output=[]), None),
        (Mock(is_finished=True, output=['123']), '123'),
    ),
    ids=lambda v: str(v),
)
async def test_ptp_group_id(ptp_group_id_job, exp_ptp_group_id, ptp_tracker_jobs, mocker):
    mocker.patch.object(type(ptp_tracker_jobs), 'ptp_group_id_job', PropertyMock(return_value=ptp_group_id_job))
    ptp_group_id = ptp_tracker_jobs.ptp_group_id
    assert ptp_group_id == exp_ptp_group_id


@pytest.mark.parametrize(
    argnames='ptp_group_id_job, exp_ptp_group_does_not_exist',
    argvalues=(
        (Mock(is_finished=False), AssertionError),
        (Mock(is_finished=True, output=[]), True),
        (Mock(is_finished=True, output=['123']), False),
    ),
    ids=lambda v: str(v),
)
async def test_ptp_group_does_not_exist(ptp_group_id_job, exp_ptp_group_does_not_exist, ptp_tracker_jobs, mocker):
    mocker.patch.object(type(ptp_tracker_jobs), 'ptp_group_id_job', PropertyMock(return_value=ptp_group_id_job))
    if (
            type(exp_ptp_group_does_not_exist) is type
            and issubclass(exp_ptp_group_does_not_exist, Exception)
    ):
        with pytest.raises(exp_ptp_group_does_not_exist) as exception_info:
            ptp_tracker_jobs.ptp_group_does_not_exist()
        assert exception_info.value.args[0] is ptp_tracker_jobs.ptp_group_id_job
    else:
        ptp_group_does_not_exist = ptp_tracker_jobs.ptp_group_does_not_exist()
        assert ptp_group_does_not_exist == exp_ptp_group_does_not_exist


def test_title_job(ptp_tracker_jobs, mocker):
    mocker.patch.object(type(ptp_tracker_jobs), 'ptp_group_id_job', PropertyMock())
    mocker.patch.object(type(ptp_tracker_jobs), 'imdb_job', PropertyMock())
    mocker.patch.object(type(ptp_tracker_jobs), 'ptp_group_does_not_exist')
    TextFieldJob_mock = mocker.patch('upsies.jobs.dialog.TextFieldJob')
    mocker.patch.object(ptp_tracker_jobs, 'get_job_name')
    mocker.patch.object(ptp_tracker_jobs, 'make_precondition')
    mocker.patch.object(ptp_tracker_jobs, 'get_job_and_dependencies')
    mocker.patch.object(ptp_tracker_jobs, 'common_job_args', return_value={'common_job_arg': 'common job argument'})

    assert ptp_tracker_jobs.title_job is TextFieldJob_mock.return_value
    assert TextFieldJob_mock.call_args_list == [call(
        name=ptp_tracker_jobs.get_job_name.return_value,
        label='Title',
        precondition=ptp_tracker_jobs.make_precondition.return_value,
        prejobs=ptp_tracker_jobs.get_job_and_dependencies.return_value,
        text=ptp_tracker_jobs.fetch_title,
        normalizer=ptp_tracker_jobs.normalize_title,
        validator=ptp_tracker_jobs.validate_title,
        common_job_arg='common job argument',
    )]
    assert ptp_tracker_jobs.get_job_name.call_args_list == [call('title')]
    assert ptp_tracker_jobs.make_precondition.call_args_list == [call(
        'title_job',
        precondition=ptp_tracker_jobs.ptp_group_does_not_exist,
    )]
    assert ptp_tracker_jobs.get_job_and_dependencies.call_args_list == [call(
        ptp_tracker_jobs.ptp_group_id_job,
    )]
    assert ptp_tracker_jobs.common_job_args.call_args_list == [call()]


@pytest.mark.parametrize(
    argnames='imdb_job, exp_exception',
    argvalues=(
        (Mock(is_finished=False), AssertionError),
        (Mock(is_finished=True, output=['123']), None),
    ),
    ids=lambda v: str(v),
)
async def test_fetch_title(imdb_job, exp_exception, ptp_tracker_jobs, mocker):
    mocker.patch.object(type(ptp_tracker_jobs), 'imdb_job', PropertyMock(return_value=imdb_job))
    mocker.patch.object(ptp_tracker_jobs.tracker, 'get_ptp_metadata', AsyncMock())

    if exp_exception:
        with pytest.raises(exp_exception) as exception_info:
            await ptp_tracker_jobs.fetch_title()
        assert exception_info.value.args[0] is ptp_tracker_jobs.imdb_job
    else:
        return_value = await ptp_tracker_jobs.fetch_title()
        assert return_value == ptp_tracker_jobs.tracker.get_ptp_metadata.return_value
        ptp_tracker_jobs.tracker.get_ptp_metadata.call_args_list == [
            call(ptp_tracker_jobs.imdb_id, key='title'),
        ]


@pytest.mark.parametrize(
    argnames='text, exp_title',
    argvalues=(
        ('The Title', 'The Title'),
        (' The Title', 'The Title'),
        (' The Title  ', 'The Title'),
        ('\nThe Title\t', 'The Title'),
    ),
    ids=lambda v: str(v),
)
def test_normalize_title(text, exp_title, ptp_tracker_jobs, mocker):
    return_value = ptp_tracker_jobs.normalize_title(text)
    assert return_value == exp_title


@pytest.mark.parametrize(
    argnames='text, exp_exception',
    argvalues=(
        ('', ValueError('Title must not be empty.')),
        ('not empty', None),
    ),
    ids=lambda v: str(v),
)
async def test_validate_title(text, exp_exception, ptp_tracker_jobs, mocker):
    if exp_exception:
        with pytest.raises(type(exp_exception), match=rf'^{re.escape(str(exp_exception))}$'):
            ptp_tracker_jobs.validate_title(text)
    else:
        return_value = ptp_tracker_jobs.validate_title(text)
        assert return_value is None


def test_year_job(ptp_tracker_jobs, mocker):
    mocker.patch.object(type(ptp_tracker_jobs), 'ptp_group_id_job', PropertyMock())
    mocker.patch.object(type(ptp_tracker_jobs), 'ptp_group_does_not_exist')
    mocker.patch.object(type(ptp_tracker_jobs), 'imdb_job', PropertyMock())
    TextFieldJob_mock = mocker.patch('upsies.jobs.dialog.TextFieldJob')
    mocker.patch.object(ptp_tracker_jobs, 'get_job_name')
    mocker.patch.object(ptp_tracker_jobs, 'make_precondition')
    mocker.patch.object(ptp_tracker_jobs, 'get_job_and_dependencies')
    mocker.patch.object(ptp_tracker_jobs, 'common_job_args', return_value={'common_job_arg': 'common job argument'})

    assert ptp_tracker_jobs.year_job is TextFieldJob_mock.return_value
    assert TextFieldJob_mock.call_args_list == [call(
        name=ptp_tracker_jobs.get_job_name.return_value,
        label='Year',
        precondition=ptp_tracker_jobs.make_precondition.return_value,
        prejobs=ptp_tracker_jobs.get_job_and_dependencies.return_value,
        text=ptp_tracker_jobs.fetch_year,
        normalizer=ptp_tracker_jobs.normalize_year,
        validator=ptp_tracker_jobs.validate_year,
        common_job_arg='common job argument',
    )]
    assert ptp_tracker_jobs.get_job_name.call_args_list == [call('year')]
    assert ptp_tracker_jobs.make_precondition.call_args_list == [call(
        'year_job',
        precondition=ptp_tracker_jobs.ptp_group_does_not_exist,
    )]
    assert ptp_tracker_jobs.get_job_and_dependencies.call_args_list == [call(
        ptp_tracker_jobs.ptp_group_id_job,
    )]
    assert ptp_tracker_jobs.common_job_args.call_args_list == [call()]


@pytest.mark.parametrize(
    argnames='imdb_job, exp_exception',
    argvalues=(
        (Mock(is_finished=False), AssertionError),
        (Mock(is_finished=True, output=['2012']), None),
    ),
    ids=lambda v: str(v),
)
async def test_fetch_year(imdb_job, exp_exception, ptp_tracker_jobs, mocker):
    mocker.patch.object(type(ptp_tracker_jobs), 'imdb_job', PropertyMock(return_value=imdb_job))
    mocker.patch.object(ptp_tracker_jobs.tracker, 'get_ptp_metadata', AsyncMock())

    if exp_exception:
        with pytest.raises(exp_exception) as exception_info:
            await ptp_tracker_jobs.fetch_year()
        assert exception_info.value.args[0] is ptp_tracker_jobs.imdb_job
    else:
        return_value = await ptp_tracker_jobs.fetch_year()
        assert return_value == ptp_tracker_jobs.tracker.get_ptp_metadata.return_value
        ptp_tracker_jobs.tracker.get_ptp_metadata.call_args_list == [
            call(ptp_tracker_jobs.imdb_id, key='year'),
        ]


@pytest.mark.parametrize(
    argnames='text, exp_year',
    argvalues=(
        ('2012', '2012'),
        (' 2012', '2012'),
        (' 2012  ', '2012'),
        ('\n2012\t', '2012'),
    ),
    ids=lambda v: str(v),
)
def test_normalize_year(text, exp_year, ptp_tracker_jobs, mocker):
    return_value = ptp_tracker_jobs.normalize_year(text)
    assert return_value == exp_year


@pytest.mark.parametrize(
    argnames='text, exp_exception',
    argvalues=(
        ('', ValueError('Year must not be empty.')),
        ('not empty', ValueError('Year is not a number.')),
        ('2012.3', ValueError('Year is not a number.')),
        ('1200', ValueError('Year is not reasonable.')),
        ('2012', None),
    ),
    ids=lambda v: str(v),
)
async def test_validate_year(text, exp_exception, ptp_tracker_jobs, mocker):
    if exp_exception:
        with pytest.raises(type(exp_exception), match=rf'^{re.escape(str(exp_exception))}$'):
            ptp_tracker_jobs.validate_year(text)
    else:
        return_value = ptp_tracker_jobs.validate_year(text)
        assert return_value is None


def test_edition_job(ptp_tracker_jobs, mocker):
    TextFieldJob_mock = mocker.patch('upsies.jobs.dialog.TextFieldJob')
    mocker.patch.object(ptp_tracker_jobs, 'get_job_name')
    mocker.patch.object(ptp_tracker_jobs, 'make_precondition')
    mocker.patch.object(ptp_tracker_jobs, 'get_job_and_dependencies')
    mocker.patch.object(ptp_tracker_jobs, 'common_job_args', return_value={'common_job_arg': 'common job argument'})

    assert ptp_tracker_jobs.edition_job is TextFieldJob_mock.return_value
    assert TextFieldJob_mock.call_args_list == [call(
        name=ptp_tracker_jobs.get_job_name.return_value,
        label='Edition',
        precondition=ptp_tracker_jobs.make_precondition.return_value,
        text=ptp_tracker_jobs.autodetect_edition,
        finish_on_success=True,
        common_job_arg='common job argument',
    )]
    assert ptp_tracker_jobs.get_job_name.call_args_list == [call('edition')]
    assert ptp_tracker_jobs.make_precondition.call_args_list == [call('edition_job')]
    assert ptp_tracker_jobs.common_job_args.call_args_list == [call(ignore_cache=True)]


@pytest.mark.asyncio
async def test_autodetect_edition(ptp_tracker_jobs, mocker):
    mocker.patch('upsies.trackers.ptp.metadata.ptp_editions', {
        'theatrical': 'Theatrical Cut',
        'unrated': 'Unrated',
        '10b': '10-bit',
        'remux': 'Remux',
    })
    mocker.patch.object(ptp_tracker_jobs, 'autodetect_edition_map', {
        'theatrical': lambda self: False,
        'unrated': lambda self: True,
        '10b': lambda self: True,
        'remux': lambda self: True,
    })
    return_value = await ptp_tracker_jobs.autodetect_edition()
    assert return_value == 'Unrated / 10-bit / Remux'


@dataclasses.dataclass
class MockReleaseName:
    edition: str = ''
    source: str = ''
    hdr_format: str = ''
    audio_format: str = ''
    has_dual_audio: bool = False
    has_commentary: bool = False

def assert_edition_keys_for(ptp_tracker_jobs, exp_keys):
    keys = [
        key
        for key, is_edition in ptp_tracker_jobs.autodetect_edition_map.items()
        if is_edition(ptp_tracker_jobs)
    ]
    assert keys == exp_keys

@pytest.mark.parametrize(
    argnames='release_name, exp_keys',
    argvalues=(
        (MockReleaseName(edition=''), []),
        (MockReleaseName(edition='Criterion'), ['collection.criterion']),
        (MockReleaseName(edition='Criterion Collection'), ['collection.criterion']),
        (MockReleaseName(edition="foo Criterion bar"), ['collection.criterion']),
    ),
    ids=lambda v: repr(v),
)
async def test_autodetect_edition_map__collection_criterion(release_name, exp_keys, ptp_tracker_jobs, mocker):
    mocker.patch.object(type(ptp_tracker_jobs), 'release_name', PropertyMock(return_value=release_name))
    assert_edition_keys_for(ptp_tracker_jobs, exp_keys)

@pytest.mark.parametrize(
    argnames='release_name, exp_keys',
    argvalues=(
        (MockReleaseName(edition=''), []),
        (MockReleaseName(edition="Director's Cut"), ['edition.dc']),
        (MockReleaseName(edition="foo Director's Cut bar"), ['edition.dc']),
    ),
    ids=lambda v: repr(v),
)
async def test_autodetect_edition_map__edition_dc(release_name, exp_keys, ptp_tracker_jobs, mocker):
    mocker.patch.object(type(ptp_tracker_jobs), 'release_name', PropertyMock(return_value=release_name))
    assert_edition_keys_for(ptp_tracker_jobs, exp_keys)

@pytest.mark.parametrize(
    argnames='release_name, exp_keys',
    argvalues=(
        (MockReleaseName(edition=''), []),
        (MockReleaseName(edition="Extended Cut"), ['edition.extended']),
        (MockReleaseName(edition="foo Extended Cut bar"), ['edition.extended']),
    ),
    ids=lambda v: repr(v),
)
async def test_autodetect_edition_map__edition_extended(release_name, exp_keys, ptp_tracker_jobs, mocker):
    mocker.patch.object(type(ptp_tracker_jobs), 'release_name', PropertyMock(return_value=release_name))
    assert_edition_keys_for(ptp_tracker_jobs, exp_keys)

@pytest.mark.parametrize(
    argnames='release_name, exp_keys',
    argvalues=(
        (MockReleaseName(edition=''), []),
        (MockReleaseName(edition="Theatrical Cut"), ['edition.theatrical']),
        (MockReleaseName(edition="foo Theatrical Cut bar"), ['edition.theatrical']),
    ),
    ids=lambda v: repr(v),
)
async def test_autodetect_edition_map__edition_theatrical(release_name, exp_keys, ptp_tracker_jobs, mocker):
    mocker.patch.object(type(ptp_tracker_jobs), 'release_name', PropertyMock(return_value=release_name))
    assert_edition_keys_for(ptp_tracker_jobs, exp_keys)

@pytest.mark.parametrize(
    argnames='release_name, exp_keys',
    argvalues=(
        (MockReleaseName(edition=''), []),
        (MockReleaseName(edition="Uncut"), ['edition.uncut']),
        (MockReleaseName(edition="foo Uncut bar"), ['edition.uncut']),
    ),
    ids=lambda v: repr(v),
)
async def test_autodetect_edition_map__edition_uncut(release_name, exp_keys, ptp_tracker_jobs, mocker):
    mocker.patch.object(type(ptp_tracker_jobs), 'release_name', PropertyMock(return_value=release_name))
    assert_edition_keys_for(ptp_tracker_jobs, exp_keys)

@pytest.mark.parametrize(
    argnames='release_name, exp_keys',
    argvalues=(
        (MockReleaseName(edition=''), []),
        (MockReleaseName(edition="Unrated"), ['edition.unrated']),
        (MockReleaseName(edition="foo Unrated bar"), ['edition.unrated']),
    ),
    ids=lambda v: repr(v),
)
async def test_autodetect_edition_map__edition_unrated(release_name, exp_keys, ptp_tracker_jobs, mocker):
    mocker.patch.object(type(ptp_tracker_jobs), 'release_name', PropertyMock(return_value=release_name))
    assert_edition_keys_for(ptp_tracker_jobs, exp_keys)

@pytest.mark.parametrize(
    argnames='release_name, exp_keys',
    argvalues=(
        (MockReleaseName(source=''), []),
        (MockReleaseName(source='Remux'), ['feature.remux']),
        (MockReleaseName(source='foo Remux bar'), ['feature.remux']),
    ),
    ids=lambda v: repr(v),
)
async def test_autodetect_edition_map__feature_remux(release_name, exp_keys, ptp_tracker_jobs, mocker):
    mocker.patch.object(type(ptp_tracker_jobs), 'release_name', PropertyMock(return_value=release_name))
    assert_edition_keys_for(ptp_tracker_jobs, exp_keys)

@pytest.mark.parametrize(
    argnames='release_name, exp_keys',
    argvalues=(
        (MockReleaseName(edition=''), []),
        (MockReleaseName(edition='2in1'), ['feature.2in1']),
        (MockReleaseName(edition='foo 2in1 bar'), ['feature.2in1']),
    ),
    ids=lambda v: repr(v),
)
async def test_autodetect_edition_map__feature_2in1(release_name, exp_keys, ptp_tracker_jobs, mocker):
    mocker.patch.object(type(ptp_tracker_jobs), 'release_name', PropertyMock(return_value=release_name))
    assert_edition_keys_for(ptp_tracker_jobs, exp_keys)

@pytest.mark.parametrize(
    argnames='release_name, exp_keys',
    argvalues=(
        (MockReleaseName(edition=''), []),
        (MockReleaseName(edition='4k Restored'), ['feature.4krestoration']),
        (MockReleaseName(edition='foo 4k Restored bar'), ['feature.4krestoration']),
    ),
    ids=lambda v: repr(v),
)
async def test_autodetect_edition_map__feature_4krestoration(release_name, exp_keys, ptp_tracker_jobs, mocker):
    mocker.patch.object(type(ptp_tracker_jobs), 'release_name', PropertyMock(return_value=release_name))
    assert_edition_keys_for(ptp_tracker_jobs, exp_keys)

@pytest.mark.parametrize(
    argnames='release_name, exp_keys',
    argvalues=(
        (MockReleaseName(edition=''), []),
        (MockReleaseName(edition='4k Remastered'), ['feature.4kremaster']),
        (MockReleaseName(edition='foo 4k Remastered bar'), ['feature.4kremaster']),
    ),
    ids=lambda v: repr(v),
)
async def test_autodetect_edition_map__feature_4kremaster(release_name, exp_keys, ptp_tracker_jobs, mocker):
    mocker.patch.object(type(ptp_tracker_jobs), 'release_name', PropertyMock(return_value=release_name))
    assert_edition_keys_for(ptp_tracker_jobs, exp_keys)

@pytest.mark.parametrize(
    argnames='release_name, bit_depth, exp_keys',
    argvalues=(
        (MockReleaseName(hdr_format=''), 8, []),
        (MockReleaseName(hdr_format=''), 10, ['feature.10bit']),
        (MockReleaseName(hdr_format='HDR10'), 10, ['feature.hdr10']),
        (MockReleaseName(hdr_format='HDR10+'), 10, ['feature.hdr10+']),
        (MockReleaseName(hdr_format='DV'), 10, ['feature.dolby_vision']),
    ),
    ids=lambda v: repr(v),
)
async def test_autodetect_edition_map__feature_10bit(release_name, bit_depth, exp_keys, ptp_tracker_jobs, mocker):
    mocker.patch.object(type(ptp_tracker_jobs), 'release_name', PropertyMock(return_value=release_name))
    bit_depth_mock = mocker.patch('upsies.utils.video.bit_depth', return_value=bit_depth)
    assert_edition_keys_for(ptp_tracker_jobs, exp_keys)
    assert bit_depth_mock.call_args_list == [call(ptp_tracker_jobs.content_path, default=None)]

@pytest.mark.parametrize(
    argnames='release_name, exp_keys',
    argvalues=(
        (MockReleaseName(audio_format=''), []),
        (MockReleaseName(audio_format='DTS:X'), ['feature.dtsx']),
        (MockReleaseName(audio_format='foo DTS:X bar'), ['feature.dtsx']),

    ),
    ids=lambda v: repr(v),
)
async def test_autodetect_edition_map__feature_dtsx(release_name, exp_keys, ptp_tracker_jobs, mocker):
    mocker.patch.object(type(ptp_tracker_jobs), 'release_name', PropertyMock(return_value=release_name))
    assert_edition_keys_for(ptp_tracker_jobs, exp_keys)

@pytest.mark.parametrize(
    argnames='release_name, exp_keys',
    argvalues=(
        (MockReleaseName(audio_format=''), []),
        (MockReleaseName(audio_format='Atmos'), ['feature.dolby_atmos']),
        (MockReleaseName(audio_format='foo Atmos bar'), ['feature.dolby_atmos']),
    ),
    ids=lambda v: repr(v),
)
async def test_autodetect_edition_map__feature_dolby_atmos(release_name, exp_keys, ptp_tracker_jobs, mocker):
    mocker.patch.object(type(ptp_tracker_jobs), 'release_name', PropertyMock(return_value=release_name))
    assert_edition_keys_for(ptp_tracker_jobs, exp_keys)

@pytest.mark.parametrize(
    argnames='release_name, exp_keys',
    argvalues=(
        (MockReleaseName(hdr_format=''), []),
        (MockReleaseName(hdr_format='DV'), ['feature.dolby_vision']),
        (MockReleaseName(hdr_format='foo DV bar'), ['feature.dolby_vision']),
    ),
    ids=lambda v: repr(v),
)
async def test_autodetect_edition_map__feature_dolby_vision(release_name, exp_keys, ptp_tracker_jobs, mocker):
    mocker.patch.object(type(ptp_tracker_jobs), 'release_name', PropertyMock(return_value=release_name))
    assert_edition_keys_for(ptp_tracker_jobs, exp_keys)

@pytest.mark.parametrize(
    argnames='release_name, exp_keys',
    argvalues=(
        (MockReleaseName(hdr_format=''), []),
        (MockReleaseName(hdr_format='HDR10'), ['feature.hdr10']),
        (MockReleaseName(hdr_format='foo HDR10 bar'), ['feature.hdr10']),
    ),
    ids=lambda v: repr(v),
)
async def test_autodetect_edition_map__feature_hdr10(release_name, exp_keys, ptp_tracker_jobs, mocker):
    mocker.patch.object(type(ptp_tracker_jobs), 'release_name', PropertyMock(return_value=release_name))
    assert_edition_keys_for(ptp_tracker_jobs, exp_keys)

@pytest.mark.parametrize(
    argnames='release_name, exp_keys',
    argvalues=(
        (MockReleaseName(hdr_format=''), []),
        (MockReleaseName(hdr_format='HDR10+'), ['feature.hdr10+']),
        (MockReleaseName(hdr_format='foo HDR10+ bar'), ['feature.hdr10+']),
    ),
    ids=lambda v: repr(v),
)
async def test_autodetect_edition_map__feature_hdr10plus(release_name, exp_keys, ptp_tracker_jobs, mocker):
    mocker.patch.object(type(ptp_tracker_jobs), 'release_name', PropertyMock(return_value=release_name))
    assert_edition_keys_for(ptp_tracker_jobs, exp_keys)

@pytest.mark.parametrize(
    argnames='release_name, exp_keys',
    argvalues=(
        (MockReleaseName(has_dual_audio=False), []),
        (MockReleaseName(has_dual_audio=True), ['feature.dual_audio']),
    ),
    ids=lambda v: repr(v),
)
async def test_autodetect_edition_map__feature_dual_audio(release_name, exp_keys, ptp_tracker_jobs, mocker):
    mocker.patch.object(type(ptp_tracker_jobs), 'release_name', PropertyMock(return_value=release_name))
    assert_edition_keys_for(ptp_tracker_jobs, exp_keys)

@pytest.mark.parametrize(
    argnames='release_name, exp_keys',
    argvalues=(
        (MockReleaseName(has_commentary=False), []),
        (MockReleaseName(has_commentary=True), ['feature.commentary']),
    ),
    ids=lambda v: repr(v),
)
async def test_autodetect_edition_map__feature_commentary(release_name, exp_keys, ptp_tracker_jobs, mocker):
    mocker.patch.object(type(ptp_tracker_jobs), 'release_name', PropertyMock(return_value=release_name))
    assert_edition_keys_for(ptp_tracker_jobs, exp_keys)


def test_tags_job(ptp_tracker_jobs, mocker):
    mocker.patch.object(type(ptp_tracker_jobs), 'ptp_group_id_job', PropertyMock())
    mocker.patch.object(type(ptp_tracker_jobs), 'ptp_group_does_not_exist')
    mocker.patch.object(type(ptp_tracker_jobs), 'imdb_job', PropertyMock())
    TextFieldJob_mock = mocker.patch('upsies.jobs.dialog.TextFieldJob')
    mocker.patch.object(ptp_tracker_jobs, 'get_job_name')
    mocker.patch.object(ptp_tracker_jobs, 'make_precondition')
    mocker.patch.object(ptp_tracker_jobs, 'get_job_and_dependencies')
    mocker.patch.object(ptp_tracker_jobs, 'common_job_args', return_value={'common_job_arg': 'common job argument'})

    assert ptp_tracker_jobs.tags_job is TextFieldJob_mock.return_value
    assert TextFieldJob_mock.call_args_list == [call(
        name=ptp_tracker_jobs.get_job_name.return_value,
        label='Tags',
        precondition=ptp_tracker_jobs.make_precondition.return_value,
        prejobs=ptp_tracker_jobs.get_job_and_dependencies.return_value,
        text=ptp_tracker_jobs.fetch_tags,
        normalizer=ptp_tracker_jobs.normalize_tags,
        validator=ptp_tracker_jobs.validate_tags,
        common_job_arg='common job argument',
    )]
    assert ptp_tracker_jobs.get_job_name.call_args_list == [call('tags')]
    assert ptp_tracker_jobs.make_precondition.call_args_list == [call(
        'tags_job',
        precondition=ptp_tracker_jobs.ptp_group_does_not_exist,
    )]
    assert ptp_tracker_jobs.get_job_and_dependencies.call_args_list == [call(
        ptp_tracker_jobs.ptp_group_id_job,
    )]
    assert ptp_tracker_jobs.common_job_args.call_args_list == [call()]


@pytest.mark.parametrize(
    argnames='imdb_job, exp_exception',
    argvalues=(
        (Mock(is_finished=False), AssertionError),
        (Mock(is_finished=True, output=['foo,bar,baz']), None),
    ),
    ids=lambda v: str(v),
)
async def test_fetch_tags(imdb_job, exp_exception, ptp_tracker_jobs, mocker):
    mocker.patch.object(type(ptp_tracker_jobs), 'imdb_job', PropertyMock(return_value=imdb_job))
    mocker.patch.object(ptp_tracker_jobs.tracker, 'get_ptp_metadata', AsyncMock())

    if exp_exception:
        with pytest.raises(exp_exception) as exception_info:
            await ptp_tracker_jobs.fetch_tags()
        assert exception_info.value.args[0] is ptp_tracker_jobs.imdb_job
    else:
        return_value = await ptp_tracker_jobs.fetch_tags()
        assert return_value == ptp_tracker_jobs.tracker.get_ptp_metadata.return_value
        ptp_tracker_jobs.tracker.get_ptp_metadata.call_args_list == [
            call(ptp_tracker_jobs.imdb_id, key='tags'),
        ]


@pytest.mark.parametrize(
    argnames='text, exp_tags',
    argvalues=(
        pytest.param('foo,bar,baz', 'bar, baz, foo', id='Tags are sorted'),
        pytest.param('foo,bar,baz,foo', 'bar, baz, foo', id='Tags are deduplicated'),
        pytest.param(',,,foo,,bar,baz,', 'bar, baz, foo', id='Empty tags are ignored'),
    ),
    ids=lambda v: str(v),
)
def test_normalize_tags(text, exp_tags, ptp_tracker_jobs, mocker):
    return_value = ptp_tracker_jobs.normalize_tags(text)
    assert return_value == exp_tags


@pytest.mark.parametrize(
    argnames='text, exp_exception',
    argvalues=(
        ('horror,awesome,drama', ValueError('Tag is not valid: awesome')),
        ('horror,drama', None),
        ('', None),
    ),
    ids=lambda v: str(v),
)
async def test_validate_tags(text, exp_exception, ptp_tracker_jobs, mocker):
    if exp_exception:
        with pytest.raises(type(exp_exception), match=rf'^{re.escape(str(exp_exception))}$'):
            ptp_tracker_jobs.validate_tags(text)
    else:
        return_value = ptp_tracker_jobs.validate_tags(text)
        assert return_value is None


async def test_poster_job(ptp_tracker_jobs, mocker):
    mocker.patch('upsies.trackers.base.jobs.TrackerJobsBase.poster_job', Mock(prejobs=('foo', 'bar')))
    mocker.patch.object(type(ptp_tracker_jobs), 'imdb_job', PropertyMock(return_value='<imdb job>'))
    mocker.patch.object(type(ptp_tracker_jobs), 'ptp_group_id_job', PropertyMock(return_value='<ptp_group_id job>'))
    poster_job = ptp_tracker_jobs.poster_job
    assert poster_job.prejobs == (
        'foo',
        'bar',
        ptp_tracker_jobs.imdb_job,
        ptp_tracker_jobs.ptp_group_id_job,
    )


@pytest.mark.parametrize(
    argnames='poster, exp_return_value',
    argvalues=(
        (None, None),
        ('', None),
        ('http://myposter.jpg', {
            'poster': 'http://myposter.jpg',
            'width': None,
            'height': None,
            'imghosts': (),
            'write_to': None,
        }),
    ),
    ids=lambda v: str(v),
)
async def test_get_poster_from_tracker(poster, exp_return_value, ptp_tracker_jobs, mocker):
    mocks = Mock()
    mocks.attach_mock(
        mocker.patch.object(type(ptp_tracker_jobs), 'imdb_job', PropertyMock(return_value=Mock(wait=AsyncMock()))),
        'wait',
    )
    mocks.attach_mock(
        mocker.patch.object(ptp_tracker_jobs.tracker, 'get_ptp_metadata', AsyncMock(return_value=poster)),
        'get_ptp_metadata',
    )
    mocker.patch.object(type(ptp_tracker_jobs), 'imdb_id', PropertyMock(return_value='tt0123'))

    return_value = await ptp_tracker_jobs.get_poster_from_tracker()
    assert return_value == exp_return_value
    assert mocks.mock_calls == [
        call.wait(),
        call.get_ptp_metadata('tt0123', key='art'),
    ]


def test_plot_job(ptp_tracker_jobs, mocker):
    mocker.patch.object(type(ptp_tracker_jobs), 'ptp_group_id_job', PropertyMock())
    mocker.patch.object(type(ptp_tracker_jobs), 'ptp_group_does_not_exist')
    mocker.patch.object(type(ptp_tracker_jobs), 'imdb_job', PropertyMock())
    TextFieldJob_mock = mocker.patch('upsies.jobs.dialog.TextFieldJob')
    mocker.patch.object(ptp_tracker_jobs, 'get_job_name')
    mocker.patch.object(ptp_tracker_jobs, 'make_precondition')
    mocker.patch.object(ptp_tracker_jobs, 'get_job_and_dependencies')
    mocker.patch.object(ptp_tracker_jobs, 'common_job_args', return_value={'common_job_arg': 'common job argument'})

    assert ptp_tracker_jobs.plot_job is TextFieldJob_mock.return_value
    assert TextFieldJob_mock.call_args_list == [call(
        name=ptp_tracker_jobs.get_job_name.return_value,
        label='Plot',
        precondition=ptp_tracker_jobs.make_precondition.return_value,
        prejobs=ptp_tracker_jobs.get_job_and_dependencies.return_value,
        text=ptp_tracker_jobs.fetch_plot,
        normalizer=ptp_tracker_jobs.normalize_plot,
        validator=ptp_tracker_jobs.validate_plot,
        finish_on_success=True,
        common_job_arg='common job argument',
    )]
    assert ptp_tracker_jobs.get_job_name.call_args_list == [call('plot')]
    assert ptp_tracker_jobs.make_precondition.call_args_list == [call(
        'plot_job',
        precondition=ptp_tracker_jobs.ptp_group_does_not_exist,
    )]
    assert ptp_tracker_jobs.get_job_and_dependencies.call_args_list == [call(
        ptp_tracker_jobs.ptp_group_id_job,
    )]
    assert ptp_tracker_jobs.common_job_args.call_args_list == [call()]


@pytest.mark.parametrize(
    argnames='imdb_job, exp_exception',
    argvalues=(
        (Mock(is_finished=False), AssertionError),
        (Mock(is_finished=True, output=['123']), None),
    ),
    ids=lambda v: str(v),
)
async def test_fetch_plot(imdb_job, exp_exception, ptp_tracker_jobs, mocker):
    mocker.patch.object(type(ptp_tracker_jobs), 'imdb_job', PropertyMock(return_value=imdb_job))
    mocker.patch.object(ptp_tracker_jobs.tracker, 'get_ptp_metadata', AsyncMock())

    if exp_exception:
        with pytest.raises(exp_exception) as exception_info:
            await ptp_tracker_jobs.fetch_plot()
        assert exception_info.value.args[0] is ptp_tracker_jobs.imdb_job
    else:
        return_value = await ptp_tracker_jobs.fetch_plot()
        assert return_value == ptp_tracker_jobs.tracker.get_ptp_metadata.return_value
        ptp_tracker_jobs.tracker.get_ptp_metadata.call_args_list == [
            call(ptp_tracker_jobs.imdb_id, key='plot'),
        ]


@pytest.mark.parametrize(
    argnames='text, exp_plot',
    argvalues=(
        ('The plot.', 'The plot.'),
        (' The plot.', 'The plot.'),
        (' The plot.  ', 'The plot.'),
        ('\nThe plot.\t', 'The plot.'),
    ),
    ids=lambda v: str(v),
)
def test_normalize_plot(text, exp_plot, ptp_tracker_jobs, mocker):
    return_value = ptp_tracker_jobs.normalize_plot(text)
    assert return_value == exp_plot


@pytest.mark.parametrize(
    argnames='text, exp_exception',
    argvalues=(
        ('', ValueError('Plot must not be empty.')),
        ('not empty', None),
    ),
    ids=lambda v: str(v),
)
async def test_validate_plot(text, exp_exception, ptp_tracker_jobs, mocker):
    if exp_exception:
        with pytest.raises(type(exp_exception), match=rf'^{re.escape(str(exp_exception))}$'):
            ptp_tracker_jobs.validate_plot(text)
    else:
        return_value = ptp_tracker_jobs.validate_plot(text)
        assert return_value is None


def test_source_job(ptp_tracker_jobs, mocker):
    TextFieldJob_mock = mocker.patch('upsies.jobs.dialog.TextFieldJob')
    mocker.patch.object(ptp_tracker_jobs, 'get_job_name')
    mocker.patch.object(ptp_tracker_jobs, 'make_precondition')
    mocker.patch.object(ptp_tracker_jobs, 'common_job_args', return_value={'common_job_arg': 'common job argument'})

    assert ptp_tracker_jobs.source_job is TextFieldJob_mock.return_value
    assert TextFieldJob_mock.call_args_list == [call(
        name=ptp_tracker_jobs.get_job_name.return_value,
        label='Source',
        precondition=ptp_tracker_jobs.make_precondition.return_value,
        text=ptp_tracker_jobs.autodetect_source,
        normalizer=ptp_tracker_jobs.normalize_source,
        validator=ptp_tracker_jobs.validate_source,
        finish_on_success=True,
        common_job_arg='common job argument',
    )]
    assert ptp_tracker_jobs.get_job_name.call_args_list == [call('source')]
    assert ptp_tracker_jobs.make_precondition.call_args_list == [call('source_job')]
    assert ptp_tracker_jobs.common_job_args.call_args_list == [call()]


@pytest.mark.parametrize(
    argnames='release_name_source, exp_source, exp_source_job_text',
    argvalues=(
        ('BluRay', 'Blu-ray', None),
        ('DVD', 'DVD', None),
        ('DVDRip', 'DVD', None),
        ('WEB', 'WEB', None),
        ('WEB-DL', 'WEB', None),
        ('WEBDL', 'WEB', None),
        ('WEBRip', 'WEB', None),
        ('HD-DVD', 'HD-DVD', None),
        ('HDDVD', 'HD-DVD', None),
        ('HD-TV', 'HDTV', None),
        ('HDTV', 'HDTV', None),
        ('TV', 'TV', None),
        ('VHS', 'VHS', None),
        ('VHSRip', 'VHS', None),
        ('YerMom', None, 'YerMom'),
    ),
    ids=lambda v: str(v),
)
def test_autodetect_source(release_name_source, exp_source, exp_source_job_text, ptp_tracker_jobs, mocker):
    mocker.patch.object(type(ptp_tracker_jobs), 'release_name', PropertyMock(return_value=Mock(
        source=release_name_source,
    )))
    mocker.patch.object(type(ptp_tracker_jobs), 'source_job', PropertyMock(return_value=Mock(
        text='not set',
    )))

    return_value = ptp_tracker_jobs.autodetect_source()
    assert return_value == exp_source
    if exp_source_job_text is not None:
        assert ptp_tracker_jobs.source_job.text == exp_source_job_text
    else:
        assert ptp_tracker_jobs.source_job.text == 'not set'


@pytest.mark.parametrize(
    argnames='text, exp_source',
    argvalues=(
        ('blu-ray', 'Blu-ray'),
        ('Blu-ray', 'Blu-ray'),
        ('BLU-RAY', 'Blu-ray'),
        ('YerMom', 'YerMom'),
    ),
    ids=lambda v: str(v),
)
def test_normalize_source(text, exp_source, ptp_tracker_jobs, mocker):
    return_value = ptp_tracker_jobs.normalize_source(text)
    assert return_value == exp_source


@pytest.mark.parametrize(
    argnames='text, exp_exception',
    argvalues=(
        ('', ValueError('You must provide a source.')),
        ('UNKNOWN_SOURCE', ValueError('You must provide a source.')),
        ('KNOWN_SOURCE', ValueError('Source is not valid: KNOWN_SOURCE')),
        ('Blu-ray', None),
    ),
    ids=lambda v: str(v),
)
async def test_validate_source(text, exp_exception, ptp_tracker_jobs, mocker):
    if exp_exception:
        with pytest.raises(type(exp_exception), match=rf'^{re.escape(str(exp_exception))}$'):
            ptp_tracker_jobs.validate_source(text)
    else:
        return_value = ptp_tracker_jobs.validate_source(text)
        assert return_value is None


@pytest.mark.parametrize(
    argnames='ptp_group_id, post_data_common, post_data_add_movie_format, post_data_add_new_movie, exp_post_data',
    argvalues=(
        (
            None,
            {'common': 'data', 'more': 'common values'},
            {'add': 'format', 'common': 'data for adding movie format'},
            {'new': 'movie', 'common': 'data for adding new movie'},
            {'new': 'movie', 'common': 'data for adding new movie', 'more': 'common values'},
        ),
        (
            '123456',
            {'common': 'data', 'more': 'common values'},
            {'add': 'format', 'common': 'data for adding movie format'},
            {'new': 'movie', 'common': 'data for adding new movie'},
            {'add': 'format', 'common': 'data for adding movie format', 'more': 'common values'},
        ),
    ),
    ids=lambda v: str(v),
)
async def test_post_data(
        ptp_group_id,
        post_data_common, post_data_add_movie_format, post_data_add_new_movie,
        exp_post_data,
        ptp_tracker_jobs, mocker,
):
    mocker.patch.object(type(ptp_tracker_jobs), 'ptp_group_id', PropertyMock(return_value=ptp_group_id))
    mocker.patch.object(type(ptp_tracker_jobs), '_post_data_common', PropertyMock(return_value=post_data_common))
    mocker.patch.object(type(ptp_tracker_jobs), '_post_data_add_movie_format', PropertyMock(return_value=post_data_add_movie_format))
    mocker.patch.object(type(ptp_tracker_jobs), '_post_data_add_new_movie', PropertyMock(return_value=post_data_add_new_movie))
    assert ptp_tracker_jobs.post_data == exp_post_data


@pytest.mark.parametrize('not_main_movie, exp_special', ((True, '1'), (False, None)))
@pytest.mark.parametrize('personal_rip, exp_internalrip', ((True, '1'), (False, None)))
@pytest.mark.parametrize('is_scene_release, exp_scene', ((True, '1'), (False, None)))
def test__post_data_common(
        not_main_movie, exp_special,
        personal_rip, exp_internalrip,
        is_scene_release, exp_scene,
        ptp_tracker_jobs, mock_job_attributes, mocker,
):
    mock_job_attributes(ptp_tracker_jobs)

    mocks = Mock()
    mocks.attach_mock(
        mocker.patch.object(ptp_tracker_jobs, 'get_job_attribute', side_effect=(
            '<type>',
            is_scene_release,
        )),
        'get_job_attribute',
    )
    mocks.attach_mock(
        mocker.patch.object(ptp_tracker_jobs, 'get_job_output', side_effect=(
            '<description>',
        )),
        'get_job_output',
    )
    mocker.patch.object(ptp_tracker_jobs, 'read_nfo', Mock(return_value='<nfo text>'))
    mocker.patch.object(type(ptp_tracker_jobs), 'options', PropertyMock(return_value={
        'not_main_movie': not_main_movie,
        'personal_rip': personal_rip,
        'upload_token': '<upload token>',
    }))
    for name in ('source', 'codec', 'container', 'resolution', 'edition', 'subtitles', 'trumpable'):
        mocker.patch.object(
            type(ptp_tracker_jobs),
            f'_post_data_common_{name}',
            PropertyMock(return_value={name: 'post data'}),
        )

    exp_post_data = {
        'type': '<type>',
        'release_desc': '<description>',
        'special': exp_special,
        'internalrip': exp_internalrip,
        'scene': exp_scene,
        'nfo_text': '<nfo text>',
        'uploadtoken': '<upload token>',
        'source': 'post data',
        'codec': 'post data',
        'container': 'post data',
        'resolution': 'post data',
        'edition': 'post data',
        'subtitles': 'post data',
        'trumpable': 'post data',
    }

    assert ptp_tracker_jobs._post_data_common == exp_post_data

    assert mocks.mock_calls == [
        call.get_job_attribute(ptp_tracker_jobs.type_job, 'choice'),
        call.get_job_output(ptp_tracker_jobs.description_job, slice=0),
        call.get_job_attribute(ptp_tracker_jobs.scene_check_job, 'is_scene_release'),
    ]


def test__post_data_common_source(ptp_tracker_jobs, mocker):
    mocker.patch.object(ptp_tracker_jobs, 'get_job_output')
    assert ptp_tracker_jobs._post_data_common_source == {
        'source': 'Other',
        'other_source': ptp_tracker_jobs.get_job_output.return_value,
    }
    assert ptp_tracker_jobs.get_job_output.call_args_list == [
        call(ptp_tracker_jobs.source_job, slice=0),
    ]


def test__post_data_common_codec(ptp_tracker_jobs, mocker):
    assert ptp_tracker_jobs._post_data_common_codec == {
        'codec': '* Auto-detect',
        'other_codec': '',
    }


def test__post_data_common_container(ptp_tracker_jobs, mocker):
    assert ptp_tracker_jobs._post_data_common_container == {
        'container': '* Auto-detect',
        'other_container': ''
    }


def test__post_data_common_resolution(ptp_tracker_jobs, mocker):
    assert ptp_tracker_jobs._post_data_common_resolution == {
        'resolution': '* Auto-detect',
        'other_resolution': ''
    }


@pytest.mark.parametrize(
    argnames='subtitles, ptp_subtitles, exp_post_data',
    argvalues=(
        pytest.param(
            [],
            {
                'No Subtitles': 0,
                'la-ta (forced)': 1,
                'la-ta': 2,
                'la (forced)': 3,
                'la': 4,
            },
            {'subtitles[]': [0]},
            id='No subtitles'
        ),
        pytest.param(
            [
                # Subtitles that have PTP codes
                Mock(language='la', region='ta', forced=True),
                Mock(language='la', region='ta', forced=False),
                Mock(language='la', region='', forced=True),
                Mock(language='la', region='', forced=False),

                # Subtitles that do not have PTP codes
                Mock(language='lx', region='ta', forced=True),
                Mock(language='lx', region='ta', forced=False),
                Mock(language='lx', region='', forced=True),
                Mock(language='lx', region='', forced=False),
            ],
            {
                'No Subtitles': 0,
                'la-ta (forced)': 1,
                'la-ta': 2,
                'la (forced)': 3,
                'la': 4,
            },
            {'subtitles[]': [1, 2, 3, 4]},
            id='Supported and unsupported subtitles'
        ),
        pytest.param(
            [
                # Subtitles that do not have PTP codes
                Mock(language='lx', region='ta', forced=True),
                Mock(language='lx', region='ta', forced=False),
                Mock(language='lx', region='', forced=True),
                Mock(language='lx', region='', forced=False),
            ],
            {
                'No Subtitles': 0,
                'la-ta (forced)': 1,
                'la-ta': 2,
                'la (forced)': 3,
                'la': 4,
            },
            {'subtitles[]': []},
            id='Only unsupported subtitles'
        ),
    ),
    ids=lambda v: str(v),
)
def test__post_data_common_subtitles(subtitles, ptp_subtitles, exp_post_data, ptp_tracker_jobs, mocker):
    mocker.patch.object(type(ptp_tracker_jobs), 'subtitles', PropertyMock(return_value=subtitles))
    mocker.patch.dict(ptp.metadata.ptp_subtitles, ptp_subtitles, clear=True)
    assert ptp_tracker_jobs._post_data_common_subtitles == exp_post_data


@pytest.mark.parametrize(
    argnames='edition_text, exp_post_data',
    argvalues=(
        ('', {'remaster': None, 'remaster_title': None}),
        ('Superdupercut', {'remaster': 'on', 'remaster_title': 'Superdupercut'}),
    ),
    ids=lambda v: repr(v),
)
def test__post_data_common_edition(edition_text, exp_post_data, ptp_tracker_jobs, mocker):
    mocker.patch.object(ptp_tracker_jobs, 'get_job_output', return_value=edition_text)
    assert ptp_tracker_jobs._post_data_common_edition == exp_post_data
    assert ptp_tracker_jobs.get_job_output.call_args_list == [
        call(ptp_tracker_jobs.edition_job, slice=0),
    ]


@pytest.mark.parametrize(
    argnames='trumpable_job_output, exp_post_data',
    argvalues=(
        ((), {'trumpable[]': []}),
        (
            (
                str(ptp.metadata.PtpTrumpableReason.HARDCODED_SUBTITLES),
            ),
            {
                'trumpable[]': [
                    ptp.metadata.PtpTrumpableReason.HARDCODED_SUBTITLES.value,
                ],
            },
        ),
        (
            (
                str(ptp.metadata.PtpTrumpableReason.NO_ENGLISH_SUBTITLES),
            ),
            {
                'trumpable[]': [
                    ptp.metadata.PtpTrumpableReason.NO_ENGLISH_SUBTITLES.value,
                ],
            },
        ),
        (
            (
                str(ptp.metadata.PtpTrumpableReason.HARDCODED_SUBTITLES),
                str(ptp.metadata.PtpTrumpableReason.NO_ENGLISH_SUBTITLES),
            ),
            {
                'trumpable[]': [
                    ptp.metadata.PtpTrumpableReason.HARDCODED_SUBTITLES.value,
                    ptp.metadata.PtpTrumpableReason.NO_ENGLISH_SUBTITLES.value,
                ],
            },
        ),
    ),
    ids=lambda v: str(v),
)
def test__post_data_common_trumpable(trumpable_job_output, exp_post_data, ptp_tracker_jobs, mocker):
    mocker.patch.object(type(ptp_tracker_jobs), 'trumpable_job', PropertyMock(return_value=Mock(
        output=trumpable_job_output,
    )))
    assert ptp_tracker_jobs._post_data_common_trumpable == exp_post_data


def test__post_data_add_movie_format(ptp_tracker_jobs, mocker):
    mocker.patch.object(type(ptp_tracker_jobs), 'ptp_group_id', PropertyMock(return_value='123456'))
    assert ptp_tracker_jobs._post_data_add_movie_format == {
        'groupid': ptp_tracker_jobs.ptp_group_id,
    }


def test__post_data_add_new_movie(ptp_tracker_jobs, mock_job_attributes, mocker):
    mock_job_attributes(ptp_tracker_jobs)

    mocker.patch.object(type(ptp_tracker_jobs), 'imdb_id', PropertyMock(return_value='tt123456'))

    mocks = Mock()
    mocks.attach_mock(
        mocker.patch.object(ptp_tracker_jobs.tracker, 'normalize_imdb_id', side_effect=lambda id: f'<{id}>'),
        'normalize_imdb_id',
    )
    mocks.attach_mock(
        mocker.patch.object(ptp_tracker_jobs, 'get_job_output', side_effect=(
            '<title>',
            '<year>',
            '<plot>',
            '<tags>',
            '<poster>',
        )),
        'get_job_output',
    )

    exp_post_data = {
        'imdb': f'<{ptp_tracker_jobs.imdb_id}>',
        'title': '<title>',
        'year': '<year>',
        'album_desc': '<plot>',
        'tags': '<tags>',
        'image': '<poster>',
    }
    assert ptp_tracker_jobs._post_data_add_new_movie == exp_post_data
    assert mocks.mock_calls == [
        call.normalize_imdb_id(ptp_tracker_jobs.imdb_id),
        call.get_job_output(ptp_tracker_jobs.title_job, slice=0),
        call.get_job_output(ptp_tracker_jobs.year_job, slice=0),
        call.get_job_output(ptp_tracker_jobs.plot_job, slice=0),
        call.get_job_output(ptp_tracker_jobs.tags_job, slice=0),
        call.get_job_output(ptp_tracker_jobs.poster_job, slice=0),
    ]
