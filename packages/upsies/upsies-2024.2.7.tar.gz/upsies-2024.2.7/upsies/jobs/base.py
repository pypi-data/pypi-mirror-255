"""
Abstract base class for jobs
"""

import abc
import asyncio
import collections
import functools
import os
import pickle
import re

import unidecode

from .. import constants, uis, utils

import logging  # isort:skip
_log = logging.getLogger(__name__)


def raise_if_finished(method):
    """
    Decorator for :class:`~.JobBase` methods that raises :class:`RuntimeError`
    if the job :attr:`~.JobBase.was_started` and :attr:`~.JobBase.is_finished`
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.was_started and self.is_finished:
            raise RuntimeError(f'Do not call {method.__name__} if job is already finished: {self.name}')
        else:
            return method(self, *args, **kwargs)

    return wrapper


def raise_if_not_started(method):
    """
    Decorator for :class:`~.JobBase` methods that raises :class:`RuntimeError`
    if the job :attr:`~.JobBase.was_started`
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.was_started:
            raise RuntimeError(f'Do not call {method.__name__} before job is started: {self.name}')
        else:
            return method(self, *args, **kwargs)

    return wrapper


class JobBase(abc.ABC):
    """
    Base class for all jobs

    :param str home_directory: Directory that is used to store created files
    :param str cache_directory: Directory that is used to cache output
    :param str cache_id: See :attr:`cache_id`
    :param str ignore_cache: Whether cached output and previously created files
        should not be re-used
    :param bool no_output_is_ok: Whether the job can succeed without any
        :attr:`output`
    :param bool hidden: Whether to hide the job's output in the UI
    :param bool autostart: Whether this job is started automatically
    :param precondition: Callable that gets no arguments and returns whether
        this job is enabled or disabled
    :param prejobs: Sequence of :attr:`prerequisite jobs <prejobs>`
    :param presignals: Mapping of :class:`jobs <JobBase>` to sequence of signals
        (see :meth:`presignal`)
    :param callbacks: Mapping of :attr:`signal` names to callable or sequence of
        callables to :meth:`~.signal.Signal.register` for that signal

    Any additional keyword arguments are passed on to :meth:`initialize`.

    If possible, arguments should be validated before creating a job instance.
    This means we can fail early before any sibling jobs have started doing
    expensive work (e.g. torrent creation) that has to be cancelled.
    """

    @property
    @abc.abstractmethod
    def name(self):
        """Internal name (e.g. for the cache file name)"""

    @property
    @abc.abstractmethod
    def label(self):
        """User-facing name"""

    @property
    def home_directory(self):
        """
        Directory that is used to store files (e.g. generated screenshots,
        torrent files, etc) or empty string

        The directory is guaranteed to exist.
        """
        if self._home_directory and not os.path.exists(self._home_directory):
            utils.fs.mkdir(self._home_directory)
        return self._home_directory

    @functools.cached_property
    def cache_directory(self):
        """
        Path to existing directory that stores :attr:`cache_file`

        Subclasses may use this directory for storing custom cache files.

        This directory is guaranteed to exist.
        """
        if not os.path.exists(self._cache_directory):
            utils.fs.mkdir(self._cache_directory)
        return self._cache_directory

    @property
    def ignore_cache(self):
        """Whether cached output and previously created files should not be re-used"""
        return self._ignore_cache

    @property
    def no_output_is_ok(self):
        """Whether the job can succeed without any :attr:`output`"""
        return self._no_output_is_ok

    @property
    def hidden(self):
        """
        Whether to hide this job's output in the UI

        This can also be set to a callable that takes no arguments and returns
        a :class:`bool` value.
        """
        if callable(self._hidden):
            return bool(self._hidden())
        else:
            return bool(self._hidden)

    @hidden.setter
    def hidden(self, hidden):
        self._hidden = hidden

    @property
    def kwargs(self):
        """Keyword arguments from instantiation as :class:`dict`"""
        return self._kwargs

    @property
    def autostart(self):
        """
        Whether this job is started automatically by the UI

        The UI must check this value before calling :attr:`start`.

        If this value is falsy, :meth:`start` must be called manually.
        """
        return self._autostart

    @property
    def precondition(self):
        """
        Callable that gets no arguments and returns whether this job should
        be :meth:`started <start>`

        See also :attr:`is_enabled`.
        """
        return self._precondition

    @precondition.setter
    def precondition(self, function):
        if self.was_started:
            raise RuntimeError('Cannot set precondition after job has been started')

        if not callable(function):
            raise TypeError(f'Not callable: {function!r}')
        self._precondition = function

    @property
    def prejobs(self):
        """
        Sequence of prerequisite :class:`jobs <upsies.jobs.base.JobBase>`

        All prejobs must be either :attr:`finished <is_finished>` or
        :attr:`disabled <is_enabled>` before this job can start.

        See also :attr:`is_enabled`.
        """
        return self._prejobs

    @prejobs.setter
    def prejobs(self, prejobs):
        if self.was_started:
            raise RuntimeError('Cannot set prejobs after job has been started')
        self._prejobs = tuple(prejobs)

    def presignal(self, job, signal):
        """
        Do not :attr:`enable <is_enabled>` this job until `job` :attr:`emits
        <signal>` `signal`

        When `job` emits `signal`, this job is enabled internally (so it can be
        :meth:`started <start>`) and the `refresh_job_list` :attr:`signal` is
        emitted.

        The payload of `signal` is discarded. Register another callback for
        `signal` if it is needed.

        See also :attr:`is_enabled`.
        """
        if self.was_started:
            raise RuntimeError('Cannot set presignal after job has been started')

        # Indicate we are waiting for signal
        self.presignals[job][signal] = False

        def presignal_handler(*args, **kwargs):
            self.presignals[job][signal] = True
            # If all presignals were emitted from the expected `job`, we tell
            # the UI to check if the we are now ready to get started.
            if all(self.presignals[job].values()):
                self.signal.emit('refresh_job_list')

        job.signal.register(signal, presignal_handler)

    @functools.cached_property
    def presignals(self):
        return collections.defaultdict(lambda: {})

    @property
    def is_enabled(self):
        """
        Whether this job is allowed to :meth:`start`

        A job is enabled if :attr:`precondition` returns `True`, all
        :attr:`prejobs` are either finished or disabled and all
        :func:`presignal`\\ s have been emitted.

        This property must be checked by the UI every time any job finishes and
        when the `refresh_job_list` :attr:`signal` is emitted. If this property
        is `True`, this job must be :meth:`started <start>` and displayed
        (unless it is :attr:`hidden`).
        """
        return (
            # Prejobs
            all(
                (prejob.is_finished or not prejob.is_enabled)
                for prejob in self.prejobs
            )
            # Presignals
            and all(
                was_emitted
                for job_, presignals in self.presignals.items()
                for signal_, was_emitted in presignals.items()
            )
            # Precondition
            and self.precondition()
        )

    @property
    def signal(self):
        """
        :class:`~.signal.Signal` instance

        The following signals are added by the base class. Subclasses can add
        their own signals.

        ``running``
            Emitted when :meth:`run` is called by :meth:`start`. Registered
            callbacks get the job instance as a positional argument.

        ``finished``
            Emitted when a job :attr:`is_finished`. A job is finished when all
            its tasks are done or cancelled or if cached output from a previous
            run is successfully read. Registered callbacks get the job
            instance as a positional argument.

        ``output``
            Emitted when :meth:`send` is called or when output is read from
            cache. Registered callbacks get the value passed to :meth:`send` as
            a positional argument.

        ``info``
            Emitted when :attr:`info` is set. Registered callbacks get the new
            :attr:`info` as a positional argument.

        ``warning``
            Emitted when :meth:`warn` is called. Registered callbacks get the
            value passed to :meth:`warn` as a positional argument.

        ``error``
            Emitted when :meth:`error` is called. Registered callbacks get the
            value passed to :meth:`error` as a positional argument.

        ``prompt``
            Emitted when :meth:`add_prompt` is called. Registered callbacks
            get the :class:`~.Prompt` instance passed to :meth:`add_prompt` as
            a positional argument. The user interface MUST subscribe to this
            signal and present dialogs to the user when it is emitted.

        ``refresh_job_list``
            Emitted when the user interface should refresh the job list,
            remove any finished jobs, start the next interactive job, etc. The
            UI usually only does this when a job finishes. This signal allows
            a job to force the refresh immediately. Registered callbacks get
            no arguments.
        """
        return self._signal

    def __init__(self, *, home_directory=None, cache_directory=None, cache_id='',
                 ignore_cache=False, no_output_is_ok=False, hidden=False, autostart=True,
                 precondition=None, prejobs=(), presignals={}, callbacks={},
                 **kwargs):
        # Internal state
        self._run_was_called = False
        self._was_started = False
        self._exception = None
        self._output = []
        self._warnings = []
        self._errors = []
        self._info = ''
        self._tasks = []
        self._finalize_event = None

        # Arguments
        self._kwargs = kwargs
        self._home_directory = home_directory if home_directory else ''
        self._cache_directory = cache_directory if cache_directory else constants.DEFAULT_CACHE_DIRECTORY
        self._cache_id = cache_id
        self._ignore_cache = bool(ignore_cache)
        self._no_output_is_ok = bool(no_output_is_ok)
        self._hidden = hidden
        self._autostart = bool(autostart)
        self.precondition = precondition if precondition is not None else (lambda: True)
        self.prejobs = prejobs

        self._signal = utils.signal.Signal(
            'running',
            'output',
            'info',
            'warning',
            'error',
            'finished',
            'prompt',
            'refresh_job_list',
        )
        self._signal.register('output', lambda output: self._output.append(str(output)))
        self._signal.register('warning', lambda warning: self._warnings.append(warning))
        self._signal.register('error', lambda error: self._errors.append(error))
        self._signal.record('output')

        self.initialize(**kwargs)

        # Add signal callbacks after `initialize` had the chance to add custom
        # signals.
        for signal_name, callback in callbacks.items():
            if callable(callback):
                self._signal.register(signal_name, callback)
            else:
                for cb in callback:
                    self._signal.register(signal_name, cb)

        # Register required signals from other jobs
        for job, signals in presignals.items():
            for signal in signals:
                self.presignal(job, signal)

    def initialize(self):
        """
        Called by :meth:`__init__` with additional keyword arguments

        This method should handle its arguments and return quickly.
        """

    @abc.abstractmethod
    async def run(self):
        """
        Do the work

        This method is called by :meth:`start`. Its coroutine is passed to
        :meth:`add_task`.

        Any keyword arguments passed to :meth:`initialize` are available via
        :attr:`kwargs`.

        The job :attr:`is_finished` when all :meth:`added tasks
        <upsies.jobs.base.JobBase.add_task>` are done or cancelled. (See also
        :meth:`finalize` and :meth:`finalization`.)

        This method may call :meth:`add_task` if more tasks are required.
        """

    def start(self):
        """
        Load cached output if available, otherwise call :meth:`run`

        This method must be called by the UI if :attr:`autostart` is `True`.

        Nothing is done if the job :attr:`is_finished` or not
        :attr:`enabled <upsies.jobs.base.JobBase.is_enabled>`.

        :raise RuntimeError: if this job is already started or if reading from
            cache file fails unexpectedly (e.g. existing but unreadable cache
            file)
        """
        if not self.is_enabled:
            # Job is waiting for prejob, presignal, precondition, etc
            _log.debug('%s: Not executing disabled job', self.name)
            # _log.debug(
            #     '%s: Not executing disabled job: prejobs=%s, presignals=%s, precondition=%s',
            #     self.name,
            #     [f'{prejob.name}:' + 'finished' if prejob.is_finished else 'running' for prejob in self.prejobs],
            #     self.presignals,
            #     self.precondition(),
            # )
        else:
            if self.was_started:
                raise RuntimeError(f'start() was already called: {self.name}')
            else:
                self._was_started = True

                cache_was_read = self._read_cache()
                if cache_was_read:
                    _log.debug('%s: Using cached output', self.name)
                    self._finish()
                else:
                    _log.debug('%s: Running', self.name)
                    self._run_was_called = True
                    # Because self._tasks is empty and self.was_started is True,
                    # we are technically finished (see is_finished property), so
                    # we need to add the first task with _add_task(), which is
                    # allowed to add tasks while the job is finished.
                    self._add_task(self.run())
                    self.signal.emit('running', self)

    @property
    def was_started(self):
        """
        Whether :meth:`start` was called while this job :attr:`is_enabled`

        .. note:: This does not mean that :meth:`run` was called. A job is
                  also considered to be started if output is read from cache.
        """
        return self._was_started

    # Adding tasks before start() is called is problematic because start()
    # determines if we are using cached output. If we are using cached output,
    # the job is finished immediately by start() and no added task is going to
    # be awaited.
    @raise_if_not_started
    @raise_if_finished
    def add_task(self, coro, callback=None):
        """
        Run asynchronous coroutine in background task

        The job :attr:`is_finished` when all added tasks are done or cancelled.

        Any exceptions from `coro` are raised by :meth:`wait` or made
        available via :attr:`raised`.

        :param coro: Any awaitable object
        :param callback: Callable that is called with the return value or
            exception of `coro`

            `callback` is not called if the task was cancelled.

        :return: :class:`asyncio.Task` instance
        """
        return self._add_task(coro, callback=callback)

    def _add_task(self, coro, callback=None):
        def callback_(task):
            try:
                # Remove task reference (this may finish the job)
                self._tasks.remove(task)

                # _finish() MUST be called. We don't want to do that in wait()
                # because we don't want to make calling wait() mandatory. Doing
                # it via add_done_callback() has the upside that it is
                # guaranteed to run. The downside is that this code is running
                # after every task is done, but it's cheap enough.
                if self.is_finished:
                    self._finish()

                # Get return value or exception from task.
                result = exception = None
                try:
                    exception = task.exception()
                except asyncio.CancelledError:
                    _log.debug('%s: Task was cancelled: %r', self.name, task)
                    task_was_cancelled = True
                else:
                    task_was_cancelled = False
                    if exception:
                        # Store exception to raise it later, e.g. in wait().
                        self.exception(exception)
                    else:
                        # Getting the result should not raise if
                        # task.exception() returned None.
                        result = task.result()

                _log.debug('%s: %d Remaining tasks', self.name, len(self._tasks))
                # for task in self._tasks:
                #     _log.debug('   - %r', task)

                # Unless task was cancelled, call callback and store its exception.
                if callback and not task_was_cancelled:
                    _log.debug('%s: Calling %s callback %r with %r', self.name,
                               task.get_coro().__qualname__, callback, result or exception)
                    try:
                        callback(result or exception)
                    except BaseException as e:
                        _log.debug('%s: Handling exception from callback %r: %r', self.name, callback, e)
                        self.exception(e)

            except BaseException as e:
                # Exceptions from task callbacks seem to be completely ignored,
                # even if asyncio.get_event_loop().set_exception_handler() is
                # set.
                self.exception(e)

        task = utils.run_task(coro, callback=callback_)
        self._tasks.append(task)
        _log.debug('%s: Added task: %r', self.name, task)
        return task

    @raise_if_not_started
    @raise_if_finished
    def add_prompt(self, prompt):
        """
        Create a dialog in the user interface

        :param prompt: :class:`~.prompts.Prompt` object that specifies the
            dialog and handles callbacks
        """
        _log.debug('%s: Adding prompt: %r', self.name, prompt)
        assert isinstance(prompt, uis.prompts.Prompt), f'Not a Prompt instance: {prompt!r}'
        self.add_task(prompt.wait())
        self.signal.emit('prompt', prompt)

    @raise_if_not_started
    async def wait(self):
        """
        Block until all :meth:`added tasks
        <upsies.jobs.base.JobBase.add_task>` are done or cancelled

        :raise: first exception from any :meth:`added task
            <upsies.jobs.base.JobBase.add_task>`
        """
        # Every time we've awaited all tasks, we must check if someone added
        # more tasks.
        while self._tasks:
            # Exceptions from tasks are handled in the task callback (see
            # _add_task()). We can safely ignore any exception raised from tasks
            # here.
            #
            # It is especially important to ignore asyncio.CancelledError
            # because jobs can cancel their tasks as they please and let us take
            # care of the gory bits.
            exceptions = await asyncio.gather(*self._tasks, return_exceptions=True)
            for result in exceptions:
                if isinstance(result, BaseException):
                    _log.debug('%s: Ignoring exception while gathering tasks: %r', self.name, result)

        # If anyone is waiting for finalize() to be called, we are not finished
        # until it is.
        if self._finalize_event:
            await self._finalize_event.wait()

        if self.raised:
            raise self.raised

    def _finish(self):
        # This function must be called when all tasks are done and finalize()
        # was called if anyone is awaiting finalization(). This function must be
        # called regardless of success or raised exceptions.
        _log.debug('%s: Finishing', self.name)

        # Some sanity checks
        assert self.is_finished, f'Job is not finished yet: {self._finalize_event=}, {self._tasks=}'
        emitted = dict(self.signal.emitted)
        assert 'finished' not in emitted, f'"finished" signal was already emitted: {emitted["finished"]}'

        _log.debug('%s: Emitting finished signal', self.name)
        self.signal.emit('finished', self)
        _log.debug('%s: Emitted finished signal', self.name)

        self._write_cache()

    def terminate(self):
        """
        Cancel all :meth:`added tasks <upsies.jobs.base.JobBase.add_task>`

        .. note: The tasks are still running after this method returns. If you
                 need to wait for this job to finish, call :meth:`wait`.

        .. note: If this method is called from a task, the calling task is not
                 cancelled. Therefore, any function that calls ``terminate()``
                 should return soon and must not rely on getting cancelled.
        """
        _log.debug('%s: Terminating', self.name)

        try:
            current_task = asyncio.current_task()
        except RuntimeError as e:
            if 'no running event loop' in str(e).casefold():
                current_task = None
            else:
                raise

        for task in self._tasks:
            if task is not current_task:
                _log.debug('%s: Cancelling %r', self.name, task)
                task.cancel()
            else:
                _log.debug('%s: Not cancelling myself: %r', self.name, task)

        # Calling terminate() means the job has failed in some way. If anyone is
        # awaiting finalization(), do not leave them hanging.
        if self._finalize_event:
            self.finalize()

    def finalize(self):
        """Unblock any calls awaiting :meth:`finalization` or :meth:`wait`"""
        # NOTE: It must be possible to call finalize() before awaiting
        #       finalization() (which then returns immediately).
        if not self._finalize_event:
            self._finalize_event = asyncio.Event()

        if not self._finalize_event.is_set():
            _log.debug('%s: Finalizing', self.name)
            self._finalize_event.set()
        else:
            _log.debug('%s: Already finalized', self.name)

    async def finalization(self):
        """
        Block until :meth:`finalize` is called

        This is useful for interactive jobs that don't have running tasks at
        all times. You can simply ``await self.finalization()`` in :meth:`run`
        and call :meth:`finalize` from anywhere to finish the job.

        .. warning: It is important to await finalization in :meth:`run` or
            any other :meth:`added task <upsies.jobs.base.JobBase.add_task>`.
        """
        if not self._finalize_event:
            self._finalize_event = asyncio.Event()
        _log.debug('%s: Awaiting finalization', self.name)
        await self._finalize_event.wait()

    @property
    def is_finished(self):
        """
        Whether all tasks are done

        If :meth:`finalization` is awaited, :meth:`finalize` must also be
        called.

        Before this job is started, `None` is returned.
        """
        if self.was_started:
            return (
                # All tasks are done and removed by their callbacks.
                len(self._tasks) <= 0
                and (
                    # Nobody is waiting for finalize() to be called.
                    not self._finalize_event
                    # Someone was waiting for finalize() to be called and it was
                    # called.
                    or (
                        self._finalize_event
                        and self._finalize_event.is_set()
                    )
                )
            )

    @property
    def exit_code(self):
        """
        `0` if job was successful, ``> 0`` otherwise,
        `None` before job :attr:`is_finished`
        """
        if self.is_finished:
            if self.errors or self.raised:
                return 1
            elif not self.output and not self.no_output_is_ok:
                return 1
            else:
                return 0

    @raise_if_not_started
    @raise_if_finished
    def send(self, output):
        """
        Append `output` to :attr:`output` and emit ``output`` signal

        .. note:: All output is converted to :class:`str`.
        """
        self.signal.emit('output', str(output))

    @property
    def output(self):
        """Immutable sequence of strings passed to :meth:`send`"""
        return tuple(self._output)

    @property
    def info(self):
        """
        String that is only displayed while the job is running and not part of the
        job's output

        Setting this property emits the ``info`` signal.
        """
        return self._info

    @info.setter
    def info(self, info):
        self._info = str(info)
        self.signal.emit('info', info)

    def warn(self, warning):
        """Append `warning` to :attr:`warnings` and emit ``warning`` signal"""
        self.signal.emit('warning', str(warning))

    @property
    def warnings(self):
        """
        Sequence of non-critical error messages the user can override or resolve

        Unlike :attr:`errors`, warnings do not imply failure.
        """
        return tuple(self._warnings)

    def clear_warnings(self):
        """Empty :attr:`warnings`"""
        self._warnings.clear()

    def error(self, error):
        """
        Append `error` to :attr:`errors`, emit ``error`` signal and
        :meth:`terminate` this job
        """
        self.signal.emit('error', error)
        _log.debug('%s: Terminating because: %r', self.name, error)
        self.terminate()

    @property
    def errors(self):
        """
        Sequence of critical errors (strings or exceptions)

        By default, :attr:`exit_code` is non-zero if any errors were reported.
        """
        return tuple(self._errors)

    def exception(self, exception):
        """
        Make `exception` available as :attr:`raised` unless it is already set

        .. warning:: This method is mostly for internal use. Setting an exception
                     means you want to throw a traceback at the user.

        :param Exception exception: Exception instance (nothing is done if
            this argument is falsy)
        """
        if not exception:
            _log.debug('%s: Not setting exception: %r', self.name, exception)
        elif self._exception:
            _log.debug(
                '%s: Not setting exception: %r - Exception already set: %r',
                self.name, exception, self._exception,
            )
        else:
            _log.debug('%s: Setting exception: %r', self.name, exception)
            self._exception = exception
            self.terminate()

    @property
    def raised(self):
        """Exception passed to :meth:`exception`"""
        return self._exception

    def _write_cache(self):
        """
        Store recorded signals in :attr:`cache_file`

        Emitted signals are serialized with :meth:`_serialize_cached`.

        :raise RuntimeError: if writing :attr:`cache_file` fails
        """
        if (
                # Only cache if we have produced fresh output.
                self._run_was_called
                # We have nothing to cache if no signals fired.
                and self.signal.emissions
                # Do not cache failed jobs.
                and self.exit_code == 0
                # Do not cache if we have no place to store it.
                and self.cache_file
        ):
            emissions_serialized = self._serialize_cached(self.signal.emissions)
            _log.debug('%s: Caching emitted signals: %r', self.name, self.signal.emissions)
            try:
                with open(self.cache_file, 'wb') as f:
                    f.write(emissions_serialized)
                    f.write(b'\n')
            except OSError as e:
                msg = e.strerror if e.strerror else str(e)
                raise RuntimeError(f'Unable to write cache {self.cache_file}: {msg}')

    def _read_cache(self):
        """
        Read cached :attr:`~.signal.Signal.emissions` from :attr:`cache_file`

        Emitted signals are deserialized with :meth:`_deserialize_cached`.

        :raise RuntimeError: if :attr:`cache_file` exists and is unreadable

        :return: `True` if cache file was read, `False` otherwise
        """
        if not self._ignore_cache and self.cache_file and os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'rb') as f:
                    emissions_serialized = f.read()
            except OSError as e:
                msg = e.strerror if e.strerror else str(e)
                raise RuntimeError(f'Unable to read cache {self.cache_file}: {msg}')
            else:
                emissions_deserialized = self._deserialize_cached(emissions_serialized)
                _log.debug('%s: Replaying cached signals: %r', self.name, emissions_deserialized)
                if emissions_deserialized:
                    self.signal.replay(emissions_deserialized)
                    return True
        return False

    def _serialize_cached(self, emissions):
        """
        Convert emitted signals to cache format

        :param emissions: See :attr:`Signal.emissions`

        :return: :class:`bytes`
        """
        return pickle.dumps(emissions, protocol=0, fix_imports=False)

    def _deserialize_cached(self, emissions_serialized):
        """
        Convert return value of :meth:`_serialize_cached` back to emitted signals

        :param emissions_serialized: :class:`bytes` object

        :return: See :attr:`Signal.emissions`
        """
        return pickle.loads(emissions_serialized)

    _max_filename_len = 255

    @functools.cached_property
    def cache_file(self):
        """
        File path in :attr:`cache_directory` to store cached :attr:`output` in

        If this property returns `None`, cache is not read or written.
        """
        cache_id = self.cache_id
        if cache_id is None:
            return None
        elif not cache_id:
            filename = f'{self.name}.out'
        else:
            # Avoid file name being too long. 255 bytes seems common.
            # https://en.wikipedia.org/wiki/Comparison_of_file_systems#Limits
            max_len = self._max_filename_len - len(self.name) - len('..out')
            cache_id_str = self._cache_id_as_string(cache_id)
            if len(cache_id_str) > max_len:
                cache_id_str = ''.join((
                    cache_id_str[:int(max_len / 2 - 1)],
                    '…',
                    cache_id_str[-int(max_len / 2 - 1):],
                ))
            filename = f'{self.name}.{cache_id_str}.out'
            filename = utils.fs.sanitize_filename(filename)
        return os.path.join(self.cache_directory, filename)

    @functools.cached_property
    def cache_id(self):
        """
        Any object that makes a job's output unique

        If this property returns `None`, :attr:`cache_file` is not read or
        written.

        If this property returns any other object, it is converted to a string
        and appended to :attr:`name`. Multibyte characters and directory
        delimiters are replaced.

        By default, the `cache_id` argument from initialization is used, which
        is an empty string by default.
        """
        return self._cache_id

    _object_without_str_regex = re.compile(r'^<.*>$')

    def _cache_id_as_string(self, value):
        # Mapping (dict, etc)
        if isinstance(value, collections.abc.Mapping):
            return ','.join((
                f'{self._cache_id_as_string(k)}={self._cache_id_as_string(v)}'
                for k, v in value.items()
            ))

        # Iterable / Sequence (list, tuple, etc)
        elif isinstance(value, collections.abc.Iterable) and not isinstance(value, str):
            return ','.join((
                self._cache_id_as_string(v)
                for v in value
            ))

        # Use same cache file for absolute and relative paths if path exists
        elif (
                isinstance(value, (str, os.PathLike))
                and os.path.exists(value)
                and not os.path.isabs(value)
        ):
            return self._cache_id_as_string(os.path.realpath(value))

        else:
            value_string = str(value)
            if self._object_without_str_regex.search(value_string):
                # `value` has no proper string representation, which results in
                # random cache IDs. We don't want "<foo.bar object at 0x<RANDOM
                # ADRESS>>" in our cache ID.
                raise RuntimeError(f'{type(value)!r} has no string representation')
            else:
                # Convert non-ASCII characters to ASCII, i.e. use the same cache
                # file for "Foo" and "Föó" and "Fǫò".
                return unidecode.unidecode(value_string)


def raise_if_closed(method):
    """
    Decorator for :class:`~.QueueJobBase` methods that raises
    :class:`RuntimeError` if :attr:`~.QueueJobBase.close` was called
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.is_closed:
            raise RuntimeError(f'Do not call {method.__name__}() after close(): {self.name}')
        else:
            return method(self, *args, **kwargs)

    return wrapper


class QueueJobBase(JobBase):
    """
    Subclass of :class:`JobBase` with an :class:`asyncio.Queue`

    This job is used to process input asynchronously, e.g. from another
    job. For example, :meth:`enqueue` from
    :class:`~.jobs.imghost.ImageHostJob` can be connected to the ``output``
    :class:`~.utils.signal.Signal` of
    :class:`~.jobs.screenshots.ScreenshotsJob` to upload each screenshot as
    soon as it is created. :meth:`close` must be called after the last
    screenshot is fed into the queue.

    It's also possible to use this job conventionally by passing a sequence of
    values as the `enqueue` argument. This processes all values and then
    calls :meth:`close` without waiting for more.

    The :meth:`initialize` method of subclasses must accept `enqueue` as a
    keyword argument.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._queue = asyncio.Queue()
        self._read_queue_task = None
        self._enqueue_args = kwargs.get('enqueue', ())
        self._is_closed = False

    async def run(self):
        if self._enqueue_args:
            # Fill queue with predetermined items from initialization.
            for value in self._enqueue_args:
                self.enqueue(value)
            self.close()

        # Block until the closing sentinel enqueued by close() is encountered.
        await self._read_queue()

    async def _read_queue(self):
        while True:
            value = await self._queue.get()
            if value is None:
                break
            else:
                await self.handle_input(value)

    @abc.abstractmethod
    async def handle_input(self, value):
        """Handle `value` from queue"""

    @raise_if_finished
    @raise_if_closed
    def enqueue(self, value):
        """Put `value` in queue"""
        self._queue.put_nowait(value)

    def close(self):
        """Finish job after all currently queued values are handled"""
        self._queue.put_nowait(None)
        self._is_closed = True

    @property
    def is_closed(self):
        return self._is_closed

    def error(self, *args, **kwargs):
        """Call :meth:`close` before calling :meth:`.JobBase.error`"""
        self.close()
        super().error(*args, **kwargs)
