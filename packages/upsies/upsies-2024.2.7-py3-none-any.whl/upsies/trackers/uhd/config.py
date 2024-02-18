"""
Concrete :class:`~.base.TrackerConfigBase` subclass for UHD
"""

import base64

from ...utils import argtypes, configfiles, is_running_in_development_environment, types
from ..base import TrackerConfigBase

UhdImageHost = types.ImageHost(
    disallowed=(
        ()
        if is_running_in_development_environment() else
        ('dummy',)
    ),
)


class UhdTrackerConfig(TrackerConfigBase):
    defaults = {
        'base_url': base64.b64decode('aHR0cHM6Ly91aGRiaXRzLm9yZw==').decode('ascii'),
        'username': '',
        'password': '',
        'anonymous': configfiles.config_value(
            value=types.Bool('no'),
            description='Whether your username is displayed on your uploads.',
        ),
        'announce_url': configfiles.config_value(
            value='',
            description='Your personal announce URL.',
        ),
        'source': '[UHDBits]',
        'image_host': configfiles.config_value(
            value=types.ListOf(
                item_type=UhdImageHost,
                default=('ptpimg', 'freeimage', 'imgbox'),
                separator=',',
            ),
            description=(
                'List of image hosting service names. The first service is normally used '
                'with the others as backup if uploading to the first fails.\n'
                + 'Supported services: ' + ', '.join(UhdImageHost.options)
            ),
        ),
        'screenshots': configfiles.config_value(
            value=types.Integer(4, min=2, max=10),
            description='How many screenshots to make.',
        ),
        'exclude': (
        ),
    }

    argument_definitions = {
        'submit': {
            ('--anonymous', '--an'): {
                'help': 'Hide your username for this submission',
                'action': 'store_true',
            },
            ('--internal', '--in'): {
                'help': 'Internal encode (use only if you were told to)',
                'action': 'store_true',
            },
            ('--3d',): {
                'help': 'Mark this as a 3D release',
                'action': 'store_true',
            },
            ('--vie', '--vi'): {
                'help': 'Release contains Vietnamese audio dub',
                'action': 'store_true',
            },
            ('--screenshots', '--ss'): {
                'help': 'How many screenshots to make',
                'type': argtypes.number_of_screenshots(min=2, max=10),
            },
            ('--poster', '--po'): {
                'help': 'Path or URL to poster image (autodetected by default)',
            },
            ('--trailer', '--tr'): {
                'help': 'Trailer YouTube ID or URL (autodetected by default)',
            },
            ('--only-description', '--od'): {
                'help': 'Only generate description (do not upload anything)',
                'action': 'store_true',
                'group': 'generate-metadata',
            },
        },
    }
