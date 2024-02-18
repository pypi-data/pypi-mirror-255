"""
Dummy tracker for testing and debugging
"""

import asyncio
import functools
import os
import random
import string

from .. import errors, jobs, uis, utils
from . import base

import logging  # isort:skip
_log = logging.getLogger(__name__)


DummyImageHost = utils.types.ImageHost(allowed=('dummy',))


class DummyTrackerConfig(base.TrackerConfigBase):
    defaults = {
        'base_url': 'http://localhost',
        'username': '',
        'password': '',
        'exclude': (),
        'source': 'DMY',
        'image_host': utils.configfiles.config_value(
            value=utils.types.ListOf(
                item_type=DummyImageHost,
                default=DummyImageHost.options,
                separator=',',
            ),
            description=(
                'List of image hosting service names. The first service is normally used '
                + 'with the others as backup if uploading to the first fails.\n'
                + 'Supported services: ' + ', '.join(DummyImageHost.options)
            ),
        ),
    }

    argument_definitions = {
        'submit': {
            ('--skip-category', '-C'): {
                'help': 'Do not ask for category',
                'action': 'store_true',
            },
            ('--screenshots', '--ss'): {
                'help': 'How many screenshots to make',
                'type': int,
                'default': 3,
            },
            ('--delay', '-d'): {
                'help': 'Number of seconds login, upload and logout take each',
                'type': float,
                'default': 1.0,
            },
            ('--get-announce-from-website'): {
                'help': 'Whether to act like we are getting the announce URL from the website ',
                'action': 'store_true',
            },
        },
        'torrent-create': {
            ('--delay', '-d'): {
                'help': 'Number of seconds login and logout take each',
                'type': float,
                'default': 0.0,
            },
            ('--get-announce-from-website'): {
                'help': 'Whether to act like we are getting the announce URL from the website ',
                'action': 'store_true',
            },
        },
    }


class DummyTrackerJobs(base.TrackerJobsBase):

    release_name_separator = '_'

    @functools.cached_property
    def jobs_before_upload(self):
        return (
            # Interactive jobs
            self.tmdb_job,
            self.imdb_job,
            self.release_name_job,
            self.category_job,
            self.scene_check_job,

            # Background jobs
            self.create_torrent_job,
            self.screenshots_job,
            self.upload_screenshots_job,
            self.poster_job,
            self.mediainfo_job,

            # Silly jobs
            self.random_string_job,
            self.stupid_question_job,
            self.say_something_job,
        )

    @functools.cached_property
    def random_string_job(self):
        return jobs.custom.CustomJob(
            name=self.get_job_name('random-string'),
            label='Random String',
            precondition=self.make_precondition('random_string_job'),
            worker=self.generate_random_string,
            catch=(
                errors.RequestError,
            ),
            **self.common_job_args(ignore_cache=True),
        )

    async def generate_random_string(self, job):
        # await asyncio.sleep(3)
        # self.random_string_job.warn('Watch out!')

        await asyncio.sleep(1)

        # raise errors.RequestError('foo :(')
        # raise RuntimeError('foo D:')

        return ''.join((
            random.choice(string.ascii_lowercase)
            for _ in range(30)
        ))

    @functools.cached_property
    def stupid_question_job(self):
        return jobs.dialog.ChoiceJob(
            name=self.get_job_name('stupid-question'),
            label='Stupid Question',
            precondition=self.make_precondition('stupid_question_job'),
            prejobs=(
                self.random_string_job,
            ),
            autodetect=self.autodetect_stupid_answer,
            question='Is the random string random enough?',
            options=(
                'Possibly',
                'Maybe',
                'Perhaps',
            ),
            callbacks={
                'finished': lambda job: job.clear_warnings(),
            },
            **self.common_job_args(),
        )

    async def autodetect_stupid_answer(self, job):
        assert self.random_string_job.is_finished

        # raise RuntimeError('How would I know?')

        random_string = self.random_string_job.output[0]
        if all(character in random_string for character in 'abcd'):
            return 'Possibly'
        elif all(character in random_string for character in 'def'):
            return 'Maybe'
        elif all(character in random_string for character in 'gh'):
            return 'Perhaps'
        else:
            self.stupid_question_job.add_prompt(
                uis.prompts.RadioListPrompt(
                    question='Is this job too stupid?',
                    options=('Yes', 'No'),
                    callbacks=(
                        self.prompt_stupid_answer_callback,
                    ),
                )
            )
            self.stupid_question_job.add_prompt(
                uis.prompts.RadioListPrompt(
                    question='Are you sure?',
                    options=('Yes', 'No', "Maybe?"),
                    callbacks=(
                        self.prompt_stupid_answer_callback_2,
                    ),
                )
            )
            self.stupid_question_job.add_prompt(
                uis.prompts.RadioListPrompt(
                    options=('Foo', 'Bar'),
                    callbacks=(),
                )
            )

    def prompt_stupid_answer_callback(self, result):
        if result == 'Yes':
            self.stupid_question_job.error('This job is too stupid.')
        else:
            self.stupid_question_job.warn('Choose wisely!')

    def prompt_stupid_answer_callback_2(self, result):
        if result == 'Yes':
            self.stupid_question_job.warn('This job is definitely not too stupid.')
        elif result == 'No':
            self.stupid_question_job.error('This job may be too stupid after all!')
        else:
            self.stupid_question_job.warn('Okay?')

    @functools.cached_property
    def say_something_job(self):
        return jobs.dialog.TextFieldJob(
            name=self.get_job_name('say-something'),
            label='Something',
            precondition=self.make_precondition('say_something_job'),
            prejobs=(
                self.random_string_job,
            ),
            nonfatal_exceptions=(
                ValueError,
            ),
            text=self.generate_something,
            **self.common_job_args(),
        )

    async def generate_something(self):
        assert self.random_string_job.is_finished
        word = self.random_string_job.output[0]

        await asyncio.sleep(6)
        self.say_something_job.warn('Still thinking...')
        await asyncio.sleep(6)

        self.say_something_job.clear_warnings()
        if 'x' in word:
            raise ValueError(f'There is an "x" in "{word}"! Yuck!')
        elif 'a' in word:
            return 'Avocado!'
        else:
            return f'This is a completely original random string: {word}'

    @functools.cached_property
    def category_job(self):
        if not self.options['skip_category']:
            return jobs.dialog.ChoiceJob(
                name=self.get_job_name('category'),
                label='Category',
                precondition=self.make_precondition('category_job'),
                options=(
                    (str(typ).capitalize(), typ)
                    for typ in utils.types.ReleaseType if typ
                ),
                autodetected=self.release_name.type,
                **self.common_job_args(),
            )


class DummyTracker(base.TrackerBase):
    name = 'dummy'
    label = 'DuMmY'

    setup_howto_template = (
        'This is just a no-op tracker for testing and demonstration.'
    )

    TrackerJobs = DummyTrackerJobs
    TrackerConfig = DummyTrackerConfig

    async def _login(self):
        _log.debug('%s: Logging in with %r', self.name, self.options)
        await asyncio.sleep(self.options['delay'])
        _log.debug('%s: Logged in with %r', self.name, self.options)

    async def _logout(self):
        _log.debug('%s: Logging out', self.name)
        await asyncio.sleep(self.options['delay'])
        _log.debug('%s: Logged out', self.name)

    async def get_announce_url(self):
        if self.options['get_announce_from_website']:
            _log.debug('%s: Getting announce URL from website', self.name)
            await self.login()
            await asyncio.sleep(1)
        else:
            _log.debug('%s: Getting announce URL from config file', self.name)
        return 'http://localhost:123/f1dd15718/announce'

    async def upload(self, tracker_jobs):
        if tracker_jobs.create_torrent_job.output:
            torrent_file = tracker_jobs.create_torrent_job.output[0]
        else:
            raise errors.RequestError('Torrent file was not created.')
        _log.debug('%s: Uploading %s', self.name, torrent_file)
        await asyncio.sleep(self.options['delay'])
        return f'http://localhost/{os.path.basename(torrent_file)}'
