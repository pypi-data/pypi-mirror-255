"""
Commands related to torrent files
"""

import functools
import os

from .... import constants, jobs, trackers, utils
from .base import CommandBase


class torrent_add(CommandBase):
    """Add torrent file to BitTorrent client"""

    names = ('torrent-add', 'ta')

    argument_definitions = {
        'CLIENT': {
            'type': utils.argtypes.client,
            'help': ('Case-insensitive BitTorrent client name\n'
                     'Supported clients: ' + ', '.join(utils.btclient.client_names())),
        },
        'TORRENT': {
            'nargs': '+',
            'help': 'Path to torrent file',
        },
        ('--download-path', '-p'): {
            'help': "Parent directory of the torrent's content",
            'metavar': 'DIRECTORY',
        },
    }

    @functools.cached_property
    def jobs(self):
        return (
            jobs.torrent.AddTorrentJob(
                home_directory=self.home_directory,
                cache_directory=self.cache_directory,
                ignore_cache=self.args.ignore_cache,
                btclient=utils.btclient.BtClient(
                    name=self.args.CLIENT,
                    url=self.client_options['url'],
                    username=self.client_options['username'],
                    password=self.client_options['password'],
                    download_path=self.download_path,
                    check_after_add=self.client_options['check_after_add'],
                    category=self.client_options.get('category', ''),
                ),
                enqueue=self.args.TORRENT,
            ),
        )

    @functools.cached_property
    def client_options(self):
        return self.get_options('clients', self.args.CLIENT)

    @functools.cached_property
    def download_path(self):
        if self.args.download_path:
            # Make provided --download-path absolute before doing path
            # translation to get the path the client should use, which may run
            # on a different computer.
            return self.client_options['translate_path'].translate(
                os.path.abspath(self.args.download_path)
            )
        else:
            # Use client's default path
            return None


class torrent_create(CommandBase):
    """
    Create torrent file and optionally add or copy it

    The piece hashes are cached and re-used if possible. This means the torrent
    is not generated for every tracker again. Note that the torrent is always
    generated if files are excluded on one tracker but not on the other. The
    files in each torrent must be identical.
    """

    names = ('torrent-create', 'tc')

    argument_definitions = {}

    subcommand_name = 'TRACKER'
    subcommands = {
        tracker.name: {
            'description': (
                f'Create a torrent file for {tracker.label} '
                'in the current working directory.'
            ),
            'cli': {
                # Default arguments for all tackers
                **{
                    'CONTENT': {
                        'type': utils.argtypes.content,
                        'help': 'Path to release content',
                    },
                    ('--exclude-files', '--ef'): {
                        'nargs': '+',
                        'metavar': 'PATTERN',
                        'help': ('Glob pattern to exclude from torrent '
                                 '(matched case-insensitively against path in torrent)'),
                        'default': (),
                    },
                    ('--exclude-files-regex', '--efr'): {
                        'nargs': '+',
                        'metavar': 'PATTERN',
                        'help': ('Regular expression to exclude from torrent '
                                 '(matched case-sensitively against path in torrent)'),
                        'type': utils.argtypes.regex,
                        'default': (),
                    },
                    ('--reuse-torrent', '-t'): {
                        'nargs': '+',
                        'metavar': 'TORRENT',
                        'help': ('Use hashed pieces from TORRENT instead of generating '
                                 'them again or getting them from '
                                 f'{utils.fs.tildify_path(constants.GENERIC_TORRENTS_DIRPATH)}\n'
                                 'TORRENT may also be a directory, which is searched recursively '
                                 'for a matching *.torrent file.\n'
                                 "NOTE: This option is ignored if TORRENT doesn't match CONTENT properly."),
                        'type': utils.argtypes.existing_path,
                        'default': (),
                    },
                    ('--add-to', '-a'): {
                        'type': utils.argtypes.client,
                        'metavar': 'CLIENT',
                        'help': ('Case-insensitive BitTorrent client name\n'
                                 'Supported clients: ' + ', '.join(utils.btclient.client_names())),
                    },
                    ('--copy-to', '-c'): {
                        'metavar': 'PATH',
                        'help': 'Copy the created torrent to PATH (file or directory)',
                    },
                },
                # Custom arguments defined by tracker for this command
                **tracker.TrackerConfig.argument_definitions.get('torrent-create', {}),
            }
        }
        for tracker in trackers.trackers()
    }

    @functools.cached_property
    def tracker_name(self):
        return self.args.subcommand.lower()

    @functools.cached_property
    def tracker(self):
        return trackers.tracker(
            name=self.tracker_name,
            options={
                **self.config['trackers'][self.tracker_name],
                **vars(self.args),
            },
        )

    @property
    def home_directory(self):
        """Create torrent file in current working directory"""
        return '.'

    @functools.cached_property
    def create_torrent_job(self):
        return jobs.torrent.CreateTorrentJob(
            home_directory=self.home_directory,
            cache_directory=self.cache_directory,
            ignore_cache=self.args.ignore_cache,
            content_path=self.args.CONTENT,
            reuse_torrent_path=(
                tuple(self.args.reuse_torrent)
                + tuple(self.config['config']['torrent-create']['reuse_torrent_paths'])
            ),
            tracker=self.tracker,
            exclude_files=(
                tuple(self.args.exclude_files)
                + tuple(self.args.exclude_files_regex)
            ),
            callbacks={
                'announce_url': self.logout_after_getting_announce_url,
            },
        )

    def logout_after_getting_announce_url(self, announce_url):
        # The "announce_url" signal is emitted twice: First we attempt to get
        # the announce URL and the signal callback is called with `Ellipsis`.
        # Then the signal is emitted again with the announce URL.
        if announce_url is not Ellipsis:
            async def logout():
                await self.tracker.logout()

            self.create_torrent_job.add_task(logout())

    @functools.cached_property
    def add_torrent_job(self):
        if self.args.add_to:
            add_torrent_job = jobs.torrent.AddTorrentJob(
                home_directory=self.home_directory,
                cache_directory=self.cache_directory,
                ignore_cache=self.args.ignore_cache,
                btclient=utils.btclient.BtClient(
                    name=self.args.add_to,
                    url=self.client_options['url'],
                    username=self.client_options['username'],
                    password=self.client_options['password'],
                    download_path=self.download_path,
                    check_after_add=self.client_options['check_after_add'],
                    category=self.client_options.get('category', ''),
                ),
            )

            # Pass CreateTorrentJob output to AddTorrentJob input.
            self.create_torrent_job.signal.register('output', add_torrent_job.enqueue)

            # Finish AddTorrentJob when CreateTorrentJob is finished. The
            # torrent will be enqueued and AddTorrentJob will finish after
            # adding the enqueued torrent.
            self.create_torrent_job.signal.register('finished', lambda _: add_torrent_job.close())

            return add_torrent_job

    @functools.cached_property
    def client_options(self):
        return self.get_options('clients', self.args.add_to)

    @functools.cached_property
    def download_path(self):
        # By default, we assume we are running on the same computer as the
        # client, in which case the download_path is identical to the parent
        # directory of the provided CONTENT path.
        #
        # If the client is running on a different computer, we apply a
        # user-configured search-and-replace path translation.
        #
        # In either case, we first make the download_path absolute for easier
        # trouble-shooting and to make the path translation predictable.
        return self.client_options['translate_path'].translate(
            os.path.abspath(utils.fs.dirname(self.args.CONTENT))
        )

    @functools.cached_property
    def copy_torrent_job(self):
        if self.args.copy_to:
            copy_torrent_job = jobs.torrent.CopyTorrentJob(
                home_directory=self.home_directory,
                cache_directory=self.cache_directory,
                ignore_cache=self.args.ignore_cache,
                destination=self.args.copy_to,
            )
            # Pass CreateTorrentJob output to CopyTorrentJob input.
            self.create_torrent_job.signal.register('output', copy_torrent_job.enqueue)
            # Tell CopyTorrentJob to finish when CreateTorrentJob is done.
            self.create_torrent_job.signal.register('finished', lambda _: copy_torrent_job.close())
            return copy_torrent_job

    @functools.cached_property
    def jobs(self):
        return (
            self.create_torrent_job,
            self.add_torrent_job,
            self.copy_torrent_job,
        )
