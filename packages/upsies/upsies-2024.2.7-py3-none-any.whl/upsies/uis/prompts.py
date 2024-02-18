"""
Generic user dialogs

Prompts take arbitrary keyword arguments that are used by the user interface
to create the dialog.

When the user makes a choice, the user interface must pass it on to the prompt
object via :meth:`~.Prompt.set_result`. The prompt object then takes care of
passing the result to any callbacks.
"""

import asyncio

import logging  # isort:skip
_log = logging.getLogger(__name__)


class Prompt:
    """
    Base class of all prompts

    Every prompt takes at least a sequence of callbacks. Any other keyword
    arguments are specified by the subclass. The user interface can access
    them as :attr:`parameters`.
    """

    def __init__(self, *, callbacks=(), **parameters):
        self._callbacks = list(callbacks)
        self._parameters = parameters
        self._result_arrived = asyncio.Event()

    @property
    def parameters(self):
        """Keyword arguments from instantiation (except for `callbacks`)"""
        return self._parameters

    async def wait(self):
        """Block until :meth:`set_result` is called"""
        _log.debug('___ Waiting for %s ...', type(self).__name__)
        await self._result_arrived.wait()
        _log.debug('___ Waiting for %s', type(self).__name__)

    def on_result(self, callback):
        """Schedule `callback` to be called when :meth:`set_result` is called"""
        self._callbacks.append(callback)

    def set_result(self, result):
        """
        Take the result from the user dialog and pass it on to any previously
        scheduled callbacks
        """
        _log.debug('___ Setting result: %r', result)

        # Call callbacks
        for callback in self._callbacks:
            _log.debug('___ Reporting result to %r: %r', callback, result)
            callback(result)

        # Unblock any wait() calls
        self._result_arrived.set()

    def __repr__(self):
        arguments = []
        if self._parameters:
            arguments.append(', '.join((
                f'{k}={v!r}'
                for k, v in self._parameters.items()
            )))
        arguments.append(f'callbacks={self._callbacks}')
        arguments_string = ', '.join(arguments)
        return f'{type(self).__name__}({arguments_string})'


class RadioListPrompt(Prompt):
    """
    Pick one of two or more options

    :param options: Sequence of choices
    :param question: Question to show alongside the options or `None`
    """

    def __init__(self, *, callbacks, options, question=None):
        super().__init__(callbacks=callbacks, options=options, question=question)
