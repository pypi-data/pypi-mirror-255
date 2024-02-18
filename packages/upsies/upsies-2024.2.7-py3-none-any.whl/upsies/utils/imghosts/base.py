"""
Base class for image uploaders
"""

import abc
import copy
import glob
import hashlib
import os

from ... import __project_name__, constants, errors
from .. import configfiles, fs, image
from . import common

import logging  # isort:skip
_log = logging.getLogger(__name__)


class ImageHostBase(abc.ABC):
    """
    Base class for image uploaders

    :param str cache_directory: Where to cache URLs; defaults to
        :attr:`~upsies.constants.DEFAULT_CACHE_DIRECTORY`
    :param options: User configuration options for this image host,
        e.g. authentication details, thumbnail size, etc
    :type options: :class:`dict`-like
    """

    def __init__(self, cache_directory=None, options=None):
        self._options = copy.deepcopy(self.default_config)
        self._options.update()
        if options is not None:
            self._options.update(options)
        self._cache_dir = cache_directory if cache_directory else constants.DEFAULT_CACHE_DIRECTORY

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # This method is called for each subclass. This hack allows us to
        # overload `default_config` in subclasses without caring about common
        # defaults, e.g. subclasses don't need to have "thumb_width" in their
        # `default_config`, but it will exist anyway.
        cls.default_config = {
            **cls.default_config_common,
            **cls.default_config,
        }

    @property
    @abc.abstractmethod
    def name(self):
        """Name of the image hosting service"""

    @property
    def cache_directory(self):
        """Path to directory where upload info is cached"""
        return self._cache_dir

    @cache_directory.setter
    def cache_directory(self, directory):
        self._cache_dir = directory

    @property
    def options(self):
        """
        Configuration options provided by the user

        This is the :class:`dict`-like object from the initialization argument
        of the same name.
        """
        return self._options

    default_config_common = {
        'thumb_width': configfiles.config_value(
            value=0,
            description=(
                'Thumbnail width in pixels or 0 for no thumbnail. '
                'Trackers may ignore this option and use a hardcoded thumbnail width.'
            ),
        ),
    }
    """Default user configuration for all subclasses"""

    default_config = {}
    """
    Default user configuration for a subclass

    Thanks to some magic, this is always an extension of :attr:`default_config_common`.
    """

    argument_definitions = {}
    """CLI argument definitions (see :attr:`.CommandBase.argument_definitions`)"""

    description = ''
    """Any documentation, for example how to get an API key"""

    async def upload(self, image_path, thumb_width=None, cache=True):
        """
        Upload image file

        :param image_path: Path to image file
        :param int thumb_width: Override ``thumb_width`` in :attr:`options`

            If set to 0, no thumbnail is uploaded.
        :param bool cache: Whether to attempt to get the image URL from cache

        :raise RequestError: if the upload fails

        :return: :class:`~.imghost.common.UploadedImage`
        """
        if 'apikey' in self.options and not self.options['apikey']:
            raise errors.RequestError(
                'You must configure an API key first. Run '
                f'"{__project_name__} upload-images {self.name} --help" '
                'for more information.'
            )

        info = {
            'url': await self._get_image_url(image_path, cache=cache),
        }

        if thumb_width is None:
            thumb_width = self.options['thumb_width']
        if thumb_width:
            try:
                thumbnail_path = image.resize(
                    image_path,
                    width=thumb_width,
                    target_directory=self.cache_directory,
                    overwrite=not cache,
                )
            except errors.ImageResizeError as e:
                raise errors.RequestError(e)
            else:
                info['thumbnail_url'] = await self._get_image_url(thumbnail_path, cache=cache)

        return common.UploadedImage(**info)

    async def _get_image_url(self, image_path, cache=True):
        url = self._get_url_from_cache(image_path) if cache else None
        if not url:
            url = await self._upload_image(image_path)
            _log.debug('Uploaded %r: %r', image_path, url)
            self._store_url_to_cache(image_path, url)
        else:
            _log.debug('Got URL from cache: %r: %r', image_path, url)
        return url

    @abc.abstractmethod
    async def _upload_image(self, image_path):
        """Upload `image_path` and return URL to the image file"""

    def _get_url_from_cache(self, image_path):
        cache_file_suffix = self._get_cache_file_suffix(image_path)
        cache_file_glob = os.path.join(
            glob.escape(self.cache_directory),
            f'*.{cache_file_suffix}',
        )
        matching_cache_files = glob.glob(cache_file_glob)

        if matching_cache_files:
            cache_file = matching_cache_files[0]
            _log.debug('Already uploaded: %s', cache_file)
            try:
                with open(cache_file, 'r') as f:
                    return f.read().strip()
            except OSError:
                # Unreadable cache file. we'll try to overwrite it later.
                pass

    def _store_url_to_cache(self, image_path, url):
        # Use file name for easier debugging.
        stem = fs.basename(image_path)
        extension = self._get_cache_file_suffix(image_path)

        # Max file name length is usually 255 bytes
        max_filename_length = 250 - len(extension)
        filename = f'{stem}.{extension}'
        cache_file = os.path.join(self.cache_directory, filename[-max_filename_length:])

        try:
            fs.mkdir(fs.dirname(cache_file))
            with open(cache_file, 'w') as f:
                f.write(url)
        except (OSError, errors.ContentError) as e:
            msg = e.strerror if getattr(e, 'strerror', None) else e
            raise RuntimeError(f'Unable to write cache {cache_file}: {msg}')

    def _get_cache_file_suffix(self, image_path):
        try:
            # Generate unique ID from the first 10 KiB of image data.
            with open(image_path, 'rb') as f:
                unique_id = hashlib.md5(f.read(10 * 1024)).hexdigest()
        except OSError:
            # If `image_path` is not readable, get unique ID from the literal
            # file path.
            unique_id = hashlib.md5(image_path.encode('utf8')).hexdigest()
        return unique_id + f'.{self.name}.url'
