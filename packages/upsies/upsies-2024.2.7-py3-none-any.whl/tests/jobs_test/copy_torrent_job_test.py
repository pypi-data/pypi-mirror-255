import os
from unittest.mock import Mock, call

import pytest

from upsies.jobs.torrent import CopyTorrentJob


@pytest.fixture
async def make_CopyTorrentJob(tmp_path):
    def make_CopyTorrentJob(destination, enqueue=()):
        return CopyTorrentJob(
            home_directory=tmp_path,
            cache_directory=tmp_path,
            ignore_cache=False,
            destination=destination,
            enqueue=enqueue,
        )
    return make_CopyTorrentJob


def test_cache_id(make_CopyTorrentJob, tmp_path):
    job = make_CopyTorrentJob(destination=tmp_path)
    assert job.cache_id is None


@pytest.mark.asyncio
async def test_handle_input_call_order(make_CopyTorrentJob, mocker, tmp_path):
    source = tmp_path / 'foo.torrent'
    source.write_bytes(b'content')

    job = make_CopyTorrentJob(destination=tmp_path)

    mocks = Mock()
    job.signal.register('copying', mocks.copying)
    job.signal.register('copied', mocks.copied)
    mocks.attach_mock(mocker.patch('shutil.copy2', return_value=str(tmp_path / source.name)), 'copy2')
    mocks.attach_mock(mocker.patch.object(job, 'send'), 'send')
    mocks.attach_mock(mocker.patch.object(job, 'error'), 'error')

    await job.handle_input(str(source))

    assert mocks.mock_calls == [
        call.copying(str(source)),
        call.copy2(str(source), str(tmp_path)),
        call.send(str(source)),
        call.copied(mocks.copy2.return_value),
    ]

@pytest.mark.asyncio
async def test_handle_input_reports_nonexisting_file(make_CopyTorrentJob, mocker, tmp_path):
    source = tmp_path / 'foo.torrent'

    job = make_CopyTorrentJob(destination=tmp_path)

    mocks = Mock()
    job.signal.register('copying', mocks.copying)
    job.signal.register('copied', mocks.copied)
    mocks.attach_mock(mocker.patch('shutil.copy2'), 'copy2')
    mocks.attach_mock(mocker.patch.object(job, 'send'), 'send')
    mocks.attach_mock(mocker.patch.object(job, 'error'), 'error')

    await job.handle_input(source)

    assert mocks.mock_calls == [
        call.error(f'{source}: No such file'),
    ]


@pytest.mark.asyncio
async def test_handle_input_gets_large_file(make_CopyTorrentJob, mocker, tmp_path):
    source = tmp_path / 'foo.torrent'
    with open(source, 'wb') as f:
        f.truncate(CopyTorrentJob.MAX_FILE_SIZE + 1)  # Sparse file

    job = make_CopyTorrentJob(destination=tmp_path)

    mocks = Mock()
    job.signal.register('copying', mocks.copying)
    job.signal.register('copied', mocks.copied)
    mocks.attach_mock(mocker.patch('shutil.copy2'), 'copy2')
    mocks.attach_mock(mocker.patch.object(job, 'send'), 'send')
    mocks.attach_mock(mocker.patch.object(job, 'error'), 'error')

    await job.handle_input(source)

    assert mocks.mock_calls == [
        call.error(f'{source}: File is too large'),
    ]


@pytest.mark.asyncio
async def test_handle_input_sends_destination_path_on_success(make_CopyTorrentJob, mocker, tmp_path):
    source = tmp_path / 'foo.torrent'
    source.write_bytes(b'content')
    destination = tmp_path / 'bar.torrent'

    job = make_CopyTorrentJob(destination=destination)

    mocks = Mock()
    mocks.attach_mock(mocker.patch.object(job, 'send'), 'send')
    mocks.attach_mock(mocker.patch.object(job, 'error'), 'error')

    await job.handle_input(source)

    assert mocks.mock_calls == [
        call.send(str(destination)),
    ]
    assert os.path.exists(destination)


@pytest.mark.asyncio
async def test_handle_input_sends_source_path_on_failure(make_CopyTorrentJob, mocker, tmp_path):
    source = tmp_path / 'foo.torrent'
    source.write_bytes(b'content')
    destination = tmp_path / 'bar.torrent'

    job = make_CopyTorrentJob(destination=destination)

    mocks = Mock()
    job.signal.register('copying', mocks.copying)
    job.signal.register('copied', mocks.copied)
    mocks.attach_mock(mocker.patch('shutil.copy2', side_effect=PermissionError('Permission denied')), 'copy2')
    mocks.attach_mock(mocker.patch.object(job, 'send'), 'send')
    mocks.attach_mock(mocker.patch.object(job, 'error'), 'error')

    await job.handle_input(source)

    assert job.output == ()
    assert mocks.mock_calls == [
        call.copying(source),
        call.copy2(source, str(destination)),
        call.error(f'Failed to copy {source} to {job._destination}: Permission denied'),
    ]


@pytest.mark.asyncio
async def test_info_property(make_CopyTorrentJob, mocker, tmp_path):
    job = make_CopyTorrentJob(destination=tmp_path)

    assert job.info == ''
    job.signal.emit('copying', 'path/to/foo')
    assert job.info == 'Copying foo'
    job.signal.emit('copied', 'path/to/foo')
    assert job.info == ''

    job.info = 'some info'
    job.signal.emit('error', 'some error')
    assert job.info == ''

    job.info = 'some info'
    job.signal.emit('finished', job)
    assert job.info == ''
