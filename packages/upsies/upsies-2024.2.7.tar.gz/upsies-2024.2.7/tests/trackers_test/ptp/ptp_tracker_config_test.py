import base64

import pytest

from upsies import utils
from upsies.trackers import base
from upsies.trackers.ptp import PtpTrackerConfig


@pytest.fixture
def tracker_config():
    return PtpTrackerConfig()


def test_PtpTrackerConfig_defaults(tracker_config):
    assert set(tracker_config) == {
        'base_url',
        'username',
        'password',
        'announce_url',
        'source',
        'randomize_infohash',
        'image_host',
        'screenshots_from_movie',
        'screenshots_from_episode',
        'exclude',

        # Inherited from TrackerConfigBase
        'add_to',
        'copy_to',
    }


def test_PtpTrackerConfig_defaults_base_url(tracker_config):
    assert tracker_config['base_url'] == base64.b64decode('aHR0cHM6Ly9wYXNzdGhlcG9wY29ybi5tZQ==').decode('ascii')


def test_PtpTrackerConfig_defaults_username(tracker_config):
    assert tracker_config['username'] == ''


def test_PtpTrackerConfig_defaults_password(tracker_config):
    assert tracker_config['password'] == ''


def test_PtpTrackerConfig_defaults_announce_url(tracker_config):
    assert tracker_config['announce_url'] == ''
    assert tracker_config['announce_url'].description == (
        'Your personal announce URL.'
    )


def test_PtpTrackerConfig_defaults_source(tracker_config):
    assert tracker_config['source'] == 'PTP'


def test_PtpTrackerConfig_defaults_image_host(tracker_config, assert_config_list_of_choice):
    exp_options = utils.imghosts.imghost_names()
    assert_config_list_of_choice(
        items=tracker_config['image_host'],
        exp_items=('ptpimg', 'imgbox'),
        exp_options=exp_options,
        exp_description=(
            'List of image hosting service names. The first service is normally used '
            + 'with the others as backup if uploading to the first fails.\n'
            + 'Supported services: ' + ', '.join(exp_options)
        ),
    )


def test_PtpTrackerConfig_defaults_screenshots_from_movie(tracker_config, assert_config_number):
    assert_config_number(
        number=tracker_config['screenshots_from_movie'],
        value=3,
        min=3,
        max=10,
        description='How many screenshots to make for single-video uploads.',
    )


def test_PtpTrackerConfig_defaults_screenshots_from_episode(tracker_config, assert_config_number):
    assert_config_number(
        number=tracker_config['screenshots_from_episode'],
        value=2,
        min=2,
        max=10,
        description='How many screenshots to make per video for multi-video uploads.',
    )


def test_PtpTrackerConfig_defaults_exclude(tracker_config):
    assert tracker_config['exclude'] == (
        utils.types.RegEx(base.exclude.checksums),
        utils.types.RegEx(base.exclude.images),
        utils.types.RegEx(base.exclude.nfo),
        utils.types.RegEx(base.exclude.samples),
    )


def test_PtpTrackerConfig_arguments(tracker_config):
    exp_argument_definitions = {
        'submit': {
            ('--hardcoded-subtitles', '--hs'),
            ('--no-english-subtitles', '--nes'),
            ('--not-main-movie', '--nmm'),
            ('--personal-rip', '--pr'),
            ('--poster', '--po'),
            ('--screenshots', '--ss'),
            ('--upload-token', '--ut'),
            ('--only-description', '--od'),
        },
    }
    assert set(tracker_config.argument_definitions) == set(exp_argument_definitions)
    for command in exp_argument_definitions:
        assert set(tracker_config.argument_definitions[command]) == exp_argument_definitions[command]


def test_PtpTrackerConfig_argument_definitions_submit_hardcoded_subtitles(tracker_config):
    assert tracker_config.argument_definitions['submit'][('--hardcoded-subtitles', '--hs')] == {
        'help': 'Video contains hardcoded subtitles',
        'action': 'store_true',
    }


def test_PtpTrackerConfig_argument_definitions_submit_no_english_subtitles(tracker_config):
    assert tracker_config.argument_definitions['submit'][('--no-english-subtitles', '--nes')] == {
        'help': (
            'Whether release contains no English audio and no English subtitles.'
            '\n'
            'This is autodetected if an audio or subtitle track with an English '
            'language tag can be found. Subtitle language tags are detected in '
            '*.idx/sub, VIDEO_TS trees and *.srt/ssa/ass/vtt (by language code '
            'in the file name, e.g. "Foo.en.srt").'
        ),
        'metavar': 'BOOL',
        'type': utils.argtypes.bool_or_none,
    }


def test_PtpTrackerConfig_argument_definitions_submit_not_main_movie(tracker_config):
    assert tracker_config.argument_definitions['submit'][('--not-main-movie', '--nmm')] == {
        'help': 'Upload ONLY contains extras, Rifftrax, Workprints',
        'action': 'store_true',
    }


def test_PtpTrackerConfig_argument_definitions_submit_personal_rip(tracker_config):
    assert tracker_config.argument_definitions['submit'][('--personal-rip', '--pr')] == {
        'help': 'Tag as your own encode',
        'action': 'store_true',
    }


def test_PtpTrackerConfig_argument_definitions_submit_poster(tracker_config):
    assert tracker_config.argument_definitions['submit'][('--poster', '--po')] == {
        'help': 'Path or URL to movie poster',
    }


def test_PtpTrackerConfig_argument_definitions_submit_screenshots(tracker_config):
    assert tracker_config.argument_definitions['submit'][('--screenshots', '--ss')] == {
        'help': 'How many screenshots to make per video file',
        'type': utils.argtypes.number_of_screenshots(min=1, max=10),
    }


def test_PtpTrackerConfig_argument_definitions_submit_upload_token(tracker_config):
    assert tracker_config.argument_definitions['submit'][('--upload-token', '--ut')] == {
        'help': 'Upload token from staff',
    }
