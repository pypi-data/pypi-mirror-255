"""
Concrete :class:`~.base.TrackerJobsBase` subclass for UHD
"""

import functools
import re
import urllib.parse
from datetime import datetime

import unidecode

from ... import __homepage__, __project_name__, errors, jobs, utils
from ..base import TrackerJobsBase

import logging  # isort:skip
_log = logging.getLogger(__name__)


class UhdTrackerJobs(TrackerJobsBase):

    @functools.cached_property
    def jobs_before_upload(self):
        # Don't start poster_job until we have an IMDb ID.
        self.poster_job.prejobs += (self.imdb_job,)

        return (
            # Interactive jobs
            self.imdb_job,
            self.type_job,
            self.year_job,
            self.quality_job,
            self.version_job,
            self.source_job,
            self.codec_job,
            self.hdr_format_job,
            self.tags_job,
            self.poster_job,
            self.trailer_job,
            self.season_job,
            self.automerge_group_job,
            self.scene_check_job,

            # Background jobs
            self.create_torrent_job,
            self.mediainfo_job,
            self.screenshots_job,
            self.upload_screenshots_job,
            self.description_job,
        )

    @property
    def isolated_jobs(self):
        """
        Sequence of job attribute names (e.g. "description_job") that were
        singled out by the user, e.g. with --only-description
        """
        if self.options.get('only_description', False):
            return self.get_job_and_dependencies(
                self.description_job,
                # `screenshots_job` is needed by `upload_screenshots_job`, but
                # `upload_screenshots_job` is a `QueueJobBase`, which doesn't
                # know anything about the job it gets input from and therefore
                # can't tells us that it needs `screenshots_job`.
                self.screenshots_job,
            )
        else:
            # Activate all jobs in jobs_before/after_upload
            return ()

    @functools.cached_property
    def type_job(self):
        return jobs.dialog.ChoiceJob(
            name=self.get_job_name('type'),
            label='Type',
            precondition=self.make_precondition('type_job'),
            prejobs=(
                self.imdb_job,
            ),
            autodetect=self.autodetect_type,
            autofinish=True,
            options=(
                ('Movie', '0'),
                # ("Music", '1'),  # Not supported
                ('TV', '2'),
            ),
            **self.common_job_args(ignore_cache=True),
        )

    async def autodetect_type(self, _):
        assert self.imdb_job.is_finished, self.imdb_job
        if self.imdb_job.output:
            type = await self.imdb.type(self.imdb_id)
            if type is utils.release.ReleaseType.movie:
                return 'Movie'
            elif type in (
                    utils.release.ReleaseType.season,
                    utils.release.ReleaseType.episode,
            ):
                return 'TV'

    @property
    def user_confirmed_type(self):
        # Get type from type_job, which got its type from imdb_job, which is
        # guaranteed to be correct because we asked the user.
        if self.type_job.is_finished and self.type_job.output:
            text = self.type_job.output[0]
            return {
                'Movie': utils.release.ReleaseType.movie,
                'TV': utils.release.ReleaseType.season,
            }[text]

    @functools.cached_property
    def year_job(self):
        return jobs.dialog.TextFieldJob(
            name=self.get_job_name('year'),
            label='Year',
            precondition=self.make_precondition('year_job'),
            prejobs=(
                self.imdb_job,
            ),
            text=self.autodetect_year,
            nonfatal_exceptions=(
                errors.RequestError,
            ),
            normalizer=self.normalize_year,
            validator=self.validate_year,
            finish_on_success=True,
            **self.common_job_args(),
        )

    async def autodetect_year(self):
        assert self.imdb_job.is_finished

        json = await self._tracker.get_uhd_info(self.imdb_id)
        year = json.get('year', None)
        _log.debug('Autodetected UHD year: %r', year)
        if year:
            return year

        year = await self.imdb.year(self.imdb_id)
        if year:
            _log.debug('Autodetected IMDb year: %r', year)
            return year

    def normalize_year(self, text):
        return text.strip()

    def validate_year(self, text):
        if not text:
            raise ValueError('Year must not be empty.')
        try:
            year = int(text)
        except ValueError:
            raise ValueError('Year must be a number.')
        else:
            if not 1800 < year < datetime.now().year + 10:
                raise ValueError('Year is not reasonable.')

    @functools.cached_property
    def season_job(self):
        return jobs.dialog.TextFieldJob(
            name=self.get_job_name('season'),
            label='Season',
            precondition=self.make_precondition('season_job'),
            prejobs=(
                self.imdb_job,
                self.type_job,
            ),
            hidden=self.season_job_is_hidden,
            text=self.autodetect_season,
            normalizer=self.normalize_season,
            validator=self.validate_season,
            finish_on_success=True,
            **self.common_job_args(),
        )

    def season_job_is_hidden(self):
        return self.user_confirmed_type not in (
            utils.release.ReleaseType.season,
            utils.release.ReleaseType.episode,
        )

    async def autodetect_season(self):
        if self.user_confirmed_type in (
                utils.release.ReleaseType.season,
                utils.release.ReleaseType.episode,
        ):
            _log.debug('Autodetected season: %r', self.release_name.only_season)
            if self.release_name.only_season:
                return self.release_name.only_season
            else:
                return None
        else:
            # Empty string for movies. This finishes the job successfully.
            return ''

    def normalize_season(self, text):
        return text.strip()

    def validate_season(self, text):
        if text:
            try:
                season = int(text)
            except ValueError:
                raise ValueError('Season must be a number.')
            else:
                # NOTE: Season 0 is ok for pilots, specials, etc.
                if not 0 <= season <= 100:
                    raise ValueError('Season is not reasonable.')

    @property
    def season_number(self):
        output = self.get_job_output(self.season_job, slice=0, default=())
        if output and output[0]:
            return int(output[0])

    @functools.cached_property
    def quality_job(self):
        return jobs.dialog.ChoiceJob(
            name=self.get_job_name('quality'),
            label='Quality',
            precondition=self.make_precondition('quality_job'),
            autodetect=self.autodetect_quality,
            autofinish=True,
            options=(
                ('mHD', 'mHD'),
                ('720p', '720p'),
                ('1080p', '1080p'),
                ('1080i', '1080i'),
                ('2160p', '2160p'),
                ('Other', 'Others'),
            ),
            **self.common_job_args(),
        )

    async def autodetect_quality(self, _):
        resolution = utils.video.resolution(self.content_path)
        _log.debug('Autodetecting quality: %s', resolution)
        if resolution in ('2160p', '1080i', '1080p', '720p'):
            return resolution
        else:
            return 'Other'

    @functools.cached_property
    def version_job(self):
        return jobs.custom.CustomJob(
            name=self.get_job_name('version'),
            label='Version',
            precondition=self.make_precondition('version_job'),
            worker=self.autodetect_version,
            # Non-special releases produce no output, which is not an error.
            no_output_is_ok=True,
            **self.common_job_args(ignore_cache=True),
        )

    async def autodetect_version(self, _):
        versions = set()
        for version, is_version in self.version_map.items():
            if not is_version:
                _log.debug('Unsupported autodetection for %r', version)
            elif is_version(self.release_name):
                _log.debug('Autodetected version: %r', version)
                versions.add(version)
        return versions

    version_map = {
        "Director's Cut": lambda release: "Director's Cut" in release.edition,
        'Theatrical': lambda release: 'Theatrical Cut' in release.edition,
        'Extended': lambda release: 'Extended Cut' in release.edition,
        'IMAX': lambda release: 'IMAX' in release.edition,
        'Uncut': lambda release: 'Uncut' in release.edition,
        'TV Cut': None,  # Unsupported
        'Unrated': lambda release: 'Unrated' in release.edition,
        'Remastered': lambda release: 'Remastered' in release.edition,
        '4K Remaster': lambda release: '4k Remastered' in release.edition,
        '4K Restoration': lambda release: '4k Restored' in release.edition,
        'B&W Version': None,  # Unsupported
        'Criterion': lambda release: 'Criterion Collection' in release.edition,
        '2in1': lambda release: '2in1' in release.edition,
        '3in1': lambda release: '3in1' in release.edition,
        'Hybrid': lambda release: 'Hybrid' in release.source,
        '10-bit': lambda release: utils.video.bit_depth(release.path, default=None) == 10,
        'Extras': None,  # Unsupported
    }

    # On the website, this is called "Media".
    @functools.cached_property
    def source_job(self):
        return jobs.dialog.ChoiceJob(
            name=self.get_job_name('source'),
            label='Source',
            precondition=self.make_precondition('source_job'),
            autodetect=self.autodetect_source,
            autofinish=True,
            options=(
                ('Blu-ray', 'Blu-ray'),
                ('Remux', 'Remux'),
                ('Encode', 'Encode'),
                ('WEB-DL', 'WEB-DL'),
                ('WEBRip', 'WEBRip'),
                ('HDRip', 'HDRip'),
                ('HDTV', 'HDTV'),
                ('Other', 'Others'),
            ),
            **self.common_job_args(ignore_cache=True),
        )

    async def autodetect_source(self, _):
        for source, is_source in self.source_map.items():
            if is_source(self.release_name):
                _log.debug('Autodetected source: %r', source)
                return source

    source_map = {
        'Encode': lambda release: any(
            source in release.source
            for source in (
                'BluRay',
                'HD-DVD',
            )),
        'WEB-DL': lambda release: 'WEB-DL' in release.source,
        'WEBRip': lambda release: 'WEBRip' in release.source,
        'HDTV': lambda release: 'HDTV' in release.source,
        # Not sure what "HDRip" is exactly and how to detect it.
        'HDRip': lambda release: 'Rip' in release.source,
    }

    @functools.cached_property
    def codec_job(self):
        return jobs.dialog.ChoiceJob(
            name=self.get_job_name('codec'),
            label='Codec',
            precondition=self.make_precondition('codec_job'),
            autodetect=self.autodetect_codec,
            autofinish=True,
            options=(
                ('x264', 'x264'),
                ('x265', 'x265'),
                ('x266', 'x266'),
                ('H.264', 'H.264'),  # AVC aka H.264
                ('H.265', 'HEVC'),   # HEVC aka H.265
                ('AV1', 'AV1'),
                ('VC-1', 'VC-1'),
                ('MPEG-2', 'MPEG-2'),
            ),
            **self.common_job_args(ignore_cache=True),
        )

    async def autodetect_codec(self, _):
        for codec, is_codec in self.codec_map.items():
            if is_codec(self.release_name):
                _log.debug('Autodetected video codec: %r', codec)
                return codec

    codec_map = {
        # TODO: Add support for commented-out codecs in utils.video and ReleaseName.
        'x264': lambda release: release.video_format == 'x264',
        'x265': lambda release: release.video_format == 'x265',
        # 'x266': lambda release: release.video_format == 'x266',
        'H.264': lambda release: release.video_format == 'H.264',
        'H.265': lambda release: release.video_format == 'H.265',
        # 'AV1': lambda release: release.video_format == 'AV1',
        # 'VC-1': lambda release: release.video_format == 'VC-1',
        # 'MPEG-2': lambda release: release.video_format == 'MPEG-2',
    }

    @functools.cached_property
    def hdr_format_job(self):
        return jobs.dialog.ChoiceJob(
            name=self.get_job_name('hdr-format'),
            label='HDR',
            precondition=self.make_precondition('hdr_format_job'),
            autodetect=self.autodetect_hdr_format,
            autofinish=True,
            options=(
                ('No', 'No'),
                ('HDR10', 'HDR10'),
                ('HDR10+', 'HDR10+'),
                ('Dolby Vision', 'DoVi'),
            ),
            **self.common_job_args(),
        )

    async def autodetect_hdr_format(self, _):
        for hdr_format, is_hdr_format in self.hdr_format_map.items():
            if is_hdr_format(self.release_name):
                _log.debug('Autodetected HDR format: %r', hdr_format)
                return hdr_format

    hdr_format_map = {
        'No': lambda release: release.hdr_format == '',
        'HDR10': lambda release: release.hdr_format == 'HDR10',
        'HDR10+': lambda release: release.hdr_format == 'HDR10+',
        'Dolby Vision': lambda release: release.hdr_format == 'DV',
    }

    @functools.cached_property
    def tags_job(self):
        return jobs.dialog.TextFieldJob(
            name=self.get_job_name('tags'),
            label='Tags',
            precondition=self.make_precondition('tags_job'),
            prejobs=(
                self.imdb_job,
            ),
            text=self.autodetect_tags,
            nonfatal_exceptions=(
                errors.RequestError,
            ),
            finish_on_success=True,
            normalizer=self.normalize_tags,
            validator=self.validate_tags,
            **self.common_job_args(),
        )

    async def autodetect_tags(self):
        json = await self._tracker.get_uhd_info(self.imdb_id)
        # Tags are comma-separated and may contain entities like "&eacute;". We
        # split them to a list. Keep in mind that the tags may be an empty
        # string, and `"".split(",")` returns `[""]`.
        return utils.html.as_text(json.get('tag', ''))

    max_tags_length = 200

    def normalize_tags(self, text):
        # Remove whitespace around tags and empty tags,
        seq = list(
            tag.strip()
            # Deduplicate while maintaining order.
            for tag in dict.fromkeys(text.split(','))
            if tag.strip()
        )

        # Ensure maximum length of `max_tag_length`.
        while seq and len(','.join(seq)) > self.max_tags_length:
            del seq[-1]
        return '\n'.join(seq)

    min_tags_count = 3

    def validate_tags(self, text):
        seq = [tag for tag in text.split('\n') if tag]
        if len(seq) < self.min_tags_count:
            raise ValueError(f'At least {self.min_tags_count} tags are required.')

    async def get_poster_from_tracker(self):
        await self.imdb_job.wait()
        json = await self._tracker.get_uhd_info(self.imdb_id)
        poster = json.get('photo', None)
        _log.debug('Poster from UHD: %r', poster)
        if poster:
            return {
                'poster': poster,
                'width': None,
                'height': None,
                'imghosts': (),
                'write_to': None,
            }

    @functools.cached_property
    def trailer_job(self):
        return jobs.dialog.TextFieldJob(
            name=self.get_job_name('trailer'),
            label='Trailer',
            precondition=self.make_precondition('trailer_job'),
            prejobs=(
                self.imdb_job,
            ),
            text=self.autodetect_trailer,
            nonfatal_exceptions=(
                errors.RequestError,
            ),
            normalizer=self.normalize_trailer,
            validator=self.validate_trailer,
            finish_on_success=True,
            **self.common_job_args(ignore_cache=bool('trailer' in self.options)),
        )

    async def autodetect_trailer(self):
        # Get trailer from user.
        if self.options.get('trailer', ''):
            return self.options['trailer']

        # Get trailer from UHD.
        assert self.imdb_job.is_finished
        json = await self._tracker.get_uhd_info(self.imdb_id)
        trailer_id = json.get('trailer', None)
        if trailer_id:
            return trailer_id

        # Default to no trailer.
        return ''

    def normalize_trailer(self, text):
        try:
            return 'https://youtu.be/' + self.get_youtube_id(text)
        except ValueError:
            # Keep invalid URL so the user can fix it.
            return text

    def validate_trailer(self, text):
        if text:
            # Raise ValueError if no YouTube ID is found.
            self.get_youtube_id(text)

    _YOUTUBE_ID_NO_DEFAULT = object()

    def get_youtube_id(self, url, default=_YOUTUBE_ID_NO_DEFAULT):
        """
        Find YouTube video ID in `url`

        :param url: Any YouTube URL
        :param default: Return value if no YouTube ID can be found in `url`

            If not provided, raise :class:`ValueError` if no YouTube ID can be
            found in `url`.
        """
        url_ = urllib.parse.urlparse(url)
        if not url_.hostname:
            if re.search(r'^([a-zA-Z0-9_-]+)$', url):
                return url
        elif re.search(r'youtu(?:be|)\.[a-z]{2,3}', url_.hostname):
            if match := re.search(r'\bv=([a-zA-Z0-9_-]+)\b', url_.query):
                return match.group(1)
            elif match := re.search(r'^/(?:embed/|v/|watch/|)([a-zA-Z0-9_-]+)$', url_.path):
                return match.group(1)

        if default is self._YOUTUBE_ID_NO_DEFAULT:
            raise ValueError('Not a YouTube ID or URL.')
        else:
            return default

    @functools.cached_property
    def description_job(self):
        return jobs.dialog.TextFieldJob(
            name=self.get_job_name('description'),
            label='Description',
            precondition=self.make_precondition('description_job'),
            prejobs=(
                self.upload_screenshots_job,
                self.mediainfo_job,
            ),
            text=self.generate_description,
            hidden=True,
            finish_on_success=True,
            read_only=True,
            **self.common_job_args(ignore_cache=True),
        )

    image_host_config = {
        'common': {'thumb_width': 350},
    }

    def generate_description(self):
        screenshots = self.generate_description_screenshots()
        mediainfo = self.generate_description_mediainfo()
        nfo = self.generate_description_nfo()
        promotion = (
            '[align=right][size=1]'
            f'Shared with [url={__homepage__}]{__project_name__}[/url]'
            '[/size][/align]'
        )
        parts = (
            f'{mediainfo}',
            f'\n\n{nfo}' if nfo else '',
            f'\n\n[center]{screenshots}[/center]',
            f'\n{promotion}',
        )
        return ''.join(part for part in parts if part)

    def generate_description_screenshots(self):
        assert self.upload_screenshots_job.is_finished
        return self.make_screenshots_grid(
            screenshots=self.upload_screenshots_job.uploaded_images,
            columns=2,
            horizontal_spacer='   ',
            vertical_spacer='\n\n',
        )

    def generate_description_mediainfo(self):
        assert self.mediainfo_job.is_finished
        assert self.mediainfo_job.output, self.mediainfo_job.output
        mediainfo = self.mediainfo_job.output[0]
        return (
            '[spoiler=Mediainfo]'
            + '[code]'
            + mediainfo.strip()
            + '[/code]'
            + '[/spoiler]'
        )

    def generate_description_nfo(self):
        nfo = self.read_nfo(strip=True)
        if nfo:
            return (
                '[spoiler=NFO]'
                + '[code]'
                + nfo
                + '[/code]'
                + '[/spoiler]'
            )

    @functools.cached_property
    def automerge_group_job(self):
        return jobs.dialog.ChoiceJob(
            name=self.get_job_name('automerge-group'),
            label='Automerge Group',
            precondition=self.make_precondition('automerge_group_job'),
            prejobs=(
                self.imdb_job,
                self.type_job,
                self.season_job,
            ),
            autodetect=self.autodetect_automerge_group,
            autofinish=True,
            options=(
                ('Yes', True),
                ('No', False),
            ),
            **self.common_job_args(ignore_cache=True),
        )

    async def autodetect_automerge_group(self, _):
        assert self.season_job.is_finished
        if self.season_number is not None:
            # All TV seasons share the same IMDB ID, but they are grouped by season
            # number. From the Uploading Guide v2 in the wiki:
            # > Auto-Merge should always be selected unless you are uploading a
            # > TV season that doesn't have a torrent group yet.
            # https://uhdbits.org/wiki.php?action=article&id=33
            #
            # This implementation searches for the IMDb ID and tries to find a
            # group named ".* Season \d+" in the returned HTML.
            season_group_names = await self._get_season_group_names()
            target_group_name_suffix = f'Season {self.season_number:02d}'.lower()
            for group_name in season_group_names:
                # Example season group names:
                #  - The Title
                #  - The Title Season 03
                #  - The Title Season 03 / The AKA Title
                if re.search(rf'\s+{target_group_name_suffix}\b', group_name):
                    _log.debug('Found existing season group: %r', group_name)
                    return 'Yes'
                else:
                    _log.debug('Existing season group does not match %r: %r',
                               target_group_name_suffix, group_name)

            # Looks like season group doesn't exist yet.
            return 'No'
        else:
            # Movies are always autogrouped by IMDb ID
            return 'Yes'

    async def _get_season_group_names(self):
        await self._tracker.login()
        response = await self._tracker._request(
            method='GET',
            url=self._tracker._torrents_url,
            params={
                'searchstr': self.imdb_id,
            },
            error_prefix='Automerge group check failed',
        )

        group_names = []
        doc = utils.html.parse(response)
        for tag in doc.find_all('a', {'class': 'torrent_name'}):
            group_name = utils.html.as_text(tag).strip()
            group_names.append(unidecode.unidecode(group_name.lower()))
        _log.debug('Existing season groups: %r', group_names)
        return group_names

    release_name_translation = {
        'group': {
            re.compile(r'^NOGROUP$'): 'Unknown',
        },
    }

    @property
    def post_data(self):
        return {
            'submit': 'true',

            # Type ("0" for Movie, "2" for TV)
            'type': self.get_job_attribute(self.type_job, 'choice'),

            # IMDb ID ("tt...")
            'imdbid': self.get_job_output(self.imdb_job, slice=0),

            # Original title
            'title': self.release_name.title,

            # English title
            'OtherTitle': self.release_name.title_aka,

            # Uploading Guide v2 says: "Disregard this field"
            'smalldesc': '',

            # Year
            'year': self.get_job_output(self.year_job, slice=0),

            # Season number or `None` (i.e. no submission of "season") for movie
            'season': self.season_number,

            # Quality (e.g. "1080p")
            'format': self.get_job_output(self.quality_job, slice=0),

            # Group
            'team': self.release_name.group,

            # Version (e.g. "Director's Cut")
            'Version': ' / '.join(self.get_job_output(self.version_job)),

            # Source ("Media" on the website) (e.g. "BluRay")
            'media': self.get_job_output(self.source_job, slice=0),

            # Codec (e.g. "x264")
            'codec': self.get_job_output(self.codec_job, slice=0),

            # HDR format (e.g. "HDR10" or "DoVi")
            'hdr': self.get_job_output(self.hdr_format_job, slice=0),

            # "genre_tags" is a side-effect of the dropdown list that lets the
            # user pick tags. This is probably ignored by the server, but we
            # keep it to reduce the bug surface.
            'genre_tags': '---',

            # Tags (We list them one per line for readability, but the server
            # wants them separated by commas.)
            'tags': ','.join(self.get_job_output(self.tags_job, slice=0).split('\n')),

            # Poster URL
            'image': self.get_job_output(self.poster_job, slice=0),

            # Trailer (YouTube ID)
            'trailer': self.get_youtube_id(
                self.get_job_output(self.trailer_job, slice=0),
                default='',
            ),

            # Mediainfo
            'mediainfo': self.get_job_output(self.mediainfo_job, slice=0),

            # Screenshots and release info
            'release_desc': self.get_job_output(self.description_job, slice=0),

            # Group with anything that has the same IMDB ID
            'auto_merge_group': (
                'on'
                if self.get_job_attribute(self.automerge_group_job, 'choice') else
                None
            ),

            # Internal release
            'internal': 'on' if self.options['internal'] else None,

            # No support for exclusive releases (this is intentional)
            # 'exclude': '0',

            # 3D version
            'd3d': '1' if self.options['3d'] else None,

            # Release contains Vietnamese Audio dub
            'vie': '1' if self.options['vie'] else None,

            # Scene release
            'scene': '1' if self.get_job_attribute(self.scene_check_job, 'is_scene_release') else None,

            # Upload anonymously
            'anonymous': '1' if self.options['anonymous'] else None,
        }

    @property
    def post_files(self):
        return {
            'file_input': {
                'file': self.torrent_filepath,
                'mimetype': 'application/x-bittorrent',
            },
        }
