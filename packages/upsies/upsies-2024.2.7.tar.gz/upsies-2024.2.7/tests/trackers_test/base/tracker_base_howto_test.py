import itertools
from unittest.mock import Mock, PropertyMock

import pytest

from upsies import __project_name__, utils
from upsies.trackers.base import _howto


def make_tracker(name):
    tracker = Mock()
    tracker.configure_mock(name=name)
    return tracker


@pytest.fixture
def tracker_cls():
    return make_tracker('foo')


@pytest.fixture
def howto(tracker_cls):
    return _howto.Howto(tracker_cls=tracker_cls)


@pytest.fixture
def mock_next_and_current_section(howto, mocker):
    def next_section(counter=itertools.count(start=1, step=1)):
        return 'N' * next(counter)

    def current_section(counter=itertools.count(start=1, step=1)):
        return 'C' * next(counter)

    mocker.patch.object(type(howto), 'next_section', PropertyMock(side_effect=next_section))
    mocker.patch.object(type(howto), 'current_section', PropertyMock(side_effect=current_section))


def test__init__(howto, tracker_cls):
    assert howto._tracker_cls is tracker_cls
    assert howto._section == -1


def test_join(howto):
    joined = howto.join('  \n foo\n', '  bar \n\t ')
    assert joined == 'foo\n\n  bar'


def test_next_and_current_section(howto):
    assert howto.next_section == 0
    assert howto.current_section == 0
    assert howto.current_section == 0
    assert howto.next_section == 1
    assert howto.current_section == 1
    assert howto.current_section == 1
    assert howto.next_section == 2
    assert howto.current_section == 2
    assert howto.current_section == 2
    assert howto.next_section == 3
    assert howto.current_section == 3
    assert howto.current_section == 3


def test_introduction(howto, mock_next_and_current_section):
    assert howto.introduction == (
        'N. How To Read This Howto\n'
        '\n'
        '   C.1 Words in ALL_CAPS_AND_WITH_UNDERSCORES are placeholders.\n'
        '   CC.2 Everything after "$" is a terminal command.'
    )


def test_screenshots(howto, mock_next_and_current_section, tracker_cls):
    tracker_cls.TrackerConfig.defaults = {
        'image_host': Mock(
            item_type=Mock(
                options=('fooimg', 'imgbar', 'bazi'),
            ),
        ),
    }

    assert howto.screenshots == (
        'N. Screenshots (Optional)\n'
        '\n'
        '   C.1 Specify how many screenshots to make.\n'
        f'       $ {__project_name__} set trackers.{tracker_cls.name}.screenshots NUMBER_OF_SCREENSHOTS\n'
        '\n'
        '   CC.2 Specify where to host images.\n'
        f'       $ {__project_name__} set trackers.{tracker_cls.name}.image_host IMAGE_HOST,IMAGE_HOST,...\n'
        '       If IMAGE_HOST is down, try the next one.\n'
        '       Supported services: fooimg, imgbar, bazi\n'
        '\n'
        '   CCC.3 Configure image hosting service.\n'
        f'       $ {__project_name__} upload-images IMAGE_HOST --help'
    )


def test_autoseed(howto, mock_next_and_current_section, tracker_cls):
    assert howto.autoseed == (
        'N. Add Uploaded Torrents To Client (Optional)\n'
        '\n'
        '   C.1 Specify which client to add uploaded torrents to.\n'
        f'       $ {__project_name__} set trackers.{tracker_cls.name}.add_to CLIENT_NAME\n'
        f'       Supported clients: ' + ', '.join(utils.btclient.client_names()) + '\n'
        '\n'
        '   CC.2 Specify your client connection.\n'
        f'       $ {__project_name__} set clients.CLIENT_NAME.url URL\n'
        f'       $ {__project_name__} set clients.CLIENT_NAME.username USERNAME\n'
        f'       $ {__project_name__} set clients.CLIENT_NAME.password PASSWORD\n'
        '\n'
        'NN. Copy Uploaded Torrents To Directory (Optional)\n'
        '\n'
        f'   $ {__project_name__} set trackers.{tracker_cls.name}.copy_to /path/to/directory'
    )


def test_reuse_torrents(howto, mock_next_and_current_section, tracker_cls):
    assert howto.reuse_torrents == (
        'N. Reuse Existing Torrents (Optional)\n'
        '\n'
        '    You can skip the hashing when creating a torrent by specifying\n'
        '    a directory path that contains the torrents you are seeding.\n'
        '    A matching torrent is found by searching the directory recursively\n'
        '    for a torrent with the same size and file names. If such a torrent is\n'
        '    found, a few pieces of each file are hashed to verify the match.\n'
        '\n'
        f'    $ {__project_name__} set config.torrent-create.reuse_torrent_paths TORRENT_DIRECTORY'
    )


def test_upload(howto, mock_next_and_current_section, tracker_cls):
    assert howto.upload == (
        f'N. Upload\n'
        '\n'
        f'   $ {__project_name__} submit {tracker_cls.name} --help\n'
        f'   $ {__project_name__} submit {tracker_cls.name} /path/to/content'
    )
