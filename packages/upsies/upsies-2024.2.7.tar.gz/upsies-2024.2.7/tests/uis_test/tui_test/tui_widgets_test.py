import asyncio
import sys
from unittest.mock import Mock, call

import pytest

from upsies.uis.tui import widgets


@pytest.mark.asyncio
async def test_ActivityIndicator_active_property(mocker):
    mocker.patch('upsies.uis.tui.widgets.ActivityIndicator._iterate')
    ai = widgets.ActivityIndicator()

    assert ai.active is False
    assert ai._iterate.call_args_list == []
    assert ai._iterate_task is None

    ai.active = 1
    assert ai.active is True
    assert ai._iterate.call_args_list == [call()]
    assert isinstance(ai._iterate_task, asyncio.Task)
    iterate_task = ai._iterate_task

    ai.active = 0
    assert ai.active is False
    assert ai._iterate.call_args_list == [call()]
    assert ai._iterate_task is None
    if sys.version_info >= (3, 11, 0):
        assert iterate_task.cancelling()
    ai.active = False
    assert ai.active is False
    assert ai._iterate.call_args_list == [call()]
    assert ai._iterate_task is None

    ai.active = 'yes'
    assert ai.active is True
    assert ai._iterate.call_args_list == [call(), call()]
    assert isinstance(ai._iterate_task, asyncio.Task)
    iterate_task = ai._iterate_task
    ai.active = True
    assert ai.active is True
    assert ai._iterate.call_args_list == [call(), call()]
    assert isinstance(ai._iterate_task, asyncio.Task)

    ai.active = ''
    assert ai.active is False
    assert ai._iterate.call_args_list == [call(), call()]
    assert ai._iterate_task is None
    if sys.version_info >= (3, 11, 0):
        assert iterate_task.cancelling()


@pytest.mark.asyncio
async def test_ActivityIndicator_enable_disable(mocker):
    ai = widgets.ActivityIndicator()
    mocker.patch.object(ai, '_iterate')
    assert ai.active is False
    ai.enable()
    assert ai.active is True
    ai.disable()
    assert ai.active is False


def test_ActivityIndicator_format_property(mocker):
    mocker.patch('upsies.uis.tui.widgets.ActivityIndicator._iterate')
    ai = widgets.ActivityIndicator()
    assert ai.format == '{indicator}'
    ai.format = '[{indicator}]'
    assert ai.format == '[{indicator}]'


def test_ActivityIndicator_text_property():
    ai = widgets.ActivityIndicator()
    mock_text = Mock()
    ai._text = mock_text
    assert ai.text is mock_text


@pytest.mark.asyncio
async def test_ActivityIndicator_iterate():

    def callback(text):
        print(text, exp_texts)
        if len(exp_texts) == 1:
            iterate_task.cancel()
        assert text == exp_texts.pop(0)

    callback = Mock(side_effect=callback)

    ai = widgets.ActivityIndicator(
        interval=0,
        format=':{indicator}:',
        states=('a', 'b', 'c'),
        callback=callback,
    )

    exp_texts = [':a:', ':b:', ':c:', ':a:', ':b:', ':c:']
    assert ai.text == exp_texts.pop(0)
    exp_callback_calls = [call.callback(txt) for txt in exp_texts]

    iterate_task = asyncio.get_running_loop().create_task(ai._iterate())
    with pytest.raises(asyncio.CancelledError):
        await iterate_task

    assert callback.call_args_list == exp_callback_calls


@pytest.mark.asyncio
async def test_ActivityIndicator_iterate_without_callback():
    ai = widgets.ActivityIndicator(
        interval=0,
        format='<{indicator}>',
        states=('a', 'b', 'c'),
    )

    exp_texts = ['<a>', '<b>', '<c>', '<a>', '<b>', '<c>']
    assert ai.text == exp_texts.pop(0)

    async def check_text_loop():
        while exp_texts:
            print(ai.text, exp_texts)
            assert ai.text == exp_texts.pop(0)
            # Yield control back to ActivityIndicator._iterate() so it can
            # change the text property to the next value.
            await asyncio.sleep(0)

        print('cancelling', iterate_task)
        iterate_task.cancel()

    iterate_task = asyncio.get_running_loop().create_task(ai._iterate())

    with pytest.raises(asyncio.CancelledError):
        await asyncio.gather(
            check_text_loop(),
            iterate_task,
        )


def test_ActivityIndicator___pt_container__():
    ai = widgets.ActivityIndicator()
    assert ai.__pt_container__() is ai.container
