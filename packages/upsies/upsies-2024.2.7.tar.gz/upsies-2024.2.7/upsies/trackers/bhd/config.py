"""
Concrete :class:`~.base.TrackerConfigBase` subclass for BHD
"""

import base64

from ...utils import argtypes, configfiles, is_running_in_development_environment, types
from ..base import TrackerConfigBase, exclude

BhdImageHost = types.ImageHost(
    allowed=(
        ('imgbox', 'ptpimg', 'imgbb', 'dummy')
        if is_running_in_development_environment() else
        ('imgbox', 'ptpimg', 'imgbb')
    ),
)


class BhdTrackerConfig(TrackerConfigBase):
    defaults = {
        'upload_url': base64.b64decode('aHR0cHM6Ly9iZXlvbmQtaGQubWUvYXBpL3VwbG9hZA==').decode('ascii'),
        'announce_url': configfiles.config_value(
            value=base64.b64decode('aHR0cHM6Ly9iZXlvbmQtaGQubWUvYW5ub3VuY2U=').decode('ascii'),
            description='The announce URL without the private passkey.',
        ),
        'announce_passkey': configfiles.config_value(
            value='',
            description=(
                'The private part of the announce URL.\n'
                'Get it from the website: My Security -> Passkey'
            ),
        ),
        'apikey': configfiles.config_value(
            value='',
            description=(
                'Your personal private API key.\n'
                'Get it from the website: My Security -> API key'
            ),
        ),
        'source': 'BHD',
        'anonymous': configfiles.config_value(
            value=types.Bool('no'),
            description='Whether your username is displayed on your uploads.',
        ),
        'draft': configfiles.config_value(
            value=types.Bool('no'),
            description=(
                'Whether your uploads are stashed under Torrents -> Drafts '
                'after the upload instead of going live.'
            ),
        ),
        'image_host': configfiles.config_value(
            value=types.ListOf(
                item_type=BhdImageHost,
                default=('imgbox',),
                separator=',',
            ),
            description=(
                'List of image hosting service names. The first service is normally used '
                'with the others as backup if uploading to the first fails.\n'
                + 'Supported services: ' + ', '.join(BhdImageHost.options)
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
    }

    argument_definitions = {
        'submit': {
            ('--custom-edition', '--ce'): {
                'help': 'Non-standard edition, e.g. "Final Cut"',
                'default': '',
            },
            ('--draft', '--dr'): {
                'help': 'Upload as draft',
                'action': 'store_true',
                # The default value must be None so CommandBase.get_options()
                # doesn't always overwrite the value with the config file value.
                'default': None,
            },
            ('--personal-rip', '--pr'): {
                'help': 'Tag as your own encode',
                'action': 'store_true',
            },
            ('--screenshots', '--ss'): {
                'help': ('How many screenshots to make '
                         f'(min={defaults["screenshots"].min}, '
                         f'max={defaults["screenshots"].max})'),
                'type': argtypes.number_of_screenshots(
                    min=defaults['screenshots'].min,
                    max=defaults['screenshots'].max,
                ),
            },
            ('--special', '--sp'): {
                'help': 'Tag as special episode, e.g. Christmas special (ignored for movie uploads)',
                'action': 'store_true',
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
        },
    }
