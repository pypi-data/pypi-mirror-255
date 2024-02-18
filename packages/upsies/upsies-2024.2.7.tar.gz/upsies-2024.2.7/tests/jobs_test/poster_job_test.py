import hashlib
import re
from unittest.mock import AsyncMock, Mock, PropertyMock, call

import pytest

from upsies import errors
from upsies.jobs.poster import PosterJob


@pytest.fixture
def job(tmp_path):
    return PosterJob(
        getter=AsyncMock(),
        cache_directory=str(tmp_path / 'cache'),
        home_directory=str(tmp_path / 'home'),
    )


def test_cache_id(job):
    assert job.cache_id is None


def test_initialize(mocker):
    mocks = Mock()
    mocker.patch('upsies.jobs.poster.PosterJob.signal', PropertyMock())
    job = PosterJob(
        getter=mocks.getter,
        width=mocks.width,
        height=mocks.height,
        write_to=mocks.write_to,
        imghosts=mocks.imghosts,
    )

    assert job._getter is mocks.getter
    assert job._width is mocks.width
    assert job._height is mocks.height
    assert job._write_to is mocks.write_to
    assert job._imghosts is mocks.imghosts

    assert job.signal.add.call_args_list == [
        call('obtaining'),
        call('obtained'),
        call('downloading'),
        call('downloaded'),
        call('resizing'),
        call('resized'),
        call('uploading'),
        call('uploaded'),
    ]


@pytest.mark.parametrize(
    argnames=(
        'width, height, write_to, imghosts,'
        'obtain, resize, write, upload, get_poster_filename,'
        'exp_mock_calls,'
    ),
    argvalues=(
        pytest.param(
            123, 456, 'out.jpg', ('imghost1', 'imghost2'),
            AsyncMock(return_value={
                'poster': 'poster.jpg',
                'width': 456,
                'height': 789,
                'write_to': 'farout.jpg',
                'imghosts': ('imghost4', 'imghost3'),
            }),
            AsyncMock(return_value='maybe_resized.jpg'),
            AsyncMock(),
            AsyncMock(),
            Mock(),
            [
                call._obtain(),
                call._resize('poster.jpg', 456, 789),
                call._write('maybe_resized.jpg', 'farout.jpg'),
                call._upload('maybe_resized.jpg', ('imghost4', 'imghost3')),
            ],
            id='Parameters from getter',
        ),

        pytest.param(
            123, 456, 'out.jpg', ('imghost1', 'imghost2'),
            AsyncMock(return_value={'poster': 'poster.jpg'}),
            AsyncMock(return_value='maybe_resized.jpg'),
            AsyncMock(),
            AsyncMock(),
            Mock(),
            [
                call._obtain(),
                call._resize('poster.jpg', 123, 456),
                call._write('maybe_resized.jpg', 'out.jpg'),
                call._upload('maybe_resized.jpg', ('imghost1', 'imghost2')),
            ],
            id='Parameters from initialization',
        ),

        pytest.param(
            123, None, None, (),
            AsyncMock(return_value={'poster': 'poster.jpg'}),
            AsyncMock(return_value='maybe_resized.jpg'),
            AsyncMock(),
            AsyncMock(),
            Mock(return_value='out_forced.jpg'),
            [
                call._obtain(),
                call._resize('poster.jpg', 123, None),
                call._write('maybe_resized.jpg', None),
                call._upload('maybe_resized.jpg', ()),
                call._get_poster_filename('maybe_resized.jpg'),
                call._write('maybe_resized.jpg', 'out_forced.jpg'),
            ],
            id='No output file or image host specified, but width',
        ),

        pytest.param(
            None, 456, None, (),
            AsyncMock(return_value={'poster': 'poster.jpg'}),
            AsyncMock(return_value='maybe_resized.jpg'),
            AsyncMock(),
            AsyncMock(),
            Mock(return_value='out_forced.jpg'),
            [
                call._obtain(),
                call._resize('poster.jpg', None, 456),
                call._write('maybe_resized.jpg', None),
                call._upload('maybe_resized.jpg', ()),
                call._get_poster_filename('maybe_resized.jpg'),
                call._write('maybe_resized.jpg', 'out_forced.jpg'),
            ],
            id='No output file or image host specified, but height',
        ),

        pytest.param(
            None, None, None, (),
            AsyncMock(return_value={'poster': 'poster.jpg'}),
            AsyncMock(return_value='maybe_resized.jpg'),
            AsyncMock(),
            AsyncMock(),
            Mock(return_value='out_forced.jpg'),
            [
                call._obtain(),
                call._resize('poster.jpg', None, None),
                call._write('maybe_resized.jpg', None),
                call._upload('maybe_resized.jpg', ()),
                call.send('maybe_resized.jpg'),
            ],
            id='No output file or image host specified, no resizing',
        ),

        pytest.param(
            None, None, '', (),
            AsyncMock(side_effect=PosterJob._ProcessingError('failed to obtain')),
            AsyncMock(return_value='maybe_resized.jpg'),
            AsyncMock(),
            AsyncMock(),
            Mock(),
            [
                call._obtain(),
                call.error(PosterJob._ProcessingError('failed to obtain')),
            ],
            id='Exception from _obtain()',
        ),

        pytest.param(
            None, None, '', (),
            AsyncMock(return_value={'poster': 'poster.jpg'}),
            AsyncMock(side_effect=PosterJob._ProcessingError('failed to resize')),
            AsyncMock(),
            AsyncMock(),
            Mock(),
            [
                call._obtain(),
                call._resize('poster.jpg', None, None),
                call.error(PosterJob._ProcessingError('failed to resize')),
            ],
            id='Exception from _resize()',
        ),

        pytest.param(
            None, None, '', (),
            AsyncMock(return_value={'poster': 'poster.jpg'}),
            AsyncMock(return_value='maybe_resized.jpg'),
            AsyncMock(side_effect=PosterJob._ProcessingError('failed to write')),
            AsyncMock(),
            Mock(),
            [
                call._obtain(),
                call._resize('poster.jpg', None, None),
                call._write('maybe_resized.jpg', ''),
                call.error(PosterJob._ProcessingError('failed to write')),
            ],
            id='Exception from _write()',
        ),

        pytest.param(
            None, None, '', (),
            AsyncMock(return_value={'poster': 'poster.jpg'}),
            AsyncMock(return_value='maybe_resized.jpg'),
            AsyncMock(),
            AsyncMock(side_effect=PosterJob._ProcessingError('failed to upload')),
            Mock(),
            [
                call._obtain(),
                call._resize('poster.jpg', None, None),
                call._write('maybe_resized.jpg', ''),
                call._upload('maybe_resized.jpg', ()),
                call.error(PosterJob._ProcessingError('failed to upload')),
            ],
            id='Exception from _upload()',
        ),
    ),
    ids=lambda v: repr(v),
)
@pytest.mark.asyncio
async def test_run(
        width, height, write_to, imghosts,
        obtain, resize, write, upload, get_poster_filename,
        exp_mock_calls,
        mocker,
):
    job = PosterJob(getter=AsyncMock(), width=width, height=height, write_to=write_to, imghosts=imghosts)
    mocks = AsyncMock()
    mocks.attach_mock(mocker.patch.object(job, '_obtain', obtain), '_obtain')
    mocks.attach_mock(mocker.patch.object(job, '_resize', resize), '_resize')
    mocks.attach_mock(mocker.patch.object(job, '_write', write), '_write')
    mocks.attach_mock(mocker.patch.object(job, '_upload', upload), '_upload')
    mocks.attach_mock(mocker.patch.object(job, '_get_poster_filename', get_poster_filename), '_get_poster_filename')
    mocks.attach_mock(mocker.patch.object(job, 'send'), 'send')
    mocks.attach_mock(mocker.patch.object(job, 'error'), 'error')

    await job.run()
    assert mocks.mock_calls == exp_mock_calls


@pytest.mark.parametrize(
    argnames='params_or_poster, exp_result, exp_mock_calls',
    argvalues=(
        pytest.param(
            errors.RequestError('service down'),
            PosterJob._ProcessingError('Failed to get poster: service down'),
            [
                call.emit('obtaining'),
                call._getter(),
            ],
            id='Getter raises RequestError',
        ),
        pytest.param(
            '',
            PosterJob._ProcessingError('No poster found'),
            [
                call.emit('obtaining'),
                call._getter(),
            ],
            id='Getter returns empty string',
        ),
        pytest.param(
            None,
            PosterJob._ProcessingError('No poster found'),
            [
                call.emit('obtaining'),
                call._getter(),
            ],
            id='Getter returns None',
        ),
        pytest.param(
            'myposter.jpg',
            {'poster': 'myposter.jpg'},
            [
                call.emit('obtaining'),
                call._getter(),
                call.emit('obtained', 'myposter.jpg'),
            ],
            id='Getter returns file path or URL',
        ),
        pytest.param(
            {'poster': 'myposter.jpg', 'width': 123, 'foo': 'bar'},
            {'poster': 'myposter.jpg', 'width': 123, 'foo': 'bar'},
            [
                call.emit('obtaining'),
                call._getter(),
                call.emit('obtained', 'myposter.jpg'),
            ],
            id='Getter returns parameters',
        ),
    ),
    ids=lambda v: repr(v),
)
@pytest.mark.asyncio
async def test__obtain(params_or_poster, exp_result, exp_mock_calls, job, mocker):
    mocks = Mock()
    mocks.attach_mock(mocker.patch.object(job.signal, 'emit'), 'emit')
    if isinstance(params_or_poster, Exception):
        mocks.attach_mock(mocker.patch.object(job, '_getter', side_effect=params_or_poster), '_getter')
    else:
        mocks.attach_mock(mocker.patch.object(job, '_getter', return_value=params_or_poster), '_getter')

    if isinstance(exp_result, Exception):
        with pytest.raises(type(exp_result), match=rf'^{re.escape(str(exp_result))}$'):
            await job._obtain()
    else:
        return_value = await job._obtain()
        assert return_value == exp_result
    assert mocks.mock_calls == exp_mock_calls


@pytest.mark.parametrize(
    argnames=(
        'poster, width, height, cache_directory,'
        'get_poster_filepath, resize,'
        'exp_result, exp_mock_calls,'
    ),
    argvalues=(
        pytest.param(
            'path/to/myposter.jpg', None, None, 'path/to/cache',
            AsyncMock(return_value='filepath/myposter.jpg'),
            Mock(return_value='filepath/myposter.resized.jpg'),
            'path/to/myposter.jpg',
            [],
            id='No resizing',
        ),
        pytest.param(
            'path/to/myposter.jpg', 123, 456, 'path/to/cache',
            AsyncMock(return_value='filepath/myposter.jpg'),
            Mock(return_value='filepath/myposter.resized.jpg'),
            'filepath/myposter.resized.jpg',
            [
                call._get_poster_filepath('path/to/myposter.jpg'),
                call.emit('resizing', 'filepath/myposter.jpg'),
                call.resize(
                    'filepath/myposter.jpg',
                    target_directory='path/to/cache',
                    target_filename='myposter.123x456.jpg',
                    width=123,
                    height=456,
                ),
                call.emit('resized', 'filepath/myposter.resized.jpg'),
            ],
            id='Resizing successful',
        ),
        pytest.param(
            'path/to/myposter.jpg', 123, 456, 'path/to/cache',
            AsyncMock(return_value='filepath/myposter.jpg'),
            Mock(side_effect=errors.ImageResizeError('wat')),
            PosterJob._ProcessingError('Failed to resize poster: wat'),
            [
                call._get_poster_filepath('path/to/myposter.jpg'),
                call.emit('resizing', 'filepath/myposter.jpg'),
                call.resize(
                    'filepath/myposter.jpg',
                    target_directory='path/to/cache',
                    target_filename='myposter.123x456.jpg',
                    width=123,
                    height=456,
                ),
            ],
            id='Resizing failed',
        ),
    ),
    ids=lambda v: repr(v),
)
@pytest.mark.asyncio
async def test__resize(
        poster, width, height, cache_directory,
        get_poster_filepath, resize,
        exp_result, exp_mock_calls,
        job, mocker,
):
    mocks = Mock()
    mocker.patch.object(type(job), 'cache_directory', PropertyMock(return_value=cache_directory))
    mocks.attach_mock(mocker.patch.object(job.signal, 'emit'), 'emit')
    mocks.attach_mock(mocker.patch.object(job, '_get_poster_filepath', get_poster_filepath), '_get_poster_filepath')
    mocks.attach_mock(mocker.patch('upsies.utils.image.resize', resize), 'resize')

    if isinstance(exp_result, Exception):
        with pytest.raises(type(exp_result), match=rf'^{re.escape(str(exp_result))}$'):
            await job._resize(poster, width, height)
    else:
        return_value = await job._resize(poster, width, height)
        assert return_value == exp_result
    assert mocks.mock_calls == exp_mock_calls


@pytest.mark.parametrize(
    argnames=(
        'poster, filepath,'
        'read_file_or_url, write_file,'
        'exp_mock_calls,'
    ),
    argvalues=(
        pytest.param(
            'myposter.jpg', '',
            AsyncMock(return_value=b'image data'),
            AsyncMock(return_value='final/path/to/myposter.jpg'),
            [],
            id='Without destination file path',
        ),
        pytest.param(
            'myposter.jpg', 'path/to/myposter.jpg',
            AsyncMock(return_value=b'image data'),
            AsyncMock(return_value='final/path/to/myposter.jpg'),
            [
                call._read_file_or_url('myposter.jpg'),
                call._write_file(b'image data', 'path/to/myposter.jpg'),
                call.send('final/path/to/myposter.jpg'),
            ],
            id='With destination file path',
        ),
    ),
    ids=lambda v: repr(v),
)
@pytest.mark.asyncio
async def test__write(
        poster, filepath,
        read_file_or_url, write_file,
        exp_mock_calls,
        job, mocker,
):
    mocks = Mock()
    mocks.attach_mock(mocker.patch.object(job, '_read_file_or_url', read_file_or_url), '_read_file_or_url')
    mocks.attach_mock(mocker.patch.object(job, '_write_file', write_file), '_write_file')
    mocks.attach_mock(mocker.patch.object(job, 'send'), 'send')

    await job._write(poster, filepath)
    assert mocks.mock_calls == exp_mock_calls


BAD_IMGHOST = Mock(upload=AsyncMock(side_effect=errors.RequestError('service is down')))
GOOD_IMGHOST = Mock(upload=AsyncMock(return_value='http://example.org/good/myposter.jpg'))
IRRELEVANT_IMGHOST = Mock(upload=AsyncMock(return_value='http://example.org/irrelevant/myposter.jpg'))

@pytest.mark.parametrize(
    argnames=(
        'poster, imghosts,'
        'get_poster_filepath,'
        'exp_mock_calls, exp_exception'
    ),
    argvalues=(
        pytest.param(
            'myposter.jpg',
            (),
            AsyncMock(return_value='path/to/myposter.jpg'),
            [],
            None,
            id='No image hosts',
        ),
        pytest.param(
            'myposter.jpg',
            (BAD_IMGHOST, GOOD_IMGHOST, IRRELEVANT_IMGHOST),
            AsyncMock(return_value='path/to/myposter.jpg'),
            [
                call._get_poster_filepath('myposter.jpg'),
                call.emit('uploading', BAD_IMGHOST),
                call.BAD_IMGHOST.upload('path/to/myposter.jpg', thumb_width=0),
                call.warn('Failed to upload poster: service is down'),
                call.emit('uploading', GOOD_IMGHOST),
                call.GOOD_IMGHOST.upload('path/to/myposter.jpg', thumb_width=0),
                call.emit('uploaded', 'http://example.org/good/myposter.jpg'),
                call.send('http://example.org/good/myposter.jpg'),
            ],
            None,
            id='Bad image host and good image host',
        ),
        pytest.param(
            'myposter.jpg',
            (BAD_IMGHOST, BAD_IMGHOST),
            AsyncMock(return_value='path/to/myposter.jpg'),
            [
                call._get_poster_filepath('myposter.jpg'),
                call.emit('uploading', BAD_IMGHOST),
                call.BAD_IMGHOST.upload('path/to/myposter.jpg', thumb_width=0),
                call.warn('Failed to upload poster: service is down'),
                call.emit('uploading', BAD_IMGHOST),
                call.BAD_IMGHOST.upload('path/to/myposter.jpg', thumb_width=0),
                call.warn('Failed to upload poster: service is down'),
            ],
            PosterJob._ProcessingError('All uploads failed'),
            id='Only bad image hosts',
        ),
    ),
    ids=lambda v: repr(v),
)
@pytest.mark.asyncio
async def test__upload(
        poster, imghosts,
        get_poster_filepath,
        exp_mock_calls, exp_exception,
        job, mocker,
):
    mocks = Mock()
    mocks.attach_mock(mocker.patch.object(job, '_get_poster_filepath', get_poster_filepath), '_get_poster_filepath')
    mocks.attach_mock(BAD_IMGHOST, 'BAD_IMGHOST')
    mocks.attach_mock(GOOD_IMGHOST, 'GOOD_IMGHOST')
    mocks.attach_mock(IRRELEVANT_IMGHOST, 'IRRELEVANT_IMGHOST')
    mocks.attach_mock(mocker.patch.object(job.signal, 'emit'), 'emit')
    mocks.attach_mock(mocker.patch.object(job, 'send'), 'send')
    mocks.attach_mock(mocker.patch.object(job, 'warn'), 'warn')
    mocks.attach_mock(mocker.patch.object(job, 'error'), 'error')

    if isinstance(exp_exception, Exception):
        with pytest.raises(type(exp_exception), match=rf'^{re.escape(str(exp_exception))}$'):
            await job._upload(poster, imghosts)
    else:
        await job._upload(poster, imghosts)
    assert mocks.mock_calls == exp_mock_calls


@pytest.mark.parametrize(
    argnames=(
        'poster, read_file_or_url, cache_directory, get_poster_filename, write_file,'
        'exp_mock_calls, exp_return_value,'
    ),
    argvalues=(
        pytest.param(
            'http://my.poster.jpg',
            AsyncMock(return_value=b'image data'),
            'path/to/cache',
            Mock(return_value='poster_filename.jpg'),
            AsyncMock(return_value='path/to/poster.jpg'),
            [
                call._read_file_or_url('http://my.poster.jpg'),
                call._get_poster_filename('http://my.poster.jpg'),
                call._write_file(b'image data', 'path/to/cache/poster_filename.jpg'),
            ],
            'path/to/poster.jpg',
            id='Poster is URL',
        ),
        pytest.param(
            'myposter.jpg',
            AsyncMock(return_value=b'image data'),
            'path/to/cache',
            Mock(return_value='poster_filename.jpg'),
            AsyncMock(return_value='path/to/poster.jpg'),
            [],
            'myposter.jpg',
            id='Poster is file path',
        ),
    ),
    ids=lambda v: repr(v),
)
@pytest.mark.asyncio
async def test__get_poster_filepath(
        poster, read_file_or_url, cache_directory, get_poster_filename, write_file,
        exp_mock_calls, exp_return_value,
        job, mocker,
):
    mocks = Mock()
    mocker.patch.object(type(job), 'cache_directory', PropertyMock(return_value=cache_directory))
    mocks.attach_mock(mocker.patch.object(job, '_read_file_or_url', read_file_or_url), '_read_file_or_url')
    mocks.attach_mock(mocker.patch.object(job, '_get_poster_filename', get_poster_filename), '_get_poster_filename')
    mocks.attach_mock(mocker.patch.object(job, '_write_file', write_file), '_write_file')

    # Return value should be cached.
    for _ in range(3):
        return_value = await job._get_poster_filepath(poster)
        assert return_value == exp_return_value
    assert mocks.mock_calls == exp_mock_calls


@pytest.mark.parametrize(
    argnames='poster, exp_return_value',
    argvalues=(
        pytest.param(
            'http://example.org/path/to/poster.jpg?foo=bar',
            'poster:example.org.' + hashlib.md5(b'/path/to/poster.jpg.foo=bar').hexdigest() + '.jpg',
            id='Poster is URL with extension',
        ),
        pytest.param(
            'http://example.org/path/to/d34db33f?foo=bar',
            'poster:example.org.' + hashlib.md5(b'/path/to/d34db33f.foo=bar').hexdigest(),
            id='Poster is URL without extension',
        ),
        pytest.param(
            'path/to/poster.jpg',
            'poster.jpg',
            id='Poster is file path',
        ),
    ),
    ids=lambda v: repr(v),
)
def test__get_poster_filename(poster, exp_return_value, job):
    return_value = job._get_poster_filename(poster)
    assert return_value == exp_return_value


@pytest.mark.parametrize(
    argnames=(
        'poster, http_get,'
        'exp_result, exp_mock_calls,'
    ),
    argvalues=(
        pytest.param(
            'http://myposter.jpg',
            AsyncMock(return_value=Mock(bytes=b'image data')),
            b'image data',
            [
                call.emit('downloading', 'http://myposter.jpg'),
                call.http_get('http://myposter.jpg', cache=True),
                call.emit('downloaded', 'http://myposter.jpg'),
            ],
            id='Poster is good URL',
        ),
        pytest.param(
            'http://broken.host/myposter.jpg',
            AsyncMock(side_effect=errors.RequestError('service is down')),
            PosterJob._ProcessingError('Failed to download poster: service is down'),
            [
                call.emit('downloading', 'http://broken.host/myposter.jpg'),
                call.http_get('http://broken.host/myposter.jpg', cache=True),
            ],
            id='Poster is bad URL',
        ),
    ),
    ids=lambda v: repr(v),
)
@pytest.mark.asyncio
async def test__read_file_or_url_gets_url(
        poster, http_get,
        exp_result, exp_mock_calls,
        job, mocker,
):
    mocks = Mock()
    mocks.attach_mock(mocker.patch('upsies.utils.http.get', http_get), 'http_get')
    mocks.attach_mock(mocker.patch.object(job.signal, 'emit'), 'emit')

    if isinstance(exp_result, Exception):
        with pytest.raises(type(exp_result), match=rf'^{re.escape(str(exp_result))}$'):
            await job._read_file_or_url(poster)
    else:
        return_value = await job._read_file_or_url(poster)
        assert return_value == exp_result
    assert mocks.mock_calls == exp_mock_calls

@pytest.mark.parametrize(
    argnames=(
        'poster, image_data,'
        'exp_result,'
    ),
    argvalues=(
        pytest.param(
            'path/to/myposter.jpg',
            b'image data',
            b'image data',
            id='Poster is good file',
        ),
        pytest.param(
            'path/to/myposter.jpg',
            None,
            PosterJob._ProcessingError('Failed to read poster: No such file or directory'),
            id='Poster is bad file',
        ),
    ),
    ids=lambda v: repr(v),
)
@pytest.mark.asyncio
async def test__read_file_or_url_gets_filepath(
        poster, image_data,
        exp_result,
        job, tmp_path, mocker,
):
    mocks = Mock()
    mocks.attach_mock(mocker.patch.object(job.signal, 'emit'), 'emit')

    poster = tmp_path / 'poster.jpg'
    if image_data is not None:
        poster.write_bytes(image_data)

    if isinstance(exp_result, Exception):
        with pytest.raises(type(exp_result), match=rf'^{re.escape(str(exp_result))}$'):
            await job._read_file_or_url(str(poster))
    else:
        return_value = await job._read_file_or_url(str(poster))
        assert return_value == exp_result

    # No signals emitted when reading files.
    assert mocks.mock_calls == []


@pytest.mark.parametrize(
    argnames=(
        'data, filepath, sanitize_path, sanitized_path_is_writable,'
        'exp_result,'
    ),
    argvalues=(
        pytest.param(
            b'image data',
            '{tmp_path}/path/to/poster.jpg',
            Mock(side_effect=lambda path: f'{path}.sanitized'),
            True,
            '{tmp_path}/path/to/poster.jpg.sanitized',
            id='File is written',
        ),
        pytest.param(
            b'image data',
            '{tmp_path}/path/to/poster.jpg',
            Mock(side_effect=lambda path: f'{path}.sanitized'),
            False,
            PosterJob._ProcessingError('Failed to write {tmp_path}/path/to/poster.jpg.sanitized: Permission denied'),
            id='File cannot be written',
        ),
    ),
    ids=lambda v: repr(v),
)
@pytest.mark.asyncio
async def test__write_file(
        data, filepath, sanitize_path, sanitized_path_is_writable,
        exp_result,
        job, tmp_path, mocker,
):
    mocks = Mock()
    mocks.attach_mock(mocker.patch('upsies.utils.fs.sanitize_path', sanitize_path), 'sanitize_path')
    mocks.attach_mock(mocker.patch.object(job.signal, 'emit'), 'emit')

    filepath = filepath.format(tmp_path=tmp_path)
    (tmp_path / filepath).parent.mkdir(parents=True, exist_ok=True)
    if not sanitized_path_is_writable:
        (tmp_path / filepath).parent.chmod(0o000)

    try:
        if isinstance(exp_result, Exception):
            msg = str(exp_result).format(tmp_path=tmp_path)
            with pytest.raises(type(exp_result), match=rf'^{re.escape(msg)}$'):
                await job._write_file(data, filepath)
        else:
            return_value = await job._write_file(data, filepath)
            assert return_value == exp_result.format(tmp_path=tmp_path)
    finally:
        (tmp_path / filepath).parent.chmod(0o700)

    assert mocks.mock_calls == [
        call.sanitize_path(filepath),
    ]
