import base64

import pytest

from upsies import utils
from upsies.trackers.uhd import UhdTrackerConfig


@pytest.fixture
def tracker_config():
    return UhdTrackerConfig()


def test_UhdTrackerConfig_defaults(tracker_config):
    assert set(tracker_config) == {
        'base_url',
        'username',
        'password',
        'anonymous',
        'announce_url',
        'source',
        'image_host',
        'screenshots',
        'exclude',

        # Inherited from TrackerConfigBase
        'add_to',
        'copy_to',
        'randomize_infohash',
    }


def test_UhdTrackerConfig_defaults_base_url(tracker_config):
    assert tracker_config['base_url'] == base64.b64decode('aHR0cHM6Ly91aGRiaXRzLm9yZw==').decode('ascii')


def test_UhdTrackerConfig_defaults_username(tracker_config):
    assert tracker_config['username'] == ''


def test_UhdTrackerConfig_defaults_password(tracker_config):
    assert tracker_config['password'] == ''


def test_UhdTrackerConfig_defaults_anonymous(tracker_config):
    assert isinstance(tracker_config['anonymous'], utils.types.Bool)
    assert not tracker_config['anonymous']
    assert tracker_config['anonymous'] == 'no'
    assert tracker_config['anonymous'].description == (
        'Whether your username is displayed on your uploads.'
    )


def test_UhdTrackerConfig_defaults_announce_url(tracker_config):
    assert tracker_config['announce_url'] == ''
    assert tracker_config['announce_url'].description == (
        'Your personal announce URL.'
    )


def test_UhdTrackerConfig_defaults_source(tracker_config):
    assert tracker_config['source'] == '[UHDBits]'


def test_UhdTrackerConfig_defaults_image_host(tracker_config, assert_config_list_of_choice):
    exp_options = utils.imghosts.imghost_names()
    assert_config_list_of_choice(
        items=tracker_config['image_host'],
        exp_items=('ptpimg', 'freeimage', 'imgbox'),
        exp_options=exp_options,
        exp_description=(
            'List of image hosting service names. The first service is normally used '
            + 'with the others as backup if uploading to the first fails.\n'
            + 'Supported services: ' + ', '.join(exp_options)
        ),
    )


def test_UhdTrackerConfig_defaults_screenshots(tracker_config, assert_config_number):
    assert_config_number(
        number=tracker_config['screenshots'],
        value=4,
        min=2,
        max=10,
        description='How many screenshots to make.',
    )


def test_UhdTrackerConfig_defaults_exclude(tracker_config):
    assert tracker_config['exclude'] == ()


def test_UhdTrackerConfig_arguments(tracker_config):
    exp_argument_definitions = {
        'submit': {
            ('--anonymous', '--an'),
            ('--internal', '--in'),
            ('--3d',),
            ('--vie', '--vi'),
            ('--screenshots', '--ss'),
            ('--poster', '--po'),
            ('--trailer', '--tr'),
            ('--only-description', '--od'),
        },
    }
    assert set(tracker_config.argument_definitions) == set(exp_argument_definitions)
    for command in exp_argument_definitions:
        assert set(tracker_config.argument_definitions[command]) == exp_argument_definitions[command]


def test_UhdTrackerConfig_argument_definitions_submit_anonymous(tracker_config):
    assert tracker_config.argument_definitions['submit'][('--anonymous', '--an')] == {
        'help': 'Hide your username for this submission',
        'action': 'store_true',
    }


def test_UhdTrackerConfig_argument_definitions_submit_internal(tracker_config):
    assert tracker_config.argument_definitions['submit'][('--internal', '--in')] == {
        'help': 'Internal encode (use only if you were told to)',
        'action': 'store_true',
    }


def test_UhdTrackerConfig_argument_definitions_submit_3d(tracker_config):
    assert tracker_config.argument_definitions['submit'][('--3d',)] == {
        'help': 'Mark this as a 3D release',
        'action': 'store_true',
    }


def test_UhdTrackerConfig_argument_definitions_submit_vie(tracker_config):
    assert tracker_config.argument_definitions['submit'][('--vie', '--vi')] == {
        'help': 'Release contains Vietnamese audio dub',
        'action': 'store_true',
    }


def test_UhdTrackerConfig_argument_definitions_submit_screenshots(tracker_config):
    assert tracker_config.argument_definitions['submit'][('--screenshots', '--ss')] == {
        'help': 'How many screenshots to make',
        'type': utils.argtypes.number_of_screenshots(min=2, max=10),
    }


def test_UhdTrackerConfig_argument_definitions_submit_poster(tracker_config):
    assert tracker_config.argument_definitions['submit'][('--poster', '--po')] == {
        'help': 'Path or URL to poster image (autodetected by default)',
    }


def test_UhdTrackerConfig_argument_definitions_submit_trailer(tracker_config):
    assert tracker_config.argument_definitions['submit'][('--trailer', '--tr')] == {
        'help': 'Trailer YouTube ID or URL (autodetected by default)',
    }


def test_UhdTrackerConfig_argument_definitions_submit_only_descrption(tracker_config):
    assert tracker_config.argument_definitions['submit'][('--only-description', '--od')] == {
        'help': 'Only generate description (do not upload anything)',
        'action': 'store_true',
        'group': 'generate-metadata',
    }
