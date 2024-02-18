"""
Upload images to image hosting services
"""

from .. import errors, utils
from ..utils.imghosts import ImageHostBase
from . import QueueJobBase

import logging  # isort:skip
_log = logging.getLogger(__name__)


class ImageHostJob(QueueJobBase):
    """Upload images to an image hosting service"""

    name = 'imghost'
    label = 'Image URLs'

    # Don't cache output and rely on caching in ImageHostBase. Otherwise, a
    # single failed/cancelled upload would throw away all the gathered URLs
    # because nothing is cached if a job fails.
    cache_id = None

    def initialize(self, *, imghosts, images_total=0, enqueue=()):
        """
        Validate arguments and set internal state

        :param imghosts: Sequence of :class:`ImageHostBase` subclass instances
            (see :func:`.utils.imghosts.imghost`)
        :param enqueue: Sequence of image paths (see
            :class:`~.base.QueueJobBase`)
        :param images_total: Number of images that are going to be uploaded. The
            only purpose of this value is to provide it via the :attr:`images_total`
            property to calculate progress.

        If `enqueue` is given, the job finishes after all images are uploaded.

        If `enqueue` is not given, calls to :meth:`upload` are expected and
        :meth:`~.QueueJobBase.close` must be called after the last call.

        `enqueue` and `images_total` must not be given at the same time.
        """
        if enqueue and images_total:
            raise RuntimeError('You must not give both arguments "enqueue" and "images_total".')
        else:
            for imghost in imghosts:
                assert isinstance(imghost, ImageHostBase), f'Not an ImageHostBase: {imghost!r}'
                # Force image hosts to cache image URLs in our cache directory
                imghost.cache_directory = self.cache_directory

            self._imghosts = imghosts
            self._uploaded_images = []
            self._urls_by_file = {}
            if images_total > 0:
                self.images_total = images_total
            else:
                self.images_total = len(enqueue)

    async def handle_input(self, image_path):
        if len(self._imghosts) <= 1:
            await self._upload_to_one(image_path)
        else:
            await self._upload_to_any(image_path)

    async def _upload_to_one(self, image_path):
        # Upload to 1 or 0 image hosts and error out immediately if that fails.
        for imghost in self._imghosts:
            try:
                await self._upload(image_path, imghost)
            except errors.RequestError as e:
                self.error(f'{imghost.name}: Upload failed: {utils.fs.basename(image_path)}: {e}')

    async def _upload_to_any(self, image_path):
        # Try each image host and stop on first successful upload.
        # Only warn about upload failures.
        fail = False
        for imghost in self._imghosts:
            try:
                await self._upload(image_path, imghost)
            except errors.RequestError as e:
                _log.debug('Failed to upload %s to %s: %r', image_path, imghost.name, e)
                self.warn(f'{imghost.name}: Upload failed: {utils.fs.basename(image_path)}: {e}')
                fail = True
            else:
                fail = False
                break
        if fail:
            self.error('All upload attempts failed.')

    async def _upload(self, image_path, imghost):
        info = await imghost.upload(image_path, cache=not self.ignore_cache)
        _log.debug('Uploaded image: %r', info)
        self._uploaded_images.append(info)
        self._urls_by_file[image_path] = info
        image_url = str(info)
        self.send(image_url)

    @property
    def exit_code(self):
        """`0` if all images were uploaded, `1` otherwise, `None` if unfinished"""
        if self.is_finished:
            if self.images_uploaded > 0 and self.images_uploaded == self.images_total:
                return 0
            else:
                return 1

    @property
    def uploaded_images(self):
        """
        Sequence of :class:`~.imghosts.common.UploadedImage` objects

        Use this property to get additional information like thumbnail URLs that
        are not part of this job's :attr:`~.base.JobBase.output`.
        """
        return tuple(self._uploaded_images)

    @property
    def urls_by_file(self):
        """Mapping of image file paths to image URLs"""
        return self._urls_by_file.copy()

    @property
    def images_uploaded(self):
        """Number of uploaded images"""
        return len(self._uploaded_images)

    @property
    def images_total(self):
        """Expected number of images to upload"""
        return self._images_total

    @images_total.setter
    def images_total(self, value):
        self._images_total = int(value)

    def set_images_total(self, value):
        """:attr:`images_total` setter as a method"""
        self.images_total = value
