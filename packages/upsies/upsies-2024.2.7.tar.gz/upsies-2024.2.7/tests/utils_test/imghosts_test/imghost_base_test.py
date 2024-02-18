import copy
import hashlib
import random
import re
import sys
from unittest.mock import AsyncMock, Mock, PropertyMock, call

import pytest

from upsies import __project_name__, errors
from upsies.utils import imghosts


def make_TestImageHost(default_config=None, **kwargs):
    # Avoid NameError bug (https://github.com/python/cpython/issues/87546)
    default_config_ = default_config

    class TestImageHost(imghosts.ImageHostBase):
        name = 'imgw00t'
        default_config = default_config_ or {}

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._upload_image_mock = AsyncMock()

        async def _upload_image(self, image_path):
            return await self._upload_image_mock(image_path)

    return TestImageHost(**kwargs)


def test_cache_directory_property(mocker, tmp_path):
    mocker.patch('upsies.constants.DEFAULT_CACHE_DIRECTORY', 'mock/cache/path')
    imghost = make_TestImageHost()
    assert imghost.cache_directory == 'mock/cache/path'
    imghost = make_TestImageHost(cache_directory=tmp_path)
    assert imghost.cache_directory is tmp_path
    imghost.cache_directory = 'path/to/foo'
    assert imghost.cache_directory == 'path/to/foo'


def test_default_config_without_custom_defaults():
    imghost = make_TestImageHost()
    default_config_common = copy.deepcopy(imghost.default_config_common)
    exp_default_config = {**default_config_common, **imghost.default_config}
    assert imghost.default_config == exp_default_config
    exp_options = {**imghost.default_config}
    assert imghost.options == exp_options
    assert imghost.default_config_common == default_config_common

def test_default_config_with_custom_defaults():
    imghost = make_TestImageHost(default_config={'foo': 1, 'bar': 2})
    default_config_common = copy.deepcopy(imghost.default_config_common)
    exp_default_config = {**default_config_common, **{'foo': 1, 'bar': 2}}
    assert imghost.default_config == exp_default_config
    exp_options = exp_default_config
    assert imghost.options == exp_options
    assert imghost.default_config_common == default_config_common

def test_default_config_with_custom_defaults_and_custom_options():
    imghost = make_TestImageHost(default_config={'foo': 1, 'bar': 2}, options={'foo': 1, 'bar': 99})
    default_config_common = copy.deepcopy(imghost.default_config_common)
    exp_default_config = {**default_config_common, **{'foo': 1, 'bar': 2}}
    assert imghost.default_config == exp_default_config
    exp_options = {**imghost.default_config, **{'foo': 1, 'bar': 99}}
    assert imghost.options == exp_options
    assert imghost.default_config_common == default_config_common

def test_default_config_with_overloaded_common_defaults():
    default_config_key = tuple(imghosts.ImageHostBase.default_config_common)[0]
    default_config = {default_config_key: 'foozbar'}
    imghost = make_TestImageHost(default_config=default_config)
    default_config_common = copy.deepcopy(imghost.default_config_common)
    exp_default_config = {**default_config_common, **{default_config_key: 'foozbar'}}
    assert imghost.default_config == exp_default_config
    exp_options = exp_default_config
    assert imghost.options == exp_options
    assert imghost.default_config_common == default_config_common


def test_options_property():
    imghost = make_TestImageHost()
    assert imghost.options == {'thumb_width': 0}
    imghost = make_TestImageHost(default_config={'foo': 1, 'bar': 2})
    assert imghost.options == {'thumb_width': 0, 'foo': 1, 'bar': 2}
    imghost = make_TestImageHost(default_config={'foo': 1, 'bar': 2}, options={'bar': 99})
    assert imghost.options == {'thumb_width': 0, 'foo': 1, 'bar': 99}


def test_description():
    imghost = make_TestImageHost()
    assert imghost.description == ''


@pytest.mark.parametrize(
    argnames='options, exp_exception',
    argvalues=(
        ({}, None),
        ({'apikey': 'd34db33f'}, None),
        ({'apikey': ''}, errors.RequestError(
            'You must configure an API key first. Run '
            f'"{__project_name__} upload-images {{name}} --help" '
            'for more information.'
        )),
    ),
)
@pytest.mark.asyncio
async def test_upload_checks_for_missing_apikey(options, exp_exception, mocker, tmp_path):
    resize_mock = mocker.patch('upsies.utils.image.resize')
    ih = make_TestImageHost(cache_directory=tmp_path, options=options)
    mocker.patch.object(ih, '_get_image_url', AsyncMock())
    if exp_exception is None:
        await ih.upload('foo.png')
        assert resize_mock.call_args_list == []
        assert ih._get_image_url.call_args_list == [call('foo.png', cache=True)]
    else:
        exp_error = str(exp_exception).format(name=ih.name)
        with pytest.raises(type(exp_exception), match=rf'{re.escape(exp_error)}$'):
            await ih.upload('foo.png')
        assert resize_mock.call_args_list == []
        assert ih._get_image_url.call_args_list == []


@pytest.mark.parametrize('cache', (True, False), ids=('cache=True', 'cache=False'))
@pytest.mark.parametrize('thumb_width', (0, 123), ids=lambda v: f'thumb_width={v}')
@pytest.mark.asyncio
async def test_upload_succeeds(thumb_width, cache, mocker, tmp_path):
    resize_mock = mocker.patch('upsies.utils.image.resize', return_value='thumbnail.png')

    ih = make_TestImageHost(cache_directory=tmp_path, options={'thumb_width': thumb_width})
    image_urls = ['https://localhost:123/foo.png']
    if thumb_width:
        image_urls.append('https://localhost:123/foo.thumb.png')
    mocker.patch.object(ih, '_get_image_url', AsyncMock(side_effect=image_urls))

    image = await ih.upload('path/to/foo.png', cache=cache)

    if thumb_width:
        assert resize_mock.call_args_list == [call(
            'path/to/foo.png',
            width=thumb_width,
            target_directory=ih.cache_directory,
            overwrite=not cache,
        )]
        assert ih._get_image_url.call_args_list == [
            call('path/to/foo.png', cache=cache),
            call(resize_mock.return_value, cache=cache),
        ]
    else:
        assert ih._get_image_url.call_args_list == [
            call('path/to/foo.png', cache=cache),
        ]

    assert isinstance(image, imghosts.UploadedImage)
    assert image == image_urls[0]
    if thumb_width:
        assert image.thumbnail_url == image_urls[1]
    else:
        assert image.thumbnail_url is None

@pytest.mark.parametrize(
    argnames='cache, resize_error, exp_request_error',
    argvalues=(
        (False, errors.ImageResizeError('not an image'), errors.RequestError('not an image')),
        (True, errors.ImageResizeError('not an image'), errors.RequestError('not an image')),
    ),
)
@pytest.mark.asyncio
async def test_upload_catches_ResizeError(cache, resize_error, exp_request_error, mocker, tmp_path):
    resize_mock = mocker.patch('upsies.utils.image.resize', side_effect=resize_error)

    ih = make_TestImageHost(cache_directory=tmp_path, options={'thumb_width': 345})
    image_urls = ['https://localhost:123/foo.png', 'https://localhost:123/foo.thumb.png']
    mocker.patch.object(ih, '_get_image_url', AsyncMock(side_effect=image_urls))

    with pytest.raises(type(exp_request_error), match=rf'^{re.escape(str(exp_request_error))}$'):
        await ih.upload('path/to/foo.png', cache=cache)

    assert resize_mock.call_args_list == [call(
        'path/to/foo.png',
        width=345,
        target_directory=ih.cache_directory,
        overwrite=not cache,
    )]
    assert ih._get_image_url.call_args_list == [
        call('path/to/foo.png', cache=cache),
    ]


@pytest.mark.asyncio
async def test_get_image_url_from_cache(mocker, tmp_path):
    ih = make_TestImageHost(cache_directory=tmp_path)
    mocker.patch.object(ih, '_upload_image', AsyncMock(return_value='http://localhost:123/uploaded.image.jpg'))
    mocker.patch.object(ih, '_get_url_from_cache', Mock(return_value='http://localhost:123/cached.image.jpg'))
    mocker.patch.object(ih, '_store_url_to_cache')
    url = await ih._get_image_url('path/to/image.jpg', cache=True)
    assert url == 'http://localhost:123/cached.image.jpg'
    assert ih._get_url_from_cache.call_args_list == [call('path/to/image.jpg')]
    assert ih._upload_image.call_args_list == []
    assert ih._store_url_to_cache.call_args_list == []

@pytest.mark.asyncio
async def test_get_image_url_from_upload(mocker, tmp_path):
    ih = make_TestImageHost(cache_directory=tmp_path)
    mocker.patch.object(ih, '_upload_image', AsyncMock(return_value='http://localhost:123/uploaded.image.jpg'))
    mocker.patch.object(ih, '_get_url_from_cache', Mock(return_value='http://localhost:123/cached.image.jpg'))
    mocker.patch.object(ih, '_store_url_to_cache')
    url = await ih._get_image_url('path/to/image.jpg', cache=False)
    assert url == 'http://localhost:123/uploaded.image.jpg'
    assert ih._get_url_from_cache.call_args_list == []
    assert ih._upload_image.call_args_list == [call('path/to/image.jpg')]
    assert ih._store_url_to_cache.call_args_list == [call(
        'path/to/image.jpg',
        'http://localhost:123/uploaded.image.jpg',
    )]


def test__get_url_from_cache_finds_no_cache_file(tmp_path, mocker):
    ih = make_TestImageHost(cache_directory=tmp_path)
    mocker.patch.object(ih, '_get_cache_file_suffix', return_value='d34db33f.foohost.url')
    image_path = 'some/path/to/foo.png'

    url = ih._get_url_from_cache(image_path)
    assert url is None
    assert ih._get_cache_file_suffix.call_args_list == [call(image_path)]

def test__get_url_from_cache_cannot_read_cache_file(tmp_path, mocker):
    ih = make_TestImageHost(cache_directory=tmp_path)
    image_path = 'some/path/to/foo.png'

    mocker.patch.object(ih, '_get_cache_file_suffix', return_value='d34db33f.foohost.url')
    cache_file = tmp_path / f'ANYTHING_1.{ih._get_cache_file_suffix.return_value}'
    cache_file.write_text(' http://1.cached.url ')
    cache_file.chmod(0o000)

    try:
        url = ih._get_url_from_cache(image_path)
    finally:
        cache_file.chmod(0o600)

    assert url is None
    assert ih._get_cache_file_suffix.call_args_list == [call(image_path)]

def test__get_url_from_cache_with_cache_directory_that_contains_invalid_glob_pattern(tmp_path, mocker):
    cache_directory = tmp_path / '[Dual-Audio]'
    cache_directory.mkdir()
    ih = make_TestImageHost(cache_directory=cache_directory)
    image_path = 'some/path/to/foo.png'

    mocker.patch.object(ih, '_get_cache_file_suffix', return_value='d34db33f.foohost.url')
    (cache_directory / f'ANYTHING.{ih._get_cache_file_suffix.return_value}').write_text('http://1.cached.url')

    url = ih._get_url_from_cache(image_path)
    assert url in (
        'http://1.cached.url',
    )
    assert ih._get_cache_file_suffix.call_args_list == [call(image_path)]

def test__get_url_from_cache_succeeds(tmp_path, mocker):
    ih = make_TestImageHost(cache_directory=tmp_path)
    image_path = 'some/path/to/foo.png'

    mocker.patch.object(ih, '_get_cache_file_suffix', return_value='d34db33f.foohost.url')
    (tmp_path / f'ANYTHING_1.{ih._get_cache_file_suffix.return_value}').write_text(' http://1.cached.url ')
    (tmp_path / f'ANYTHING_2.{ih._get_cache_file_suffix.return_value}').write_text('  http://2.cached.url  ')

    url = ih._get_url_from_cache(image_path)
    assert url in (
        'http://1.cached.url',
        'http://2.cached.url',
    )
    assert ih._get_cache_file_suffix.call_args_list == [call(image_path)]


@pytest.mark.parametrize(
    argnames='image_filename, cache_file_suffix, exp_cache_filename',
    argvalues=(
        pytest.param(
            'foo.png',
            'd34db33f.foohost.url',
            'foo.png.d34db33f.foohost.url',
            id='Short file name',
        ),
        pytest.param(
            'foo.' + ('o' * 300) + '.png',
            'd34db33f.foohost.url',
            ('foo.' + ('o' * 300) + '.png.d34db33f.foohost.url')[-(250 - len('d34db33f.foohost.url')):],
            id='Long file name',
        ),
    ),
)
def test__store_url_to_cache_succeeds(image_filename, cache_file_suffix, exp_cache_filename, tmp_path, mocker):
    ih = make_TestImageHost(cache_directory=tmp_path)
    image_path = f'some/path/to/{image_filename}'
    url = 'http://image.url'

    mocker.patch.object(type(ih), 'cache_directory', PropertyMock(return_value=tmp_path))
    mocker.patch.object(ih, '_get_cache_file_suffix', return_value=cache_file_suffix)

    ih._store_url_to_cache(image_path, url)

    exp_cache_filepath = tmp_path / exp_cache_filename
    print(exp_cache_filepath)
    assert exp_cache_filepath.read_text() == url
    assert ih._get_cache_file_suffix.call_args_list == [call(image_path)]

def test__store_url_to_cache_cannot_create_cache_directory(tmp_path, mocker):
    ih = make_TestImageHost(cache_directory=tmp_path)
    image_path = 'some/path/to/image.png'
    url = 'http://image.url'
    cache_directory = tmp_path / 'parent' / 'cache'
    cache_directory.parent.mkdir()
    cache_directory.parent.chmod(0o000)

    try:
        mocker.patch.object(type(ih), 'cache_directory', PropertyMock(return_value=str(cache_directory)))
        mocker.patch.object(ih, '_get_cache_file_suffix', return_value='d34db33f.imghost.url')

        exp_cache_file = cache_directory / 'image.png.d34db33f.imghost.url'
        exp_msg = f'Unable to write cache {exp_cache_file}: {cache_directory}: Permission denied'
        with pytest.raises(RuntimeError, match=rf'^{re.escape(exp_msg)}$'):
            ih._store_url_to_cache(image_path, url)
    finally:
        cache_directory.parent.chmod(0o700)

def test__store_url_to_cache_cannot_create_cache_file(tmp_path, mocker):
    ih = make_TestImageHost(cache_directory=tmp_path)
    image_path = 'some/path/to/image.png'
    url = 'http://image.url'
    cache_directory = tmp_path / 'cache'
    cache_directory.mkdir()
    cache_file = cache_directory / 'image.png.d34db33f.imghost.url'
    cache_file.write_text('http://secret.url')
    cache_file.chmod(0o000)

    try:
        mocker.patch.object(type(ih), 'cache_directory', PropertyMock(return_value=str(cache_directory)))
        mocker.patch.object(ih, '_get_cache_file_suffix', return_value='d34db33f.imghost.url')

        exp_cache_file = cache_directory / 'image.png.d34db33f.imghost.url'
        exp_msg = f'Unable to write cache {exp_cache_file}: Permission denied'
        with pytest.raises(RuntimeError, match=rf'^{re.escape(exp_msg)}$'):
            ih._store_url_to_cache(image_path, url)
    finally:
        cache_file.chmod(0o600)


@pytest.mark.skipif(sys.version_info <= (3, 9, 0), reason='Python <= 3.8 is lacking random.randbytes')
def test__get_cache_file_suffix_gets_unique_id_from_file_content(tmp_path, mocker):
    ih = make_TestImageHost(cache_directory=tmp_path)
    image_data = random.randbytes(11 * 1024)
    image_path = tmp_path / 'image.png'
    image_path.write_bytes(image_data)

    cache_file_suffix = ih._get_cache_file_suffix(image_path)
    assert cache_file_suffix == (
        hashlib.md5(image_data[:10 * 1024]).hexdigest()
        + f'.{ih.name}.url'
    )

def test__get_cache_file_suffix_gets_unique_id_from_image_path(tmp_path, mocker):
    ih = make_TestImageHost(cache_directory=tmp_path)
    image_path = tmp_path / 'image.png'
    image_path.write_bytes(b'whatever')
    image_path.chmod(0o000)
    try:
        cache_file_suffix = ih._get_cache_file_suffix(str(image_path))
        assert cache_file_suffix == (
            hashlib.md5(str(image_path).encode('utf8')).hexdigest()
            + f'.{ih.name}.url'
        )
    finally:
        image_path.chmod(0o600)
