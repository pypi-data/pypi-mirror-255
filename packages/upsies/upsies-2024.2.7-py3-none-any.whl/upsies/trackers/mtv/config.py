"""
Concrete :class:`~.base.TrackerConfigBase` subclass for MTV
"""

import base64

from ...utils import argtypes, configfiles, is_running_in_development_environment, types
from ..base import TrackerConfigBase, exclude

MtvImageHost = types.ImageHost(
    allowed=(
        ('imgbox', 'ptpimg', 'dummy')
        if is_running_in_development_environment() else
        ('imgbox', 'ptpimg')
    ),
)


class MtvTrackerConfig(TrackerConfigBase):
    defaults = {
        'base_url': base64.b64decode('aHR0cHM6Ly93d3cubW9yZXRoYW50di5tZQ==').decode('ascii'),
        'username': '',
        'password': '',
        'announce_url': configfiles.config_value(
            value='',
            description='Your personal announce URL. Automatically fetched from the website if not set.',
        ),
        'source': 'MTV',
        'image_host': configfiles.config_value(
            value=types.ListOf(
                item_type=MtvImageHost,
                default=('imgbox',),
                separator=',',
            ),
            description=(
                'List of image hosting service names. The first service is normally used '
                'with the others as backup if uploading to the first fails.\n'
                + 'Supported services: ' + ', '.join(MtvImageHost.options)
            ),
        ),
        'screenshots': configfiles.config_value(
            value=types.Integer(4, min=3, max=10),
            description='How many screenshots to make.',
        ),
        'exclude': (
            exclude.checksums,
            exclude.extras,
            exclude.images,
            exclude.nfo,
            exclude.samples,
            exclude.subtitles,
        ),
        'anonymous': configfiles.config_value(
            value=types.Bool('no'),
            description='Whether your username is displayed on your uploads.',
        ),
    }

    argument_definitions = {
        'submit': {
            ('--screenshots', '--ss'): {
                'help': ('How many screenshots to make '
                         f'(min={defaults["screenshots"].min}, '
                         f'max={defaults["screenshots"].max})'),
                'type': argtypes.number_of_screenshots(
                    min=defaults['screenshots'].min,
                    max=defaults['screenshots'].max,
                ),
            },
            ('--only-description', '--od'): {
                'help': 'Only generate description (do not upload anything)',
                'action': 'store_true',
                'group': 'generate-metadata',
            },
            ('--only-title', '--ot'): {
                'help': 'Only generate title (do not upload anything)',
                'action': 'store_true',
                'group': 'generate-metadata',
            },
            ('--ignore-dupes', '--id'): {
                'help': 'Force submission even if the tracker reports duplicates',
                'action': 'store_true',
            },
        },
    }
