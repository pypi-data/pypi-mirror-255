from unittest.mock import Mock, call

import pytest

from upsies import errors
from upsies.jobs.set import SetJob


def config_mock(dct):
    def getitem(self, name):
        return dct[name]

    def setitem(self, name, value):
        dct[name] = value

    return Mock(
        paths=tuple(dct),
        __getitem__=getitem,
        __setitem__=setitem,
        keys=lambda: dct.keys(),
        values=lambda: dct.values(),
    )


@pytest.fixture
def make_SetJob(tmp_path):
    def make_SetJob(**kwargs):
        return SetJob(home_directory=tmp_path, cache_directory=tmp_path, **kwargs)
    return make_SetJob


def test_cache_id(make_SetJob):
    job = make_SetJob(config=config_mock({'foo': 'bar'}))
    assert job.cache_id is None


def test_output_is_hidden(make_SetJob):
    job = make_SetJob(config=config_mock({'foo': 'bar'}))
    assert job.hidden is True


@pytest.mark.asyncio
async def test_no_arguments(mocker, make_SetJob):
    mocker.patch('upsies.jobs.set.SetJob._display_option')
    cfg = config_mock({'foo': '1', 'bar': '2', 'baz': '3'})
    job = make_SetJob(config=cfg)
    job.start()
    await job.wait()
    assert job._display_option.call_args_list == [call('foo'), call('bar'), call('baz')]


@pytest.mark.parametrize('option', ('foo', 'bar', 'baz'))
@pytest.mark.asyncio
async def test_arguments_option(option, mocker, make_SetJob):
    mocker.patch('upsies.jobs.set.SetJob._display_option')
    values = {'foo': '1', 'bar': '2', 'baz': '3'}
    cfg = config_mock(values)
    job = make_SetJob(config=cfg, option=option)
    job.start()
    await job.wait()
    assert cfg.reset.call_args_list == []
    assert cfg.write.call_args_list == []
    assert job._display_option.call_args_list == [call(option)]
    assert dict(cfg) == values

@pytest.mark.parametrize('option', ('foo', 'bar', 'baz'))
@pytest.mark.asyncio
async def test_arguments_option_and_value(option, mocker, make_SetJob):
    mocker.patch('upsies.jobs.set.SetJob._display_option')
    values = {'foo': '1', 'bar': '2', 'baz': '3'}
    cfg = config_mock(values)
    job = make_SetJob(config=cfg, option=option, value='hello')
    job.start()
    await job.wait()
    assert cfg.reset.call_args_list == []
    assert cfg.write.call_args_list == [call(option)]
    assert job._display_option.call_args_list == [call(option)]
    assert dict(cfg) == {**values, option: 'hello'}

@pytest.mark.parametrize('option', ('foo', 'bar', 'baz'))
@pytest.mark.asyncio
async def test_arguments_option_and_reset(option, mocker, make_SetJob):
    mocker.patch('upsies.jobs.set.SetJob._display_option')
    values = {'foo': '1', 'bar': '2', 'baz': '3'}
    cfg = config_mock(values)
    job = make_SetJob(config=cfg, option=option, reset=True)
    job.start()
    await job.wait()
    assert cfg.reset.call_args_list == [call(option)]
    assert cfg.write.call_args_list == [call(option)]
    assert job._display_option.call_args_list == [call(option)]
    assert dict(cfg) == values

@pytest.mark.asyncio
async def test_arguments_reset(mocker, make_SetJob):
    mocker.patch('upsies.jobs.set.SetJob._display_option')
    values = {'foo': '1', 'bar': '2', 'baz': '3'}
    cfg = config_mock(values)
    job = make_SetJob(config=cfg, reset=True)
    job.start()
    await job.wait()
    assert cfg.reset.call_args_list == [call('foo'), call('bar'), call('baz')]
    assert cfg.write.call_args_list == [call('foo'), call('bar'), call('baz')]
    assert job._display_option.call_args_list == [call('foo'), call('bar'), call('baz')]
    assert dict(cfg) == values

def test_arguments_value(make_SetJob):
    with pytest.raises(RuntimeError, match=r'^Argument "value" needs argument "option"\.$'):
        make_SetJob(config=config_mock({'foo': 'bar'}), value='foo')

def test_arguments_value_and_reset(make_SetJob):
    with pytest.raises(RuntimeError, match=r'^Arguments "value" and "reset" are mutually exclusive\.$'):
        make_SetJob(config=config_mock({'foo': 'bar'}), value='foo', reset=True)

def test_arguments_option_and_value_and_reset(make_SetJob):
    with pytest.raises(RuntimeError, match=r'^Arguments "value" and "reset" are mutually exclusive\.$'):
        make_SetJob(config=config_mock({'foo': 'bar'}), value='foo', reset=True)


@pytest.mark.parametrize(
    argnames=('mode', 'kwargs'),
    argvalues=(
        ('_reset_mode', {'reset': True}),
        ('_set_mode', {'option': 'foo', 'value': 'bar'}),
        ('_display_mode', {}),
    ),
    ids=lambda v: str(v),
)
@pytest.mark.asyncio
async def test_ConfigError_is_handled(mode, kwargs, mocker, make_SetJob):
    mocker.patch('upsies.jobs.set.SetJob._display_option')
    mocker.patch(f'upsies.jobs.set.SetJob.{mode}', side_effect=errors.ConfigError('no!'))
    values = {'foo': '1', 'bar': '2', 'baz': '3'}
    cfg = config_mock(values)
    job = make_SetJob(config=cfg, **kwargs)
    job.start()
    await job.wait()
    assert job.errors == (errors.ConfigError('no!'),)
    assert job.is_finished
    assert job.exit_code != 0
    assert cfg.reset.call_args_list == []
    assert cfg.write.call_args_list == []
    assert job._display_option.call_args_list == []
    assert dict(cfg) == values


@pytest.mark.parametrize(
    argnames=('name', 'value', 'exp_output'),
    argvalues=(
        ('foo', 'asdf', 'foo = asdf'),
        ('bar', 'a sd f', 'bar = a sd f'),
        ('baz', 123, 'baz = 123'),
        ('foo', ['a', 'b', 'c'], 'foo =\n  a\n  b\n  c'),
        ('foo', [1, 2, 3, 'd'], 'foo =\n  1\n  2\n  3\n  d'),
        ('foo', [], 'foo ='),
    ),
    ids=lambda v: str(v),
)
@pytest.mark.asyncio
async def test_display_option(name, value, exp_output, make_SetJob):
    job = make_SetJob(config=config_mock({name: value}))
    job.start()
    await job.wait()
    assert job.output == (exp_output,)
