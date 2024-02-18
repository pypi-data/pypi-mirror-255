import re
from unittest.mock import Mock, call

import pytest

from upsies.utils import subtitle


@pytest.mark.parametrize('forced, exp_forced', (
    (True, True),
    (False, False),
    ('', False),
    (1, True),
))
@pytest.mark.parametrize('format, exp_format', (
    ('SRT', 'SRT'),
    ('', ''),
    (None, ''),
))
@pytest.mark.parametrize(
    argnames='language, exp_language, exp_region, exp_code',
    argvalues=(
        ('foo-mx-Latn', '', '', ''),

        ('pt', 'pt', '', 'pt'),
        ('PT', 'pt', '', 'pt'),
        ('por', 'pt', '', 'pt'),

        ('Pt-bR', 'pt', 'BR', 'pt-BR'),
        ('spa-419', 'es', '419', 'es-419'),
        ('zh-HANS', 'zh', '', 'zh'),
        ('gsw-u-sd-chzh', 'gsw', '', 'gsw'),
    ),
)
def test_Subtitle(
        language, exp_language, exp_region, exp_code,
        format, exp_format,
        forced, exp_forced,
):
    sub = subtitle.Subtitle(language=language, forced=forced, format=format)
    assert sub.language == exp_language
    assert sub.region == exp_region
    assert sub.forced == exp_forced
    assert sub.format == exp_format

    assert repr(sub) == (
        'Subtitle('
        + f'language={exp_code!r}'
        + f', forced={exp_forced!r}'
        + f', format={exp_format!r}'
        + ')'
    )


@pytest.mark.parametrize(
    argnames='a, b, exp_equal',
    argvalues=(
        (
            subtitle.Subtitle(language='foo', forced=False, format=None),
            subtitle.Subtitle(language='FOO', forced=False, format=None),
            True,
        ),
        (
            subtitle.Subtitle(language='foo', forced=False, format=None),
            subtitle.Subtitle(language='bar', forced=False, format=None),
            False,
        ),
        (
            subtitle.Subtitle(language='foo', forced=False, format=None),
            subtitle.Subtitle(language='foo', forced=0, format=None),
            True,
        ),
        (
            subtitle.Subtitle(language='foo', forced=False, format=None),
            subtitle.Subtitle(language='foo', forced=1, format=None),
            False,
        ),
        (
            subtitle.Subtitle(language='foo', forced=False, format=None),
            subtitle.Subtitle(language='foo', forced=False, format=''),
            True,
        ),
        (
            subtitle.Subtitle(language='foo', forced=False, format='FMT'),
            subtitle.Subtitle(language='foo', forced=False, format='FMT2'),
            False,
        ),
    ),
)
def test_Subtitle___eq__(a, b, exp_equal):
    equal = a == b
    assert equal is exp_equal


def test_get_subtitles(mocker):
    mocks = Mock()
    for funcname in dir(subtitle):
        if funcname.startswith('get_subtitles_from_'):
            mocks.attach_mock(
                mocker.patch(f'upsies.utils.subtitle.{funcname}', return_value={funcname, 'return', 'values'}),
                funcname,
            )

    content_path = 'path/to/content'
    subtitles = subtitle.get_subtitles(content_path)
    assert subtitles == {
        'get_subtitles_from_mediainfo',
        'get_subtitles_from_text_files',
        'get_subtitles_from_idx_files',
        'get_subtitles_from_dvd_tree',
        'return', 'values',
    }

    assert mocks.mock_calls == [
        call.get_subtitles_from_mediainfo(content_path),
        call.get_subtitles_from_text_files(content_path),
        call.get_subtitles_from_idx_files(content_path),
        call.get_subtitles_from_dvd_tree(content_path),
    ]


@pytest.mark.parametrize(
    argnames='all_tracks, exp_subtitles',
    argvalues=(
        pytest.param({}, set(), id='No tracks'),
        pytest.param({'Text': []}, set(), id='No subtitle tracks'),
        pytest.param(
            {'Text': [
                {},
                {'Forced': 'No'},
                {'Forced': 'Yes'},
                {'CodecID': 'S_HDMV/PGS'},
                {'CodecID': 'S_TEXT/UTF8'},
                {'Language': 'eng'},
                {'Language': 'zh-HANS'},
                {'Language': 'invalid language code', 'CodecID': 'S_TEXT/VTT'},
            ]},
            {
                subtitle.Subtitle(language='', forced=False, format=''),
                subtitle.Subtitle(language='', forced=False, format=''),
                subtitle.Subtitle(language='', forced=True, format=''),
                subtitle.Subtitle(language='', forced=False, format='PGS'),
                subtitle.Subtitle(language='', forced=False, format='SRT'),
                subtitle.Subtitle(language='en', forced=False, format=''),
                subtitle.Subtitle(language='zh-Hans', forced=False, format=''),
                subtitle.Subtitle(language='', forced=False, format=''),
            },
            id='Various subtitle tracks',
        ),
    ),
    ids=lambda v: repr(v),
)
def test_get_subtitles_from_mediainfo(all_tracks, exp_subtitles, mocker):
    tracks_mock = mocker.patch('upsies.utils.video.tracks', return_value=all_tracks)

    content_path = 'path/to/content'
    subtitles = subtitle.get_subtitles_from_mediainfo(content_path)
    assert subtitles == exp_subtitles

    assert tracks_mock.call_args_list == [call(content_path)]


@pytest.mark.parametrize(
    argnames='file_list, exp_subtitles',
    argvalues=(
        pytest.param(
            [],
            set(),
            id='No files found',
        ),
        pytest.param(
            ['path/to/foo.srt', 'path/to/foo.ssa', 'path/to/foo.ass', 'path/to/foo.vtt', 'path/to/foo'],
            {
                subtitle.Subtitle(language='', forced=False, format='SRT'),
                subtitle.Subtitle(language='', forced=False, format='SSA'),
                subtitle.Subtitle(language='', forced=False, format='ASS'),
                subtitle.Subtitle(language='', forced=False, format='VTT'),
                subtitle.Subtitle(language='', forced=False, format=''),
            },
            id='No language in file name',
        ),
        pytest.param(
            ['path/to/foo.eng.srt', 'path/to/foo.fr.ssa', 'path/to/foo.invalid-code.ass', 'path/to/foo.vie.vtt'],
            {
                subtitle.Subtitle(language='en', forced=False, format='SRT'),
                subtitle.Subtitle(language='fr', forced=False, format='SSA'),
                subtitle.Subtitle(language='', forced=False, format='ASS'),
                subtitle.Subtitle(language='vie', forced=False, format='VTT'),
            },
            id='Language in file name',
        ),
    ),
    ids=lambda v: repr(v),
)
def test_get_subtitles_from_text_files(file_list, exp_subtitles, mocker):
    file_list_mock = mocker.patch('upsies.utils.fs.file_list', return_value=file_list)

    content_path = 'path/to/content'
    subtitles = subtitle.get_subtitles_from_text_files(content_path)
    assert subtitles == exp_subtitles

    assert file_list_mock.call_args_list == [
        call(content_path, extensions=('srt', 'ssa', 'ass', 'vtt')),
    ]


@pytest.mark.parametrize(
    argnames='existing_files, nonexisting_files, exp_subtitles',
    argvalues=(
        pytest.param(
            {},
            ['nosuchfile.idx'],
            set(),
            id='No subtitles',
        ),
        pytest.param(
            {
                'foo.idx': 'junk\nid: de, index: 0\nmore junk\n',
                'bar.idx': 'junk\nid: en, index: 1\nmore junk\n',
                'baz.idx': 'junk\nid: ru, index: 123\nmore junk\n',
                'none.idx': 'junk\n, index: 123\nmore junk\n',
                'nope.idx': 'junk\nid: invalidcode, index: 123\nmore junk\n',
            },
            ['nosuchfile.idx'],
            {
                subtitle.Subtitle(language='de', forced=False, format='VobSub'),
                subtitle.Subtitle(language='en', forced=False, format='VobSub'),
                subtitle.Subtitle(language='ru', forced=False, format='VobSub'),
                subtitle.Subtitle(language='', forced=False, format='VobSub'),
                subtitle.Subtitle(language='', forced=False, format='VobSub'),
            },
            id='Various subtitles',
        ),
    ),
    ids=lambda v: repr(v),
)
def test_get_subtitles_from_idx_files(existing_files, nonexisting_files, exp_subtitles, tmp_path, mocker):
    content_path = tmp_path / 'content'
    content_path.mkdir(parents=True, exist_ok=True)
    for file, data in existing_files.items():
        (content_path / file).write_text(data)

    file_list_mock = mocker.patch('upsies.utils.fs.file_list', return_value=(
        str(content_path / file)
        for file in (list(existing_files) + nonexisting_files)
    ))

    subtitles = subtitle.get_subtitles_from_idx_files(content_path)
    assert subtitles == exp_subtitles

    assert file_list_mock.call_args_list == [
        call(content_path, extensions=('idx',)),
    ]


@pytest.mark.parametrize(
    argnames='found_videos, exp_subtitles',
    argvalues=(
        (
            {
                'a.mkv': {'Video': ..., 'Audio': ..., 'Text': [{'Language': 'a', 'Forced': 'Yes', 'CodecID': 'S_TEXT/UTF8'}]},
                'VTS_01_02.VOB': {'Video': ..., 'Audio': ..., 'Text': [
                    {'Language': 'xa'},
                    {'Language': 'xb'},
                ]},
                'VIDEO_TS.IFO': {},
                'b.jpg': {},
                'VTS_03_04.VOB': {'Video': ..., 'Audio': ..., 'Text': [
                    {'Language': 'ya'},
                    {'Language': 'yb'},
                ]},
            },
            set((
                subtitle.Subtitle(language='xa', forced=False, format='VobSub'),
                subtitle.Subtitle(language='xb', forced=False, format='VobSub'),
                subtitle.Subtitle(language='ya', forced=False, format='VobSub'),
                subtitle.Subtitle(language='yb', forced=False, format='VobSub'),
            )),
        ),
    ),
    ids=lambda v: repr(v),
)
def test_get_subtitles_from_dvd_tree(found_videos, exp_subtitles, tmp_path, mocker):
    content_path = 'path/to/content'

    find_videos_mock = mocker.patch('upsies.utils.video.find_videos', return_value=tuple(found_videos))
    tracks_mock = mocker.patch('upsies.utils.video.tracks', side_effect=(
        tracks
        for filename, tracks in found_videos.items()
        if filename.upper().endswith('VOB')
    ))

    subtitles = subtitle.get_subtitles_from_dvd_tree(content_path)
    assert subtitles == exp_subtitles

    assert find_videos_mock.call_args_list == [
        call(content_path),
    ]
    assert tracks_mock.call_args_list == [
        call(re.sub(r'\d+.VOB', '0.IFO', filename))
        for filename in found_videos.keys()
        if filename.upper().endswith('VOB')
    ]
