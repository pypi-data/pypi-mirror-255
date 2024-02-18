import re
import sys
from unittest.mock import AsyncMock, Mock, PropertyMock, call

import pytest

from upsies.jobs import dialog


@pytest.fixture
def make_ChoiceJob(tmp_path):
    def make_ChoiceJob(**kwargs):
        return dialog.ChoiceJob(home_directory=tmp_path, cache_directory=tmp_path, **kwargs)
    return make_ChoiceJob


def test_name_property(make_ChoiceJob):
    job = make_ChoiceJob(name='foo', label='Foo', options=('1', '2', '3'))
    assert job.name == 'foo'


def test_label_property(make_ChoiceJob):
    job = make_ChoiceJob(name='foo', label='Foo', options=('1', '2', '3'))
    assert job.label == 'Foo'


def test_question_property(make_ChoiceJob):
    job = make_ChoiceJob(name='foo', label='Foo', options=('1', '2', '3'), question='Pick a number:')
    assert job.question == 'Pick a number:'
    job.question = 'Peeck ay numbeur:'
    assert job.question == 'Peeck ay numbeur:'
    job.question = None
    assert job.question is None
    job.question = ''
    assert job.question == ''


def test_options_getter(make_ChoiceJob):
    job = make_ChoiceJob(name='foo', label='Foo', options=('1', '2', '3'))
    assert job.options is job._options
    assert job._options == [('1', '1'), ('2', '2'), ('3', '3')]

def test_options_setter_with_strings(make_ChoiceJob):
    job = make_ChoiceJob(name='foo', label='Foo', options=('1', '2', '3'))
    job.options = ('a', 'b', 'c')
    assert job._options == [('a', 'a'), ('b', 'b'), ('c', 'c')]

@pytest.mark.parametrize('invalid_sequence', (['b'], ['b', 2, 'foo']))
def test_options_setter_with_invalid_sequence(invalid_sequence, make_ChoiceJob):
    job = make_ChoiceJob(name='foo', label='Foo', options=('1', '2', '3'))
    with pytest.raises(ValueError, match=(
            r'^Option must be 2-tuple, '
            rf'not {re.escape(str(invalid_sequence))}$'
    )):
        job.options = (['a', 1], invalid_sequence, ['c', 3])
    assert job._options == [('1', '1'), ('2', '2'), ('3', '3')]

def test_options_setter_with_valid_sequence(make_ChoiceJob):
    job = make_ChoiceJob(name='foo', label='Foo', options=('1', '2', '3'))
    job.options = (['a', 1], ['b', 2], ['c', 3])
    assert job._options == [('a', 1), ('b', 2), ('c', 3)]

def test_options_setter_with_invalid_option(make_ChoiceJob):
    job = make_ChoiceJob(name='foo', label='Foo', options=('1', '2', '3'))
    with pytest.raises(ValueError, match=r'^Option must be 2-tuple, not None$'):
        job.options = (['a', 1], None, ['c', 3])
    assert job._options == [('1', '1'), ('2', '2'), ('3', '3')]

def test_options_setter_with_too_few_options(make_ChoiceJob):
    job = make_ChoiceJob(name='foo', label='Foo', options=('1', '2', '3'))
    with pytest.raises(ValueError, match=r"^There must be at least 2 options: \['a'\]$"):
        job.options = ['a']
    assert job._options == [('1', '1'), ('2', '2'), ('3', '3')]

@pytest.mark.parametrize('focused_option', (('2', 2), '2', 2))
def test_options_setter_preserves_focus_if_possible(focused_option, make_ChoiceJob):
    job = make_ChoiceJob(name='foo', label='Foo', options=(('1', 1), ('2', 2), ('3', 3)))
    job.focused = ('2', 2)
    assert job.focused == ('2', 2)
    job.options = (['a', 0], ['b', 1], ['c', 2], ['d', 3], ['e', 4])
    assert job.focused == ('c', 2)

@pytest.mark.parametrize('focused_option', (('2', 2), '2', 2))
def test_options_setter_defaults_focus_to_first_option(focused_option, make_ChoiceJob):
    job = make_ChoiceJob(name='foo', label='Foo', options=(('1', 1), ('2', 2), ('3', 3)))
    job.focused = ('3', 3)
    assert job.focused == ('3', 3)
    job.options = (['0', 0], ['1', 1], ['2', 2])
    assert job.focused == ('0', 0)

def test_options_setter_emits_dialog_updated_signal(make_ChoiceJob):
    job = make_ChoiceJob(name='foo', label='Foo', options=(('1', 1), ('2', 2), ('3', 3)))
    cb = Mock()
    job.signal.register('dialog_updated', cb)
    job.options = (['0', 0], ['1', 1], ['2', 2])
    assert cb.call_args_list == [call(job)]

def test_options_change_emits_dialog_updated_signal(make_ChoiceJob):
    job = make_ChoiceJob(name='foo', label='Foo', options=(('1', 1), ('2', 2), ('3', 3)))
    cb = Mock()
    job.signal.register('dialog_updated', cb)
    job.options.append(['3', 3])
    assert cb.call_args_list == [call(job)]


@pytest.mark.parametrize(
    argnames='options, thing, exp_result',
    argvalues=(
        # None
        ([('Foo', 10), ('Bar', 20), ('Baz', 30)], None, None),

        # option
        ([('Foo', 10), ('Bar', 20), ('Baz', 30)], ('Foo', 10), 0),
        ([('Foo', 10), ('Bar', 20), ('Baz', 30)], ('Bar', 20), 1),
        ([('Foo', 10), ('Bar', 20), ('Baz', 30)], ('Baz', 30), 2),

        # Index
        ([('Foo', 10), ('Bar', 20), ('Baz', 30)], -1, 0),
        ([('Foo', 10), ('Bar', 20), ('Baz', 30)], 0, 0),
        ([('Foo', 10), ('Bar', 20), ('Baz', 30)], 1, 1),
        ([('Foo', 10), ('Bar', 20), ('Baz', 30)], 2, 2),
        ([('Foo', 10), ('Bar', 20), ('Baz', 30)], 3, 2),

        # Label
        ([('Foo', 10), ('Bar', 20), ('Baz', 30)], 'Foo', 0),
        ([('Foo', 10), ('Bar', 20), ('Baz', 30)], 'Bar', 1),
        ([('Foo', 10), ('Bar', 20), ('Baz', 30)], 'Baz', 2),

        # Value
        ([('Foo', 1.1), ('Bar', 2.2), ('Baz', 3.3)], 1.1, 0),
        ([('Foo', 1.1), ('Bar', 2.2), ('Baz', 3.3)], 2.2, 1),
        ([('Foo', 1.1), ('Bar', 2.2), ('Baz', 3.3)], 3.3, 2),

        # Regular expression match against label
        ([('Foo', 1.1), ('Bar', 2.2), ('Baz', 3.3)], re.compile(r'(?i:foo)'), 0),
        ([('Foo', 1.1), ('Bar', 2.2), ('Baz', 3.3)], re.compile(r'r$'), 1),
        ([('Foo', 1.1), ('Bar', 2.2), ('Baz', 3.3)], re.compile(r'^[Bb]az$'), 2),

        # Regular expression match against value
        ([('Foo', 1.1), ('Bar', 2.2), ('Baz', 3.3)], re.compile(r'\d\.1'), 0),
        ([('Foo', 1.1), ('Bar', 2.2), ('Baz', 3.3)], re.compile(r'2+$'), 1),
        ([('Foo', 1.1), ('Bar', 2.2), ('Baz', 3.3)], re.compile(r'3\.?3'), 2),

        # No matching option found
        ([('Foo', 1.1), ('Bar', 2.2), ('Baz', 3.3)], 'foo', ValueError("No such option: 'foo'")),
    ),
    ids=lambda v: str(v),
)
def test_get_index(options, thing, exp_result, make_ChoiceJob):
    job = make_ChoiceJob(name='foo', label='Foo', options=options)

    if isinstance(exp_result, Exception):
        with pytest.raises(type(exp_result), match=rf'^{re.escape(str(exp_result))}$'):
            job.get_index(thing)
    else:
        index = job.get_index(thing)
        assert index == exp_result

@pytest.mark.parametrize(
    argnames='options, index, focused_index, exp_return_value',
    argvalues=(
        ([('a', 1), ('b', 2), ('c', 3)], 0, 2, ('a', 1)),
        ([('a', 1), ('b', 2), ('c', 3)], 1, 1, ('b', 2)),
        ([('a', 1), ('b', 2), ('c', 3)], 2, 0, ('c', 3)),
        ([('a', 1), ('b', 2), ('c', 3)], None, 2, ('c', 3)),
        ([('a', 1), ('b', 2), ('c', 3)], None, 1, ('b', 2)),
        ([('a', 1), ('b', 2), ('c', 3)], None, 0, ('a', 1)),
    ),
    ids=lambda v: repr(v),
)
def test_get_option(options, index, focused_index, exp_return_value, make_ChoiceJob, mocker):
    job = make_ChoiceJob(name='foo', label='Foo', options=options)
    mocker.patch.object(job, 'get_index', return_value=index)
    mocker.patch.object(type(job), 'focused_index', PropertyMock(return_value=focused_index))

    return_value = job.get_option('something')
    assert return_value == exp_return_value
    assert job.get_index.call_args_list == [call('something')]


def test_focused_index(make_ChoiceJob):
    job = make_ChoiceJob(name='foo', label='Foo', options=('1', '2', '3'))
    assert job.focused_index is job._focused_index
    delattr(job, '_focused_index')
    assert job.focused_index is None


@pytest.mark.parametrize(
    argnames='options, focused_index, exp_focused',
    argvalues=(
        ((('1', 1), ('2', 2), ('3', 3)), None, None),
        ((('1', 1), ('2', 2), ('3', 3)), 0, ('1', 1)),
        ((('1', 1), ('2', 2), ('3', 3)), 1, ('2', 2)),
        ((('1', 1), ('2', 2), ('3', 3)), 2, ('3', 3)),
    ),
)
def test_focused_getter(options, focused_index, exp_focused, make_ChoiceJob, mocker):
    job = make_ChoiceJob(name='foo', label='Foo', options=options)
    mocker.patch.object(type(job), 'focused_index', PropertyMock(return_value=focused_index))
    assert job.focused == exp_focused

@pytest.mark.parametrize(
    argnames='get_index_return_value, exp_focused_index',
    argvalues=(
        (None, 0),
        (0, 0),
        (123, 123),
    ),
)
def test_focused_setter(get_index_return_value, exp_focused_index, make_ChoiceJob, mocker):
    job = make_ChoiceJob(name='foo', label='Foo', options=('1', '2', '3'))

    mocks = Mock()
    mocks.attach_mock(mocker.patch.object(job, 'get_index', return_value=get_index_return_value), 'get_index')
    mocks.attach_mock(mocker.patch.object(job.signal, 'emit'), 'emit')

    job.focused = 'something'
    assert job.focused_index == exp_focused_index
    assert mocks.mock_calls == [
        call.get_index('something'),
        call.emit('dialog_updated', job),
    ]


def test_autodetected_index(make_ChoiceJob):
    job = make_ChoiceJob(name='foo', label='Foo', options=('1', '2', '3'))
    assert job.autodetected_index is job._autodetected_index
    delattr(job, '_autodetected_index')
    assert job.autodetected_index is None


@pytest.mark.parametrize(
    argnames='options, autodetected_index, exp_autodetected',
    argvalues=(
        ((('1', 1), ('2', 2), ('3', 3)), None, None),
        ((('1', 1), ('2', 2), ('3', 3)), 0, ('1', 1)),
        ((('1', 1), ('2', 2), ('3', 3)), 1, ('2', 2)),
        ((('1', 1), ('2', 2), ('3', 3)), 2, ('3', 3)),
    ),
)
def test_autodetected_getter(options, autodetected_index, exp_autodetected, make_ChoiceJob, mocker):
    job = make_ChoiceJob(name='foo', label='Foo', options=options)
    mocker.patch.object(type(job), 'autodetected_index', PropertyMock(return_value=autodetected_index))
    assert job.autodetected == exp_autodetected

@pytest.mark.parametrize(
    argnames='get_index_return_value, exp_autodetected_index',
    argvalues=(
        (None, None),
        (0, 0),
        (123, 123),
    ),
)
def test_autodetected_setter(get_index_return_value, exp_autodetected_index, make_ChoiceJob, mocker):
    job = make_ChoiceJob(name='foo', label='Foo', options=('1', '2', '3'))

    mocks = Mock()
    mocks.attach_mock(mocker.patch.object(job, 'get_index', return_value=get_index_return_value), 'get_index')
    mocks.attach_mock(mocker.patch.object(job.signal, 'emit'), 'emit')

    job.autodetected = 'something'
    assert job.autodetected_index == exp_autodetected_index
    assert mocks.mock_calls == [
        call.get_index('something'),
        call.emit('dialog_updated', job),
    ]


def test_choice_property(make_ChoiceJob):
    job = make_ChoiceJob(name='foo', label='Foo', options=(('a', 1), ('b', 2), ('c', 3)))
    assert job.choice is None
    job._choice = 'mychoice'
    assert job.choice is job._choice


@pytest.mark.parametrize(
    argnames='choice_attribute, choice_return_value, exp_result',
    argvalues=(
        (None, ('asdf', 123), 123),
        ('mychoice', None, RuntimeError('foo: Choice was already made: mychoice')),
    ),
    ids=lambda v: str(v),
)
def test_set_choice(choice_attribute, choice_return_value, exp_result, make_ChoiceJob, mocker):
    job = make_ChoiceJob(name='foo', label='Foo', options=('ignored', 'options'))
    if choice_attribute is not None:
        job._choice = choice_attribute
    mocker.patch.object(job, 'get_option', return_value=choice_return_value)

    if isinstance(exp_result, Exception):
        with pytest.raises(type(exp_result), match=rf'^{re.escape(str(exp_result))}$'):
            job._set_choice('something')
    else:
        job._set_choice('something')
        assert job._choice == exp_result
        assert job.get_option.call_args_list == [call('something')]


@pytest.mark.asyncio
async def test_make_choice(make_ChoiceJob, mocker):
    job = make_ChoiceJob(name='foo', label='Foo', options=('ignored', 'options'))
    mocker.patch.object(job, 'get_option', return_value=('asdf', 123))

    job.start()
    job.make_choice('something')
    await job.wait()

    assert job.output == ('asdf',)
    assert job.choice == 123
    assert job.is_finished


def test_set_label(make_ChoiceJob):
    job = make_ChoiceJob(name='foo', label='Foo', options=(('a', 1), ('b', 2), ('c', 3)))
    cb = Mock()
    job.signal.register('dialog_updated', cb)

    job.set_label('a', 'the a')
    assert job.options == [('the a', 1), ('b', 2), ('c', 3)]
    assert cb.call_args_list == [call(job)]

    job.set_label(2, 'the b')
    assert job.options == [('the a', 1), ('the b', 2), ('c', 3)]
    assert cb.call_args_list == [call(job), call(job)]

    job.set_label(('c', 3), 'the c')
    assert job.options == [('the a', 1), ('the b', 2), ('the c', 3)]
    assert cb.call_args_list == [call(job), call(job), call(job)]

    job.set_label('d', 'the d')
    assert job.options == [('the a', 1), ('the b', 2), ('the c', 3)]
    assert cb.call_args_list == [call(job), call(job), call(job)]


@pytest.mark.parametrize(
    argnames='autodetected, focused, exp_autodetected, exp_focused',
    argvalues=(
        (None, None, None, ('a', 'a')),
        ('b', None, ('b', 'b'), ('b', 'b')),
        ('b', 'c', ('b', 'b'), ('c', 'c')),
    ),
    ids=lambda v: repr(v),
)
def test_initialize_sets_properties(autodetected, focused, exp_autodetected, exp_focused, make_ChoiceJob, mocker):
    job = make_ChoiceJob(name='foo', label='Foo', options=('a', 'b', 'c'),
                         autodetected=autodetected, focused=focused)
    assert job.options == [('a', 'a'), ('b', 'b'), ('c', 'c')]
    assert job.autodetected == exp_autodetected
    assert job.focused == exp_focused

@pytest.mark.asyncio
async def test_initialize_sets_choice_property_when_output_is_cached(make_ChoiceJob):
    job1 = make_ChoiceJob(name='foo', label='Foo', options=(('a', 1), ('b', 2), ('c', 3)), ignore_cache=False)
    job1.start()
    job1.make_choice('b')
    await job1.wait()
    assert job1.is_finished
    assert job1.output == ('b',)
    assert job1.choice == 2

    # Running the same job again should finish it immediately and set `choice`
    # as well as `output`
    job2 = make_ChoiceJob(name='foo', label='Foo', options=(('a', 1), ('b', 2), ('c', 3)), ignore_cache=False)
    job2.start()
    await job2.wait()
    assert job2.is_finished
    assert job2.output == ('b',)
    assert job2.choice == 2


@pytest.mark.parametrize(
    argnames='autodetect, autofinish, exp_autodetected, exp_finished',
    argvalues=(
        # No autodetection and autofinish
        (None, True, None, False),

        # No autodetection and not autofinish
        (None, False, None, False),

        # Successful autodetection and autofinish
        (Mock(return_value='a'), True, ('a', 'a'), True),
        (Mock(return_value='b'), True, ('b', 'b'), True),
        (Mock(return_value='c'), True, ('c', 'c'), True),

        # Successful autodetection and not autofinish
        (Mock(return_value='a'), False, ('a', 'a'), False),
        (Mock(return_value='b'), False, ('b', 'b'), False),
        (Mock(return_value='c'), False, ('c', 'c'), False),

        # Failed autodetection and autofinish
        (Mock(return_value=None), True, None, False),

        # Failed autodetection and not autofinish
        (Mock(return_value=None), False, None, False),
    ),
    ids=lambda v: repr(v),
)
@pytest.mark.asyncio
async def test_run(autodetect, autofinish, exp_autodetected, exp_finished, make_ChoiceJob, mocker):
    job = make_ChoiceJob(
        name='foo',
        label='Foo',
        options=('a', 'b', 'c'),
        focused='b',
        autodetect=autodetect,
        autofinish=autofinish,
    )

    mocks = Mock()
    mocks.attach_mock(
        mocker.patch.object(job, '_call_autodetect', return_value=(
            autodetect.return_value
            if autodetect else
            None
        )),
        '_call_autodetect',
    )
    mocks.attach_mock(mocker.patch.object(job, 'make_choice'), 'make_choice')
    mocks.attach_mock(mocker.patch.object(job, 'finalization'), 'finalization')

    job.signal.register('autodetecting', mocks.autodetecting)
    job.signal.register('autodetected', mocks.autodetected)

    # Check state before job is running
    assert job.autodetected is None
    assert job.focused == ('b', 'b')
    assert not job.is_finished
    originally_focused = job.focused

    await job.run()

    # Check state after job is finished
    assert job.autodetected == exp_autodetected
    assert job.focused == exp_autodetected or originally_focused

    exp_calls = []
    exp_calls.append(call.autodetecting())
    if autodetect:
        exp_calls.append(call._call_autodetect())
    exp_calls.append(call.autodetected())
    if exp_autodetected and exp_finished:
        exp_calls.append(call.make_choice(exp_autodetected))
    exp_calls.append(call.finalization())

    assert mocks.mock_calls == exp_calls


@pytest.mark.parametrize(
    argnames='autodetect, exp_result',
    argvalues=(
        (None, None),
        (AsyncMock(return_value='autodetected'), 'autodetected'),
        (Mock(return_value='autodetected'), 'autodetected'),
        ('wat', RuntimeError("Bad autodetect value: 'wat'")),
        (0, RuntimeError("Bad autodetect value: 0")),
    ),
    ids=lambda v: repr(v),
)
@pytest.mark.asyncio
async def test__call_autodetect(autodetect, exp_result, make_ChoiceJob, mocker):
    # TODO: Remove when Python 3.9 is no longer supported.
    # inspect.iscoroutinefunction() returns False for AsynMock() instances in
    # Python 3.9.
    if sys.version_info < (3, 10, 0):
        if isinstance(autodetect, AsyncMock):
            async def autodetect_proper(job, _return_value=autodetect.return_value):
                return _return_value

            autodetect = autodetect_proper

    job = make_ChoiceJob(
        name='foo',
        label='Foo',
        options=('a', 'b', 'c'),
        autodetect=autodetect,
    )

    if isinstance(exp_result, BaseException):
        with pytest.raises(type(exp_result), match=rf'^{re.escape(str(exp_result))}$'):
            await job._call_autodetect()
    else:
        return_value = await job._call_autodetect()
        assert return_value == exp_result
