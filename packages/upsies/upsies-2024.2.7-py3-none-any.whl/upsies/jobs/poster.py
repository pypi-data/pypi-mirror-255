"""
Find, download and re-upload poster for movie, series or season
"""

import collections
import hashlib
import os
import re
import urllib.parse

import async_lru

from .. import errors, utils
from . import JobBase

import logging  # isort:skip
_log = logging.getLogger(__name__)


class PosterJob(JobBase):
    """
    Get poster and optionally resize and reupload it
    """

    name = 'poster'
    label = 'Poster'

    # Caching is done by utilities.
    cache_id = None

    def initialize(self, *, getter, width=None, height=None, write_to=None, imghosts=()):
        """
        Set internal state

        :param getter: Coroutine function that returns a poster file or
                       poster URL (e.g. :meth:`.WebDbApiBase.poster_url`).
                       May raise :class:`~.RequestError`, which is passed
                       to :meth:`~.JobBase.error`.
        :param width: Resize poster to this many pixels wide (aspect ratio
                      is always maintained)
        :param height: Resize poster to this many pixels high (aspect
                       ratio always is maintained)
        :param imghosts: Upload poster to the first image hosting service in
                         this sequence of :class:`~.ImageHostBase` subclasses
                         and try the next one if this fails.
                         :class:`~.RequestError` from uploading is passed to
                         :meth:`~.JobBase.warn`. If all uploads fail,
                         :meth:`error` is called.
        :param write_to: Write poster to this file path (may be `None` or
                         empty string)
        """
        self._getter = getter
        self._width = width
        self._height = height
        self._write_to = write_to
        self._imghosts = imghosts

        self.signal.add('obtaining')
        self.signal.add('obtained')
        self.signal.add('downloading')
        self.signal.add('downloaded')
        self.signal.add('resizing')
        self.signal.add('resized')
        self.signal.add('uploading')
        self.signal.add('uploaded')

    _url_regex = re.compile(r'^https?://.+', flags=re.IGNORECASE)

    class _ProcessingError(errors.UpsiesError):
        pass

    async def run(self):
        try:
            params = await self._obtain()
            poster = params['poster']
            width = params.get('width', self._width)
            height = params.get('height', self._height)
            write_to = params.get('write_to', self._write_to)
            imghosts = params.get('imghosts', self._imghosts)

            poster = await self._resize(poster, width, height)
            await self._write(poster, write_to)
            await self._upload(poster, imghosts)

            if not write_to and not imghosts:
                if width or height:
                    await self._write(poster, self._get_poster_filename(poster))
                else:
                    self.send(poster)

        except self._ProcessingError as e:
            self.error(e)

    async def _obtain(self):
        _log.debug('Obtaining poster: %r', self._getter)
        self.signal.emit('obtaining')
        try:
            params_or_poster = await self._getter()
        except errors.RequestError as e:
            raise self._ProcessingError(f'Failed to get poster: {e}')
        else:
            _log.debug('Obtained poster: %r', params_or_poster)
            if not params_or_poster:
                raise self._ProcessingError('No poster found')
            elif isinstance(params_or_poster, collections.abc.Mapping):
                params = params_or_poster
            else:
                params = {'poster': params_or_poster}

            self.signal.emit('obtained', params['poster'])
            return params

    async def _resize(self, poster, width, height):
        if width or height:
            _log.debug('Resizing poster to %s x %s: %r', width, height, poster)

            # Download the poster so we can resize it.
            filepath = await self._get_poster_filepath(poster)
            filename_resized = '.'.join((
                utils.fs.basename(utils.fs.strip_extension(filepath)),
                f'{width}x{height}',
                utils.fs.file_extension(filepath),
            ))

            self.signal.emit('resizing', filepath)
            try:
                filepath_resized = utils.image.resize(
                    filepath,
                    target_directory=self.cache_directory,
                    target_filename=filename_resized,
                    width=width,
                    height=height,
                )
            except errors.ImageResizeError as e:
                raise self._ProcessingError(f'Failed to resize poster: {e}')
            else:
                self.signal.emit('resized', filepath_resized)
                return filepath_resized
        else:
            # Return original poster file or URL.
            return poster

    async def _write(self, poster, filepath):
        if filepath:
            # Write poster file or URL to user-provided path.
            _log.debug('Writing poster: %r', (poster, filepath))
            data = await self._read_file_or_url(poster)
            filepath = await self._write_file(data, filepath)
            self.send(filepath)

    async def _upload(self, poster, imghosts):
        if imghosts:
            # If poster is a URL, we must download it first.
            filepath = await self._get_poster_filepath(poster)

            # Upload `filepath` to any `imghost` and return the URL of the first
            # successful upload.
            for imghost in imghosts:
                _log.debug('Uploading poster: %r', (filepath, imghost.name))
                self.signal.emit('uploading', imghost)
                try:
                    url = await imghost.upload(filepath, thumb_width=0)
                except errors.RequestError as e:
                    self.warn(f'Failed to upload poster: {e}')
                else:
                    self.signal.emit('uploaded', url)
                    self.send(url)
                    return

            # If all upload() calls failed, add an error to all the warnings.
            raise self._ProcessingError('All uploads failed')

    @async_lru.alru_cache
    async def _get_poster_filepath(self, poster):
        if self._url_regex.search(poster):
            # Download poster URL to temporary file and return its path.
            data = await self._read_file_or_url(poster)
            filepath = os.path.join(
                self.cache_directory,
                self._get_poster_filename(poster),
            )
            return await self._write_file(data, filepath)

        else:
            # Return original poster file path.
            return poster

    def _get_poster_filename(self, poster):
        if self._url_regex.search(poster):
            # Turn poster URL into unique file name.
            url = urllib.parse.urlparse(poster)
            unique_id = hashlib.md5(
                '.'.join((url.path, url.query))
                .encode('utf8')
            ).hexdigest()
            filename = 'poster:' + '.'.join((
                url.hostname,
                unique_id,
            ))
            extension = utils.fs.file_extension(url.path)
            if extension:
                filename += f'.{extension}'
            return filename
        else:
            # Get poster file name from poster file path.
            return utils.fs.basename(poster)

    async def _read_file_or_url(self, poster):
        if self._url_regex.search(poster):
            # Return downloaded data from URL.
            _log.debug('Downloading poster: %r', poster)
            try:
                self.signal.emit('downloading', poster)
                response = await utils.http.get(poster, cache=True)
            except errors.RequestError as e:
                raise self._ProcessingError(f'Failed to download poster: {e}')
            else:
                self.signal.emit('downloaded', poster)
                return response.bytes

        else:
            # Return poster file content.
            _log.debug('Reading poster: %r', poster)
            try:
                with open(poster, 'rb') as f:
                    return f.read()
            except OSError as e:
                msg = e.strerror if e.strerror else str(e)
                raise self._ProcessingError(f'Failed to read poster: {msg}')

    async def _write_file(self, data, filepath):
        # Write `data` to sanitized `filepath` and return sanitized `filepath`.
        filepath = utils.fs.sanitize_path(filepath)
        try:
            with open(filepath, 'wb') as f:
                f.write(data)
        except OSError as e:
            msg = e.strerror if e.strerror else str(e)
            raise self._ProcessingError(f'Failed to write {filepath}: {msg}')
        else:
            return filepath
