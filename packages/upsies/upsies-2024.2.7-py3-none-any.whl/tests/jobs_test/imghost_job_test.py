from unittest.mock import AsyncMock, Mock, PropertyMock, call

import pytest

from upsies import errors
from upsies.jobs.imghost import ImageHostJob
from upsies.utils.imghosts import ImageHostBase


@pytest.fixture
def fooimg(tmp_path):
    class FooImageHost(ImageHostBase):
        name = 'foo.img'
        default_config = {}
        upload = AsyncMock()
        _upload_image = 'not an abstract base method'
    return FooImageHost(cache_directory=tmp_path / 'fooimg')

@pytest.fixture
def barimg(tmp_path):
    class BarImageHost(ImageHostBase):
        name = 'bar.img'
        default_config = {}
        upload = AsyncMock()
        _upload_image = 'not an abstract base method'
    return BarImageHost(cache_directory=tmp_path / 'barimg')

@pytest.fixture
def bazimg(tmp_path):
    class BazImageHost(ImageHostBase):
        name = 'baz.img'
        default_config = {}
        upload = AsyncMock()
        _upload_image = 'not an abstract base method'
    return BazImageHost(cache_directory=tmp_path / 'bazimg')

@pytest.fixture
def arfimg(tmp_path):
    class ArfImageHost(ImageHostBase):
        name = 'arf.img'
        default_config = {}
        upload = AsyncMock()
        _upload_image = 'not an abstract base method'
    return ArfImageHost(cache_directory=tmp_path / 'arfimg')

@pytest.fixture
def imghosts(fooimg, barimg, bazimg, arfimg):
    return fooimg, barimg, bazimg, arfimg

@pytest.fixture
def imghosts_map(fooimg, barimg, bazimg, arfimg):
    return {'fooimg': fooimg, 'barimg': barimg, 'bazimg': bazimg, 'arfimg': arfimg}

@pytest.fixture
async def make_ImageHostJob(tmp_path, imghosts):
    def make_ImageHostJob(home_directory=tmp_path, imghosts=imghosts, images_total=0, enqueue=()):
        return ImageHostJob(
            home_directory=home_directory,
            cache_directory=tmp_path,
            ignore_cache=False,
            imghosts=imghosts,
            images_total=images_total,
            enqueue=enqueue,
        )
    return make_ImageHostJob


def test_cache_id(make_ImageHostJob):
    job = make_ImageHostJob()
    assert job.cache_id is None


def test_initialize_sets_cache_directory_of_imghosts(make_ImageHostJob, fooimg, barimg):
    job = make_ImageHostJob(imghosts=(fooimg, barimg))
    for imghost in job._imghosts:
        assert imghost.cache_directory is job.cache_directory


def test_initialize_is_called_with_enqueue_and_images_total(make_ImageHostJob):
    with pytest.raises(RuntimeError, match=(r'^You must not give both arguments '
                                            r'"enqueue" and "images_total"\.$')):
        make_ImageHostJob(images_total=24, enqueue=('a', 'b', 'c'))


def test_initialize_is_called_without_enqueue_and_without_images_total(make_ImageHostJob, mocker):
    job = make_ImageHostJob()
    assert job.images_total == 0


async def test_initialize_is_called_with_enqueue(make_ImageHostJob, mocker):
    job = make_ImageHostJob(enqueue=('a', 'b', 'c'))
    assert job.images_total == 3


async def test_initialize_is_called_with_images_total(make_ImageHostJob, mocker):
    job = make_ImageHostJob(images_total=5)
    assert job.images_total == 5


@pytest.mark.parametrize(
    argnames='imghost_names, exp_mock_calls',
    argvalues=(
        ((), ['_upload_to_one']),
        (('fooimg',), ['_upload_to_one']),
        (('fooimg', 'barimg'), ['_upload_to_any']),
        (('fooimg', 'barimg', 'bazimg'), ['_upload_to_any']),
    ),
    ids=lambda v: repr(v),
)
async def test_handle_input(imghost_names, exp_mock_calls, imghosts_map, make_ImageHostJob, mocker):
    image_path = 'path/to/some.jpg'
    imghosts = [imghosts_map[name] for name in imghost_names]
    job = make_ImageHostJob(imghosts=imghosts)
    mocks = Mock()
    mocks.attach_mock(mocker.patch.object(job, '_upload_to_one'), '_upload_to_one')
    mocks.attach_mock(mocker.patch.object(job, '_upload_to_any'), '_upload_to_any')

    exp_mock_calls = [
        getattr(call, method_name)(image_path)
        for method_name in exp_mock_calls
    ]
    return_value = await job.handle_input(image_path)
    assert return_value is None
    assert mocks.mock_calls == exp_mock_calls


@pytest.mark.parametrize(
    argnames='number_of_imghosts, upload_exception, exp_upload_call, exp_error_call',
    argvalues=(
        (0, None, False, False),
        (1, None, True, False),
        (0, errors.RequestError('foo'), False, False),
        (1, errors.RequestError('foo'), True, True),
    ),
    ids=lambda v: repr(v),
)
async def test__upload_to_one(
        number_of_imghosts, upload_exception, exp_upload_call, exp_error_call,
        imghosts_map, make_ImageHostJob, mocker,
):
    image_path = 'path/to/some.jpg'
    imghosts = list(imghosts_map.values())[:number_of_imghosts]
    job = make_ImageHostJob(imghosts=imghosts)
    mocks = Mock()
    mocks.attach_mock(mocker.patch.object(job, '_upload', side_effect=upload_exception), '_upload')
    mocks.attach_mock(mocker.patch.object(job, 'error'), 'error')

    exp_mock_calls = []
    if exp_upload_call:
        exp_mock_calls.append(call._upload(image_path, imghosts[0]))
    if exp_error_call:
        exp_mock_calls.append(call.error(f'{imghosts[0].name}: Upload failed: some.jpg: {upload_exception}'))

    return_value = await job._upload_to_one(image_path)
    assert return_value is None
    assert mocks.mock_calls == exp_mock_calls


@pytest.mark.parametrize(
    argnames='number_of_imghosts, upload_exceptions, exp_upload_calls, exp_warn_calls, exp_error_call',
    argvalues=(
        (4, [], 1, 0, False),
        (4, [
            errors.RequestError('This service is down.'),
        ], 2, 1, False),
        (4, [
            errors.RequestError('This service is down.'),
            errors.RequestError('This service is also down.'),
        ], 3, 2, False),
        (4, [
            errors.RequestError('This service is down.'),
            errors.RequestError('This service is also down.'),
            errors.RequestError('Another service is down.'),
        ], 4, 3, False),
        (4, [
            errors.RequestError('This service is down.'),
            errors.RequestError('This service is also down.'),
            errors.RequestError('Another service is down.'),
            errors.RequestError('Last service is down.'),
        ], 4, 4, True),
    ),
    ids=lambda v: repr(v),
)
async def test__upload_to_any(
        number_of_imghosts, upload_exceptions, exp_upload_calls, exp_warn_calls, exp_error_call,
        imghosts_map, make_ImageHostJob, mocker,
):
    image_path = 'path/to/some.jpg'
    imghosts = list(imghosts_map.values())[:number_of_imghosts]
    job = make_ImageHostJob(imghosts=imghosts)
    mocks = Mock()
    upload_side_effects = upload_exceptions + [None for _ in range(exp_upload_calls)]
    mocks.attach_mock(mocker.patch.object(job, '_upload', side_effect=upload_side_effects), '_upload')
    mocks.attach_mock(mocker.patch.object(job, 'warn'), 'warn')
    mocks.attach_mock(mocker.patch.object(job, 'error'), 'error')

    exp_mock_calls = []
    if exp_upload_calls:
        for i, imghost in enumerate(imghosts[:exp_upload_calls]):
            exp_mock_calls.append(call._upload(image_path, imghost))
            is_final_host = i == len(imghosts[:exp_upload_calls])
            if not is_final_host:
                try:
                    e = upload_exceptions[i]
                except IndexError:
                    pass
                else:
                    exp_mock_calls.append(call.warn(f'{imghost.name}: Upload failed: some.jpg: {e}'))

    if exp_error_call:
        exp_mock_calls.append(call.error('All upload attempts failed.'))

    for c in exp_mock_calls:
        print('exp_call:', c)

    return_value = await job._upload_to_any(image_path)
    assert return_value is None
    assert mocks.mock_calls == exp_mock_calls


@pytest.mark.parametrize(
    argnames='ignore_cache, exp_cache_argument',
    argvalues=(
        (True, False),
        (False, True),
    ),
    ids=lambda v: str(v),
)
async def test__upload(ignore_cache, exp_cache_argument, fooimg, make_ImageHostJob, mocker):
    job = make_ImageHostJob(imghosts=(fooimg,))
    mocks = Mock()
    mocks.attach_mock(mocker.patch.object(fooimg, 'upload', side_effect=lambda path, cache: f'http://{path}'), 'upload')
    mocks.attach_mock(mocker.patch.object(job, 'send'), 'send')
    mocker.patch.object(type(job), 'ignore_cache', PropertyMock(return_value=ignore_cache))

    image_paths = [
        f'path/to/{i}.jpg'
        for i in range(6)
    ]
    for image_path in image_paths:
        return_value = await job._upload(image_path, fooimg)
        assert return_value is None
        assert mocks.mock_calls[-2] == call.upload(image_path, cache=exp_cache_argument)
        assert mocks.mock_calls[-1] == call.send(f'http://{image_path}')
        assert job._uploaded_images[-1] == f'http://{image_path}'
    assert len(job._uploaded_images) == len(image_paths)


@pytest.mark.parametrize(
    argnames='is_finished, images_uploaded, images_total, exp_exit_code',
    argvalues=(
        (False, -1, -1, None),
        (True, 0, 0, 1),
        (True, 1, 2, 1),
        (True, 2, 2, 0),
    ),
    ids=lambda v: str(v),
)
def test_exit_code(is_finished, images_uploaded, images_total, exp_exit_code, make_ImageHostJob, mocker):
    job = make_ImageHostJob()
    mocker.patch.object(type(job), 'is_finished', PropertyMock(return_value=is_finished))
    mocker.patch.object(type(job), 'images_uploaded', PropertyMock(return_value=images_uploaded))
    mocker.patch.object(type(job), 'images_total', PropertyMock(return_value=images_total))
    assert job.exit_code == exp_exit_code


def test_uploaded_images(make_ImageHostJob, mocker):
    job = make_ImageHostJob()
    mocker.patch.object(job, '_uploaded_images', ['<uploaded 1.jpg>', '<uploaded 2.jpg>', '<uploaded 3.jpg>'])
    assert job.uploaded_images == ('<uploaded 1.jpg>', '<uploaded 2.jpg>', '<uploaded 3.jpg>')


def test_urls_by_file(make_ImageHostJob, mocker):
    job = make_ImageHostJob()
    mocker.patch.object(job, '_urls_by_file', {
        '1.jpg': 'http://1.jpg',
        '2.jpg': 'http://2.jpg',
        '3.jpg': 'http://3.jpg',
    })
    urls_by_file = job.urls_by_file
    assert urls_by_file == {
        '1.jpg': 'http://1.jpg',
        '2.jpg': 'http://2.jpg',
        '3.jpg': 'http://3.jpg',
    }
    urls_by_file.clear()
    assert urls_by_file == {}
    assert job.urls_by_file == {
        '1.jpg': 'http://1.jpg',
        '2.jpg': 'http://2.jpg',
        '3.jpg': 'http://3.jpg',
    }


def test_images_uploaded(make_ImageHostJob, mocker):
    job = make_ImageHostJob()
    mocker.patch.object(job, '_uploaded_images', ['<uploaded 1.jpg>', '<uploaded 2.jpg>', '<uploaded 3.jpg>'])
    assert job.images_uploaded == 3


def test_images_total(make_ImageHostJob, mocker):
    job = make_ImageHostJob()
    unique_object = object()
    mocker.patch.object(job, '_images_total', unique_object)
    assert job.images_total is unique_object

    job.images_total = 123.5
    assert job.images_total == 123
    with pytest.raises(ValueError):
        job.images_total = 'foo'

    job.set_images_total(124)
    assert job.images_total == 124
    with pytest.raises(TypeError):
        job.set_images_total(object())
