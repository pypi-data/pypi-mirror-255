"""
Custom job that provide the result of a coroutine
"""

import collections

from . import JobBase

import logging  # isort:skip
_log = logging.getLogger(__name__)


class CustomJob(JobBase):
    """Wrapper around coroutine function"""

    @property
    def name(self):
        return self._name

    @property
    def label(self):
        return self._label

    def initialize(self, *, name, label, worker, catch=()):
        """
        Set internal state

        :param name: Name for internal use
        :param label: Name for user-facing use
        :param worker: Coroutine function that takes the job instance as a
            positional argument and returns this job's output

            If `worker` returns any iterable that isn't a string, each item is
            passed to :attr:`send`.

            If `worker` returns `None`, it is interpreted as "no output" and the
            job fails. An empty string is valid output and does not mean the job
            failed.
        :param catch: Sequence of :class:`Exception` classes to catch from
            `worker` and pass to :meth:`~.JobBase.error`

        This job finishes when `worker` returns.

        :class:`~.asyncio.CancelledError` from `worker` is ignored. Any other
        exceptions are passed to :meth:`~.JobBase.exception`.
        """
        self._name = str(name)
        self._label = str(label)
        self._worker = worker
        self._expected_exceptions = tuple(catch)

    async def run(self):
        try:
            result = await self._worker(self)
        except self._expected_exceptions as e:
            self.error(e)
        else:
            self._handle_worker_result(result)

    def _handle_worker_result(self, result):
        if result is not None:
            if (
                    not isinstance(result, str)
                    and isinstance(result, collections.abc.Iterable)
            ):
                # Worker returned list/tuple/etc
                for result in result:
                    self.send(result)
            else:
                self.send(result)
