import re
from unittest.mock import Mock, call

import pytest

from upsies import errors
from upsies.jobs.mediainfo import MediainfoJob


@pytest.fixture
def job(tmp_path):
    return MediainfoJob(
        home_directory=tmp_path,
        cache_directory=tmp_path,
        content_path='path/to/content',
    )


@pytest.mark.parametrize(
    argnames='from_all_videos, exp_from_all_videos_id',
    argvalues=(
        (True, 'from_all_videos'),
        (False, 'from_first_video'),
    ),
)
@pytest.mark.parametrize(
    argnames='exclude_files, exp_exclude_files_id',
    argvalues=(
        ((), None),
        (('*.foo', 'bar*'), ['*.foo', 'bar*']),
        ((re.compile(r'.*\.foo$'), re.compile(r'^bar.*')), [r'.*\.foo$', '^bar.*']),
        (('*.foo', re.compile(r'^bar.*')), ['*.foo', '^bar.*']),
    ),
    ids=lambda v: repr(v),
)
@pytest.mark.parametrize(
    argnames='format, exp_format_id',
    argvalues=(
        (MediainfoJob._DEFAULT_FORMAT, None),
        ('[mediainfo]{MEDIAINFO}[/mediainfo]', 'format=[mediainfo]{MEDIAINFO}[/mediainfo]'),
        ('{mediainfo}{MEDIAINFO}{/mediainfo}', 'format={mediainfo}{MEDIAINFO}{/mediainfo}'),
    ),
    ids=lambda v: repr(v),
)
def test_cache_id(from_all_videos, exp_from_all_videos_id,
                  exclude_files, exp_exclude_files_id,
                  format, exp_format_id,
                  job, mocker):
    mocker.patch.object(job, '_content_path', 'path/to/Foo.2000-ASDF')
    mocker.patch.object(job, '_from_all_videos', from_all_videos)
    mocker.patch.object(job, '_exclude_files', exclude_files)
    mocker.patch.object(job, '_format', format)
    exp_cache_id = [
        'Foo.2000-ASDF',
        exp_from_all_videos_id,
    ]
    if exp_exclude_files_id is not None:
        exp_cache_id.append(exp_exclude_files_id)
    if exp_format_id is not None:
        exp_cache_id.append(exp_format_id)
    assert job.cache_id == exp_cache_id


def test_initialize():
    job = MediainfoJob(
        content_path='path/to/my/content',
        from_all_videos='maybe?',
        exclude_files=('foo', 'bar', 'baz'),
        format='my format',
    )
    assert job._content_path == 'path/to/my/content'
    assert job._from_all_videos == 'maybe?'
    assert job._exclude_files == ('foo', 'bar', 'baz')
    assert job._format == 'my format'
    assert job.signal.signals['mediainfo'] == [job._store_mediainfos_by_file]


@pytest.mark.parametrize(
    argnames='filtered_videos, from_all_videos, mediainfo_exceptions, exp_mock_calls',
    argvalues=(
        pytest.param(
            (),
            False,
            {},
            [
                call.error('No video files found'),
            ],
            id='No video files found',
        ),

        pytest.param(
            ('foo.mkv', 'bar.mkv', 'baz.mkv'),
            False,
            {
                'foo.mkv': None,
                'bar.mkv': None,
                'baz.mkv': None,
            },
            [
                call.mediainfo('foo.mkv'),
                call.send('<mediainfo for foo.mkv>'),
                call.emit('mediainfo', 'foo.mkv', '<mediainfo for foo.mkv>'),
            ],
            id='MKV / First / No exception',
        ),

        pytest.param(
            ('foo.mkv', 'bar.mkv', 'baz.mkv'),
            False,
            {
                'foo.mkv': None,
                'bar.mkv': errors.ContentError('no'),
                'baz.mkv': None,
            },
            [
                call.mediainfo('foo.mkv'),
                call.send('<mediainfo for foo.mkv>'),
                call.emit('mediainfo', 'foo.mkv', '<mediainfo for foo.mkv>'),
            ],
            id='MKV / First / ContentError is irrelevant',
        ),

        pytest.param(
            ('foo.mkv', 'bar.mkv', 'baz.mkv'),
            False,
            {
                'foo.mkv': errors.ContentError('no'),
                'bar.mkv': None,
                'baz.mkv': None,
            },
            [
                call.mediainfo('foo.mkv'),
                call.error(errors.ContentError('no')),
            ],
            id='MKV / First / ContentError is reported',
        ),

        pytest.param(
            ('foo.mkv', 'bar.mkv', 'baz.mkv'),
            False,
            {
                'foo.mkv': None,
                'bar.mkv': Exception('NO'),
                'baz.mkv': None,
            },
            [
                call.mediainfo('foo.mkv'),
                call.send('<mediainfo for foo.mkv>'),
                call.emit('mediainfo', 'foo.mkv', '<mediainfo for foo.mkv>'),
            ],
            id='MKV / First / Exception is irrelevant',
        ),

        pytest.param(
            ('foo.mkv', 'bar.mkv', 'baz.mkv'),
            False,
            {
                'foo.mkv': Exception('NO'),
                'bar.mkv': None,
                'baz.mkv': None,
            },
            [
                call.mediainfo('foo.mkv'),
                Exception('NO'),
            ],
            id='MKV / First / Exception is raised',
        ),

        pytest.param(
            ('foo.mkv', 'bar.mkv', 'baz.mkv'),
            True,
            {
                'foo.mkv': None,
                'bar.mkv': None,
                'baz.mkv': None,
            },
            [
                call.mediainfo('foo.mkv'),
                call.send('<mediainfo for foo.mkv>'),
                call.emit('mediainfo', 'foo.mkv', '<mediainfo for foo.mkv>'),
                call.mediainfo('bar.mkv'),
                call.send('<mediainfo for bar.mkv>'),
                call.emit('mediainfo', 'bar.mkv', '<mediainfo for bar.mkv>'),
                call.mediainfo('baz.mkv'),
                call.send('<mediainfo for baz.mkv>'),
                call.emit('mediainfo', 'baz.mkv', '<mediainfo for baz.mkv>'),
            ],
            id='MKV / All / No exception',
        ),

        pytest.param(
            ('foo.mkv', 'bar.mkv', 'baz.mkv'),
            True,
            {
                'foo.mkv': None,
                'bar.mkv': errors.ContentError('no'),
                'baz.mkv': None,
            },
            [
                call.mediainfo('foo.mkv'),
                call.send('<mediainfo for foo.mkv>'),
                call.emit('mediainfo', 'foo.mkv', '<mediainfo for foo.mkv>'),
                call.mediainfo('bar.mkv'),
                call.error(errors.ContentError('no')),
                call.mediainfo('baz.mkv'),
                call.send('<mediainfo for baz.mkv>'),
                call.emit('mediainfo', 'baz.mkv', '<mediainfo for baz.mkv>'),
            ],
            id='MKV / All / ContentError is reported',
        ),

        pytest.param(
            ('foo.mkv', 'bar.mkv', 'baz.mkv'),
            True,
            {
                'foo.mkv': None,
                'bar.mkv': Exception('NO'),
                'baz.mkv': None,
            },
            [
                call.mediainfo('foo.mkv'),
                call.send('<mediainfo for foo.mkv>'),
                call.emit('mediainfo', 'foo.mkv', '<mediainfo for foo.mkv>'),
                call.mediainfo('bar.mkv'),
                Exception('NO'),
            ],
            id='MKV / All / Exception is raised',
        ),

        pytest.param(
            ('foo/VIDEO_TS/VTS_01_2.VOB', 'bar/VIDEO_TS/VTS_03_4.VOB', 'baz/VIDEO_TS/VTS_05_6.VOB'),
            False,
            {
                '<IFO for foo/VIDEO_TS/VTS_01_2.VOB>': None,
                'foo/VIDEO_TS/VTS_01_2.VOB': None,
                '<IFO for bar/VIDEO_TS/VTS_03_4.VOB>': None,
                'bar/VIDEO_TS/VTS_03_4.VOB': None,
                '<IFO for baz/VIDEO_TS/VTS_05_6.VOB>': None,
                'baz/VIDEO_TS/VTS_05_6.VOB': None,
            },
            [
                call.vob2ifo('foo/VIDEO_TS/VTS_01_2.VOB'),
                call.mediainfo('<IFO for foo/VIDEO_TS/VTS_01_2.VOB>'),
                call.mediainfo('foo/VIDEO_TS/VTS_01_2.VOB'),
                call.send('<mediainfo for <IFO for foo/VIDEO_TS/VTS_01_2.VOB>>'),
                call.emit('mediainfo', '<IFO for foo/VIDEO_TS/VTS_01_2.VOB>', '<mediainfo for <IFO for foo/VIDEO_TS/VTS_01_2.VOB>>'),
                call.send('<mediainfo for foo/VIDEO_TS/VTS_01_2.VOB>'),
                call.emit('mediainfo', 'foo/VIDEO_TS/VTS_01_2.VOB', '<mediainfo for foo/VIDEO_TS/VTS_01_2.VOB>'),
            ],
            id='DVD / First / No exception',
        ),

        pytest.param(
            ('foo/VIDEO_TS/VTS_01_2.VOB', 'bar/VIDEO_TS/VTS_03_4.VOB', 'baz/VIDEO_TS/VTS_05_6.VOB'),
            False,
            {
                '<IFO for foo/VIDEO_TS/VTS_01_2.VOB>': None,
                'foo/VIDEO_TS/VTS_01_2.VOB': None,
                '<IFO for bar/VIDEO_TS/VTS_03_4.VOB>': errors.ContentError('no'),
                'bar/VIDEO_TS/VTS_03_4.VOB': None,
                '<IFO for baz/VIDEO_TS/VTS_05_6.VOB>': None,
                'baz/VIDEO_TS/VTS_05_6.VOB': None,
            },
            [
                call.vob2ifo('foo/VIDEO_TS/VTS_01_2.VOB'),
                call.mediainfo('<IFO for foo/VIDEO_TS/VTS_01_2.VOB>'),
                call.mediainfo('foo/VIDEO_TS/VTS_01_2.VOB'),
                call.send('<mediainfo for <IFO for foo/VIDEO_TS/VTS_01_2.VOB>>'),
                call.emit('mediainfo', '<IFO for foo/VIDEO_TS/VTS_01_2.VOB>', '<mediainfo for <IFO for foo/VIDEO_TS/VTS_01_2.VOB>>'),
                call.send('<mediainfo for foo/VIDEO_TS/VTS_01_2.VOB>'),
                call.emit('mediainfo', 'foo/VIDEO_TS/VTS_01_2.VOB', '<mediainfo for foo/VIDEO_TS/VTS_01_2.VOB>'),
            ],
            id='DVD / First / ContentError is irrelevant for IFO',
        ),

        pytest.param(
            ('foo/VIDEO_TS/VTS_01_2.VOB', 'bar/VIDEO_TS/VTS_03_4.VOB', 'baz/VIDEO_TS/VTS_05_6.VOB'),
            False,
            {
                '<IFO for foo/VIDEO_TS/VTS_01_2.VOB>': None,
                'foo/VIDEO_TS/VTS_01_2.VOB': None,
                '<IFO for bar/VIDEO_TS/VTS_03_4.VOB>': None,
                'bar/VIDEO_TS/VTS_03_4.VOB': errors.ContentError('no'),
                '<IFO for baz/VIDEO_TS/VTS_05_6.VOB>': None,
                'baz/VIDEO_TS/VTS_05_6.VOB': None,
            },
            [
                call.vob2ifo('foo/VIDEO_TS/VTS_01_2.VOB'),
                call.mediainfo('<IFO for foo/VIDEO_TS/VTS_01_2.VOB>'),
                call.mediainfo('foo/VIDEO_TS/VTS_01_2.VOB'),
                call.send('<mediainfo for <IFO for foo/VIDEO_TS/VTS_01_2.VOB>>'),
                call.emit('mediainfo', '<IFO for foo/VIDEO_TS/VTS_01_2.VOB>', '<mediainfo for <IFO for foo/VIDEO_TS/VTS_01_2.VOB>>'),
                call.send('<mediainfo for foo/VIDEO_TS/VTS_01_2.VOB>'),
                call.emit('mediainfo', 'foo/VIDEO_TS/VTS_01_2.VOB', '<mediainfo for foo/VIDEO_TS/VTS_01_2.VOB>'),
            ],
            id='DVD / First / ContentError is irrelevant for VOB',
        ),

        pytest.param(
            ('foo/VIDEO_TS/VTS_01_2.VOB', 'bar/VIDEO_TS/VTS_03_4.VOB', 'baz/VIDEO_TS/VTS_05_6.VOB'),
            False,
            {
                '<IFO for foo/VIDEO_TS/VTS_01_2.VOB>': errors.ContentError('no'),
                'foo/VIDEO_TS/VTS_01_2.VOB': None,
                '<IFO for bar/VIDEO_TS/VTS_03_4.VOB>': None,
                'bar/VIDEO_TS/VTS_03_4.VOB': None,
                '<IFO for baz/VIDEO_TS/VTS_05_6.VOB>': None,
                'baz/VIDEO_TS/VTS_05_6.VOB': None,
            },
            [
                call.vob2ifo('foo/VIDEO_TS/VTS_01_2.VOB'),
                call.mediainfo('<IFO for foo/VIDEO_TS/VTS_01_2.VOB>'),
                call.mediainfo('foo/VIDEO_TS/VTS_01_2.VOB'),
                call.error(errors.ContentError('no')),
                call.send('<mediainfo for foo/VIDEO_TS/VTS_01_2.VOB>'),
                call.emit('mediainfo', 'foo/VIDEO_TS/VTS_01_2.VOB', '<mediainfo for foo/VIDEO_TS/VTS_01_2.VOB>'),
            ],
            id='DVD / First / ContentError is reported for IFO',
        ),

        pytest.param(
            ('foo/VIDEO_TS/VTS_01_2.VOB', 'bar/VIDEO_TS/VTS_03_4.VOB', 'baz/VIDEO_TS/VTS_05_6.VOB'),
            False,
            {
                '<IFO for foo/VIDEO_TS/VTS_01_2.VOB>': None,
                'foo/VIDEO_TS/VTS_01_2.VOB': errors.ContentError('no'),
                '<IFO for bar/VIDEO_TS/VTS_03_4.VOB>': None,
                'bar/VIDEO_TS/VTS_03_4.VOB': None,
                '<IFO for baz/VIDEO_TS/VTS_05_6.VOB>': None,
                'baz/VIDEO_TS/VTS_05_6.VOB': None,
            },
            [
                call.vob2ifo('foo/VIDEO_TS/VTS_01_2.VOB'),
                call.mediainfo('<IFO for foo/VIDEO_TS/VTS_01_2.VOB>'),
                call.mediainfo('foo/VIDEO_TS/VTS_01_2.VOB'),
                call.send('<mediainfo for <IFO for foo/VIDEO_TS/VTS_01_2.VOB>>'),
                call.emit('mediainfo', '<IFO for foo/VIDEO_TS/VTS_01_2.VOB>', '<mediainfo for <IFO for foo/VIDEO_TS/VTS_01_2.VOB>>'),
                call.error(errors.ContentError('no')),
            ],
            id='DVD / First / ContentError is reported for VOB',
        ),

        pytest.param(
            ('foo/VIDEO_TS/VTS_01_2.VOB', 'bar/VIDEO_TS/VTS_03_4.VOB', 'baz/VIDEO_TS/VTS_05_6.VOB'),
            False,
            {
                '<IFO for foo/VIDEO_TS/VTS_01_2.VOB>': None,
                'foo/VIDEO_TS/VTS_01_2.VOB': None,
                '<IFO for bar/VIDEO_TS/VTS_03_4.VOB>': Exception('NO'),
                'bar/VIDEO_TS/VTS_03_4.VOB': None,
                '<IFO for baz/VIDEO_TS/VTS_05_6.VOB>': None,
                'baz/VIDEO_TS/VTS_05_6.VOB': None,
            },
            [
                call.vob2ifo('foo/VIDEO_TS/VTS_01_2.VOB'),
                call.mediainfo('<IFO for foo/VIDEO_TS/VTS_01_2.VOB>'),
                call.mediainfo('foo/VIDEO_TS/VTS_01_2.VOB'),
                call.send('<mediainfo for <IFO for foo/VIDEO_TS/VTS_01_2.VOB>>'),
                call.emit('mediainfo', '<IFO for foo/VIDEO_TS/VTS_01_2.VOB>', '<mediainfo for <IFO for foo/VIDEO_TS/VTS_01_2.VOB>>'),
                call.send('<mediainfo for foo/VIDEO_TS/VTS_01_2.VOB>'),
                call.emit('mediainfo', 'foo/VIDEO_TS/VTS_01_2.VOB', '<mediainfo for foo/VIDEO_TS/VTS_01_2.VOB>'),
            ],
            id='DVD / First / Exception is irrelevant for IFO',
        ),

        pytest.param(
            ('foo/VIDEO_TS/VTS_01_2.VOB', 'bar/VIDEO_TS/VTS_03_4.VOB', 'baz/VIDEO_TS/VTS_05_6.VOB'),
            False,
            {
                '<IFO for foo/VIDEO_TS/VTS_01_2.VOB>': None,
                'foo/VIDEO_TS/VTS_01_2.VOB': None,
                '<IFO for bar/VIDEO_TS/VTS_03_4.VOB>': None,
                'bar/VIDEO_TS/VTS_03_4.VOB': Exception('NO'),
                '<IFO for baz/VIDEO_TS/VTS_05_6.VOB>': None,
                'baz/VIDEO_TS/VTS_05_6.VOB': None,
            },
            [
                call.vob2ifo('foo/VIDEO_TS/VTS_01_2.VOB'),
                call.mediainfo('<IFO for foo/VIDEO_TS/VTS_01_2.VOB>'),
                call.mediainfo('foo/VIDEO_TS/VTS_01_2.VOB'),
                call.send('<mediainfo for <IFO for foo/VIDEO_TS/VTS_01_2.VOB>>'),
                call.emit('mediainfo', '<IFO for foo/VIDEO_TS/VTS_01_2.VOB>', '<mediainfo for <IFO for foo/VIDEO_TS/VTS_01_2.VOB>>'),
                call.send('<mediainfo for foo/VIDEO_TS/VTS_01_2.VOB>'),
                call.emit('mediainfo', 'foo/VIDEO_TS/VTS_01_2.VOB', '<mediainfo for foo/VIDEO_TS/VTS_01_2.VOB>'),
            ],
            id='DVD / First / Exception is irrelevant for VOB',
        ),

        pytest.param(
            ('foo/VIDEO_TS/VTS_01_2.VOB', 'bar/VIDEO_TS/VTS_03_4.VOB', 'baz/VIDEO_TS/VTS_05_6.VOB'),
            False,
            {
                '<IFO for foo/VIDEO_TS/VTS_01_2.VOB>': Exception('NO'),
                'foo/VIDEO_TS/VTS_01_2.VOB': None,
                '<IFO for bar/VIDEO_TS/VTS_03_4.VOB>': None,
                'bar/VIDEO_TS/VTS_03_4.VOB': None,
                '<IFO for baz/VIDEO_TS/VTS_05_6.VOB>': None,
                'baz/VIDEO_TS/VTS_05_6.VOB': None,
            },
            [
                call.vob2ifo('foo/VIDEO_TS/VTS_01_2.VOB'),
                call.mediainfo('<IFO for foo/VIDEO_TS/VTS_01_2.VOB>'),
                call.mediainfo('foo/VIDEO_TS/VTS_01_2.VOB'),
                Exception('NO'),
            ],
            id='DVD / First / Exception is raised for IFO',
        ),

        pytest.param(
            ('foo/VIDEO_TS/VTS_01_2.VOB', 'bar/VIDEO_TS/VTS_03_4.VOB', 'baz/VIDEO_TS/VTS_05_6.VOB'),
            False,
            {
                '<IFO for foo/VIDEO_TS/VTS_01_2.VOB>': None,
                'foo/VIDEO_TS/VTS_01_2.VOB': Exception('NO'),
                '<IFO for bar/VIDEO_TS/VTS_03_4.VOB>': None,
                'bar/VIDEO_TS/VTS_03_4.VOB': None,
                '<IFO for baz/VIDEO_TS/VTS_05_6.VOB>': None,
                'baz/VIDEO_TS/VTS_05_6.VOB': None,
            },
            [
                call.vob2ifo('foo/VIDEO_TS/VTS_01_2.VOB'),
                call.mediainfo('<IFO for foo/VIDEO_TS/VTS_01_2.VOB>'),
                call.mediainfo('foo/VIDEO_TS/VTS_01_2.VOB'),
                call.send('<mediainfo for <IFO for foo/VIDEO_TS/VTS_01_2.VOB>>'),
                call.emit('mediainfo', '<IFO for foo/VIDEO_TS/VTS_01_2.VOB>', '<mediainfo for <IFO for foo/VIDEO_TS/VTS_01_2.VOB>>'),
                Exception('NO'),
            ],
            id='DVD / First / Exception is raised for VOB',
        ),

        pytest.param(
            ('foo/VIDEO_TS/VTS_01_2.VOB', 'bar/VIDEO_TS/VTS_03_4.VOB', 'baz/VIDEO_TS/VTS_05_6.VOB'),
            True,
            {
                '<IFO for foo/VIDEO_TS/VTS_01_2.VOB>': None,
                'foo/VIDEO_TS/VTS_01_2.VOB': None,
                '<IFO for bar/VIDEO_TS/VTS_03_4.VOB>': None,
                'bar/VIDEO_TS/VTS_03_4.VOB': None,
                '<IFO for baz/VIDEO_TS/VTS_05_6.VOB>': None,
                'baz/VIDEO_TS/VTS_05_6.VOB': None,
            },
            [
                call.vob2ifo('foo/VIDEO_TS/VTS_01_2.VOB'),
                call.mediainfo('<IFO for foo/VIDEO_TS/VTS_01_2.VOB>'),
                call.mediainfo('foo/VIDEO_TS/VTS_01_2.VOB'),
                call.send('<mediainfo for <IFO for foo/VIDEO_TS/VTS_01_2.VOB>>'),
                call.emit('mediainfo', '<IFO for foo/VIDEO_TS/VTS_01_2.VOB>', '<mediainfo for <IFO for foo/VIDEO_TS/VTS_01_2.VOB>>'),
                call.send('<mediainfo for foo/VIDEO_TS/VTS_01_2.VOB>'),
                call.emit('mediainfo', 'foo/VIDEO_TS/VTS_01_2.VOB', '<mediainfo for foo/VIDEO_TS/VTS_01_2.VOB>'),

                call.vob2ifo('bar/VIDEO_TS/VTS_03_4.VOB'),
                call.mediainfo('<IFO for bar/VIDEO_TS/VTS_03_4.VOB>'),
                call.mediainfo('bar/VIDEO_TS/VTS_03_4.VOB'),
                call.send('<mediainfo for <IFO for bar/VIDEO_TS/VTS_03_4.VOB>>'),
                call.emit('mediainfo', '<IFO for bar/VIDEO_TS/VTS_03_4.VOB>', '<mediainfo for <IFO for bar/VIDEO_TS/VTS_03_4.VOB>>'),
                call.send('<mediainfo for bar/VIDEO_TS/VTS_03_4.VOB>'),
                call.emit('mediainfo', 'bar/VIDEO_TS/VTS_03_4.VOB', '<mediainfo for bar/VIDEO_TS/VTS_03_4.VOB>'),

                call.vob2ifo('baz/VIDEO_TS/VTS_05_6.VOB'),
                call.mediainfo('<IFO for baz/VIDEO_TS/VTS_05_6.VOB>'),
                call.mediainfo('baz/VIDEO_TS/VTS_05_6.VOB'),
                call.send('<mediainfo for <IFO for baz/VIDEO_TS/VTS_05_6.VOB>>'),
                call.emit('mediainfo', '<IFO for baz/VIDEO_TS/VTS_05_6.VOB>', '<mediainfo for <IFO for baz/VIDEO_TS/VTS_05_6.VOB>>'),
                call.send('<mediainfo for baz/VIDEO_TS/VTS_05_6.VOB>'),
                call.emit('mediainfo', 'baz/VIDEO_TS/VTS_05_6.VOB', '<mediainfo for baz/VIDEO_TS/VTS_05_6.VOB>'),
            ],
            id='DVD / All / No exception',
        ),

        pytest.param(
            ('foo/VIDEO_TS/VTS_01_2.VOB', 'bar/VIDEO_TS/VTS_03_4.VOB', 'baz/VIDEO_TS/VTS_05_6.VOB'),
            True,
            {
                '<IFO for foo/VIDEO_TS/VTS_01_2.VOB>': None,
                'foo/VIDEO_TS/VTS_01_2.VOB': None,
                '<IFO for bar/VIDEO_TS/VTS_03_4.VOB>': errors.ContentError('no'),
                'bar/VIDEO_TS/VTS_03_4.VOB': None,
                '<IFO for baz/VIDEO_TS/VTS_05_6.VOB>': None,
                'baz/VIDEO_TS/VTS_05_6.VOB': None,
            },
            [
                call.vob2ifo('foo/VIDEO_TS/VTS_01_2.VOB'),
                call.mediainfo('<IFO for foo/VIDEO_TS/VTS_01_2.VOB>'),
                call.mediainfo('foo/VIDEO_TS/VTS_01_2.VOB'),
                call.send('<mediainfo for <IFO for foo/VIDEO_TS/VTS_01_2.VOB>>'),
                call.emit('mediainfo', '<IFO for foo/VIDEO_TS/VTS_01_2.VOB>', '<mediainfo for <IFO for foo/VIDEO_TS/VTS_01_2.VOB>>'),
                call.send('<mediainfo for foo/VIDEO_TS/VTS_01_2.VOB>'),
                call.emit('mediainfo', 'foo/VIDEO_TS/VTS_01_2.VOB', '<mediainfo for foo/VIDEO_TS/VTS_01_2.VOB>'),

                call.vob2ifo('bar/VIDEO_TS/VTS_03_4.VOB'),
                call.mediainfo('<IFO for bar/VIDEO_TS/VTS_03_4.VOB>'),
                call.mediainfo('bar/VIDEO_TS/VTS_03_4.VOB'),
                call.error(errors.ContentError('no')),
                call.send('<mediainfo for bar/VIDEO_TS/VTS_03_4.VOB>'),
                call.emit('mediainfo', 'bar/VIDEO_TS/VTS_03_4.VOB', '<mediainfo for bar/VIDEO_TS/VTS_03_4.VOB>'),

                call.vob2ifo('baz/VIDEO_TS/VTS_05_6.VOB'),
                call.mediainfo('<IFO for baz/VIDEO_TS/VTS_05_6.VOB>'),
                call.mediainfo('baz/VIDEO_TS/VTS_05_6.VOB'),
                call.send('<mediainfo for <IFO for baz/VIDEO_TS/VTS_05_6.VOB>>'),
                call.emit('mediainfo', '<IFO for baz/VIDEO_TS/VTS_05_6.VOB>', '<mediainfo for <IFO for baz/VIDEO_TS/VTS_05_6.VOB>>'),
                call.send('<mediainfo for baz/VIDEO_TS/VTS_05_6.VOB>'),
                call.emit('mediainfo', 'baz/VIDEO_TS/VTS_05_6.VOB', '<mediainfo for baz/VIDEO_TS/VTS_05_6.VOB>'),
            ],
            id='DVD / All / ContentError is reported for IFO',
        ),

        pytest.param(
            ('foo/VIDEO_TS/VTS_01_2.VOB', 'bar/VIDEO_TS/VTS_03_4.VOB', 'baz/VIDEO_TS/VTS_05_6.VOB'),
            True,
            {
                '<IFO for foo/VIDEO_TS/VTS_01_2.VOB>': None,
                'foo/VIDEO_TS/VTS_01_2.VOB': None,
                '<IFO for bar/VIDEO_TS/VTS_03_4.VOB>': None,
                'bar/VIDEO_TS/VTS_03_4.VOB': errors.ContentError('no'),
                '<IFO for baz/VIDEO_TS/VTS_05_6.VOB>': None,
                'baz/VIDEO_TS/VTS_05_6.VOB': None,
            },
            [
                call.vob2ifo('foo/VIDEO_TS/VTS_01_2.VOB'),
                call.mediainfo('<IFO for foo/VIDEO_TS/VTS_01_2.VOB>'),
                call.mediainfo('foo/VIDEO_TS/VTS_01_2.VOB'),
                call.send('<mediainfo for <IFO for foo/VIDEO_TS/VTS_01_2.VOB>>'),
                call.emit('mediainfo', '<IFO for foo/VIDEO_TS/VTS_01_2.VOB>', '<mediainfo for <IFO for foo/VIDEO_TS/VTS_01_2.VOB>>'),
                call.send('<mediainfo for foo/VIDEO_TS/VTS_01_2.VOB>'),
                call.emit('mediainfo', 'foo/VIDEO_TS/VTS_01_2.VOB', '<mediainfo for foo/VIDEO_TS/VTS_01_2.VOB>'),

                call.vob2ifo('bar/VIDEO_TS/VTS_03_4.VOB'),
                call.mediainfo('<IFO for bar/VIDEO_TS/VTS_03_4.VOB>'),
                call.mediainfo('bar/VIDEO_TS/VTS_03_4.VOB'),
                call.send('<mediainfo for <IFO for bar/VIDEO_TS/VTS_03_4.VOB>>'),
                call.emit('mediainfo', '<IFO for bar/VIDEO_TS/VTS_03_4.VOB>', '<mediainfo for <IFO for bar/VIDEO_TS/VTS_03_4.VOB>>'),
                call.error(errors.ContentError('no')),

                call.vob2ifo('baz/VIDEO_TS/VTS_05_6.VOB'),
                call.mediainfo('<IFO for baz/VIDEO_TS/VTS_05_6.VOB>'),
                call.mediainfo('baz/VIDEO_TS/VTS_05_6.VOB'),
                call.send('<mediainfo for <IFO for baz/VIDEO_TS/VTS_05_6.VOB>>'),
                call.emit('mediainfo', '<IFO for baz/VIDEO_TS/VTS_05_6.VOB>', '<mediainfo for <IFO for baz/VIDEO_TS/VTS_05_6.VOB>>'),
                call.send('<mediainfo for baz/VIDEO_TS/VTS_05_6.VOB>'),
                call.emit('mediainfo', 'baz/VIDEO_TS/VTS_05_6.VOB', '<mediainfo for baz/VIDEO_TS/VTS_05_6.VOB>'),
            ],
            id='DVD / All / ContentError is reported for VOB',
        ),

        pytest.param(
            ('foo/VIDEO_TS/VTS_01_2.VOB', 'bar/VIDEO_TS/VTS_03_4.VOB', 'baz/VIDEO_TS/VTS_05_6.VOB'),
            True,
            {
                '<IFO for foo/VIDEO_TS/VTS_01_2.VOB>': None,
                'foo/VIDEO_TS/VTS_01_2.VOB': None,
                '<IFO for bar/VIDEO_TS/VTS_03_4.VOB>': Exception('NO'),
                'bar/VIDEO_TS/VTS_03_4.VOB': None,
                '<IFO for baz/VIDEO_TS/VTS_05_6.VOB>': None,
                'baz/VIDEO_TS/VTS_05_6.VOB': None,
            },
            [
                call.vob2ifo('foo/VIDEO_TS/VTS_01_2.VOB'),
                call.mediainfo('<IFO for foo/VIDEO_TS/VTS_01_2.VOB>'),
                call.mediainfo('foo/VIDEO_TS/VTS_01_2.VOB'),
                call.send('<mediainfo for <IFO for foo/VIDEO_TS/VTS_01_2.VOB>>'),
                call.emit('mediainfo', '<IFO for foo/VIDEO_TS/VTS_01_2.VOB>', '<mediainfo for <IFO for foo/VIDEO_TS/VTS_01_2.VOB>>'),
                call.send('<mediainfo for foo/VIDEO_TS/VTS_01_2.VOB>'),
                call.emit('mediainfo', 'foo/VIDEO_TS/VTS_01_2.VOB', '<mediainfo for foo/VIDEO_TS/VTS_01_2.VOB>'),

                call.vob2ifo('bar/VIDEO_TS/VTS_03_4.VOB'),
                call.mediainfo('<IFO for bar/VIDEO_TS/VTS_03_4.VOB>'),
                call.mediainfo('bar/VIDEO_TS/VTS_03_4.VOB'),
                Exception('NO'),
            ],
            id='DVD / All / Exception is raised for IFO',
        ),

        pytest.param(
            ('foo/VIDEO_TS/VTS_01_2.VOB', 'bar/VIDEO_TS/VTS_03_4.VOB', 'baz/VIDEO_TS/VTS_05_6.VOB'),
            True,
            {
                '<IFO for foo/VIDEO_TS/VTS_01_2.VOB>': None,
                'foo/VIDEO_TS/VTS_01_2.VOB': None,
                '<IFO for bar/VIDEO_TS/VTS_03_4.VOB>': None,
                'bar/VIDEO_TS/VTS_03_4.VOB': Exception('NO'),
                '<IFO for baz/VIDEO_TS/VTS_05_6.VOB>': None,
                'baz/VIDEO_TS/VTS_05_6.VOB': None,
            },
            [
                call.vob2ifo('foo/VIDEO_TS/VTS_01_2.VOB'),
                call.mediainfo('<IFO for foo/VIDEO_TS/VTS_01_2.VOB>'),
                call.mediainfo('foo/VIDEO_TS/VTS_01_2.VOB'),
                call.send('<mediainfo for <IFO for foo/VIDEO_TS/VTS_01_2.VOB>>'),
                call.emit('mediainfo', '<IFO for foo/VIDEO_TS/VTS_01_2.VOB>', '<mediainfo for <IFO for foo/VIDEO_TS/VTS_01_2.VOB>>'),
                call.send('<mediainfo for foo/VIDEO_TS/VTS_01_2.VOB>'),
                call.emit('mediainfo', 'foo/VIDEO_TS/VTS_01_2.VOB', '<mediainfo for foo/VIDEO_TS/VTS_01_2.VOB>'),

                call.vob2ifo('bar/VIDEO_TS/VTS_03_4.VOB'),
                call.mediainfo('<IFO for bar/VIDEO_TS/VTS_03_4.VOB>'),
                call.mediainfo('bar/VIDEO_TS/VTS_03_4.VOB'),
                call.send('<mediainfo for <IFO for bar/VIDEO_TS/VTS_03_4.VOB>>'),
                call.emit('mediainfo', '<IFO for bar/VIDEO_TS/VTS_03_4.VOB>', '<mediainfo for <IFO for bar/VIDEO_TS/VTS_03_4.VOB>>'),
                Exception('NO'),
            ],
            id='DVD / All / Exception is raised for VOB',
        ),
    ),
    ids=lambda v: repr(v),
)
@pytest.mark.asyncio
async def test_run(filtered_videos, from_all_videos, mediainfo_exceptions, exp_mock_calls,
                   job, mocker):
    job._from_all_videos = from_all_videos
    mocks = Mock()
    mocks.attach_mock(
        mocker.patch('upsies.utils.torrent.filter_files'),
        'filter_files',
    )
    mocks.attach_mock(
        mocker.patch('upsies.utils.video.filter_main_videos', return_value=filtered_videos),
        'filter_main_videos',
    )

    def mediainfo_side_effect(filepath):
        exception = mediainfo_exceptions.get(filepath, None)
        print('side_effect for', filepath, 'is', repr(exception))
        if exception:
            raise exception
        else:
            return f'<mediainfo for {filepath}>'

    mocks.attach_mock(
        mocker.patch('upsies.utils.video.mediainfo', side_effect=mediainfo_side_effect),
        'mediainfo',
    )
    mocks.attach_mock(
        mocker.patch('upsies.utils.video.vob2ifo', side_effect=lambda f: f'<IFO for {f}>'),
        'vob2ifo',
    )
    mocks.attach_mock(mocker.patch.object(job, 'send'), 'send')
    mocks.attach_mock(mocker.patch.object(job, 'error'), 'error')
    mocks.attach_mock(mocker.patch.object(job.signal, 'emit'), 'emit')

    exp_exceptions = [x for x in exp_mock_calls if isinstance(x, Exception)]
    exp_mock_calls = [x for x in exp_mock_calls if not isinstance(x, Exception)]

    if exp_exceptions:
        exp_exception = exp_exceptions[0]
        with pytest.raises(type(exp_exception), match=rf'^{re.escape(str(exp_exception))}$'):
            await job.run()
    else:
        await job.run()

    assert mocks.mock_calls == [
        call.filter_files(
            content_path=job._content_path,
            exclude=job._exclude_files,
        ),
        call.filter_main_videos(mocks.filter_files.return_value),

    ] + exp_mock_calls


@pytest.mark.parametrize(
    argnames='mediainfo, format, exp_mediainfo',
    argvalues=(
        (
            'mock mediainfo',
            '{MEDIAINFO}',
            'mock mediainfo',
        ),
        (
            'mock mediainfo',
            '{{MEDIAINFO}}',
            '{mock mediainfo}',
        ),
        (
            'mock mediainfo',
            'foo',
            'foo',
        ),
    ),
)
def test_send(mediainfo, format, exp_mediainfo, job, mocker):
    parent_send = mocker.patch('upsies.jobs.base.JobBase.send')
    mocker.patch.object(job, '_format', format)
    job.send(mediainfo)
    assert parent_send.call_args_list == [call(exp_mediainfo)]


def test_store_mediainfos_by_file(job):
    assert job._mediainfos_by_file == {}

    job._store_mediainfos_by_file('foo.mkv', 'mediainfo for foo.mkv')
    assert job._mediainfos_by_file == {
        'foo.mkv': 'mediainfo for foo.mkv',
    }

    job._store_mediainfos_by_file('bar.mkv', 'mediainfo for bar.mkv')
    assert job._mediainfos_by_file == {
        'foo.mkv': 'mediainfo for foo.mkv',
        'bar.mkv': 'mediainfo for bar.mkv',
    }

    job._store_mediainfos_by_file('dvd/VIDEO_TS/VTS_01_0.IFO', 'mediainfo for VTS_01_0.IFO')
    assert job._mediainfos_by_file == {
        'foo.mkv': 'mediainfo for foo.mkv',
        'bar.mkv': 'mediainfo for bar.mkv',
        'dvd/VIDEO_TS/VTS_01_0.IFO': 'mediainfo for VTS_01_0.IFO',
    }
    job._store_mediainfos_by_file('dvd/VIDEO_TS/VTS_01_1.VOB', 'mediainfo for VTS_01_1.VOB')
    assert job._mediainfos_by_file == {
        'foo.mkv': 'mediainfo for foo.mkv',
        'bar.mkv': 'mediainfo for bar.mkv',
        'dvd/VIDEO_TS/VTS_01_0.IFO': 'mediainfo for VTS_01_0.IFO',
        'dvd/VIDEO_TS/VTS_01_1.VOB': 'mediainfo for VTS_01_1.VOB',
    }


def test_mediainfos_by_file(job):
    job._mediainfos_by_file = {
        'path/to/foo.mkv': 'mediainfo for foo.mkv',
    }

    mediainfos_by_file = job.mediainfos_by_file
    assert mediainfos_by_file == {
        'path/to/foo.mkv': 'mediainfo for foo.mkv',
    }

    mediainfos_by_file['path/to/foo.mkv'] = 'not a mediainfo'
    assert job.mediainfos_by_file == {
        'path/to/foo.mkv': 'mediainfo for foo.mkv',
    }

    mediainfos_by_file['path/to/bar.mkv'] = 'mediainfo for bar.mkv'
    assert job.mediainfos_by_file == {
        'path/to/foo.mkv': 'mediainfo for foo.mkv',
    }

    del mediainfos_by_file['path/to/foo.mkv']
    assert job.mediainfos_by_file == {
        'path/to/foo.mkv': 'mediainfo for foo.mkv',
    }
