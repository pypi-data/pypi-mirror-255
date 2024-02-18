"""
Share generated metadata
"""

import asyncio

from .. import errors, trackers
from . import JobBase

import logging  # isort:skip
_log = logging.getLogger(__name__)


class SubmitJob(JobBase):
    """
    Submit torrent file and other metadata to tracker

    This job adds the following signals to the :attr:`~.JobBase.signal`
    attribute:

        ``logging_in``
            Emitted when attempting to start a user session. Registered
            callbacks get no arguments.

        ``logged_in``
            Emitted when login attempt ended. Registered callbacks get no
            arguments.

        ``uploading``
            Emitted when attempting to upload metadata. Registered callbacks get
            no arguments.

        ``uploaded``
            Emitted when upload attempt ended. Registered callbacks get no
            arguments.

        ``logging_out``
            Emitted when attempting to end a user session. Registered callbacks
            get no arguments.

        ``logged_out``
            Emitted when logout attempt ended. Registered callbacks get no
            arguments.
    """

    name = 'submit'
    label = 'Submit'

    # Don't cache output.
    cache_id = None

    def initialize(self, *, tracker, tracker_jobs):
        """
        Set internal state

        :param TrackerBase tracker: Return value of :func:`~.trackers.tracker`
        :param TrackerJobsBase tracker_jobs: Instance of
            :attr:`~.base.TrackerBase.TrackerJobs`
        """
        assert isinstance(tracker, trackers.TrackerBase), f'Not a TrackerBase: {tracker!r}'
        assert isinstance(tracker_jobs, trackers.TrackerJobsBase), f'Not a TrackerJobsBase: {tracker_jobs!r}'

        # Pass through signals from Tracker and TrackerJobs
        for t in (tracker, tracker_jobs):
            t.signal.register('warning', self.warn)
            t.signal.register('error', self.error)
            t.signal.register('exception', self.exception)

        self._tracker = tracker
        self._tracker_jobs = tracker_jobs

        for signal, message in (('logging_in', 'Logging in'),
                                ('logged_in', 'Logged in'),
                                ('uploading', 'Uploading'),
                                ('uploaded', 'Uploaded'),
                                ('logging_out', 'Logging out'),
                                ('logged_out', '')):
            self.signal.add(signal)
            self.signal.register(signal, lambda msg=message: setattr(self, 'info', msg))

        self.signal.register('finished', lambda _: setattr(self, 'info', ''))
        self.signal.register('error', lambda _: setattr(self, 'info', ''))

        # Create jobs_after_upload now so they can connect to other jobs,
        # e.g. add_torrent_job needs to register for create_torrent_job's output
        # before create_torrent_job finishes.
        self.enabled_jobs_after_upload

        # Start jobs_after_upload only if the upload succeeds. This also works
        # nicely when this job is getting it's output from cache.
        self.signal.register('output', self._start_jobs_after_upload)

    def _start_jobs_after_upload(self, _):
        for job in self.enabled_jobs_after_upload:
            job.start()

    async def run(self):
        # While there is any unfinished job, keep collecting all enabled+started
        # jobs and wait for them. We do it like this because any job can enable
        # and/or disable other jobs, and then we have to re-collect all enabled
        # jobs.
        def get_unfinished_jobs():
            return tuple(
                job
                for job in self.enabled_jobs_before_upload
                if job.was_started and not job.is_finished
            )

        while jobs := get_unfinished_jobs():
            _log.debug('Waiting for jobs before upload: %r', [j.name for j in jobs])
            await asyncio.gather(*(job.wait() for job in jobs))
            jobs = get_unfinished_jobs()
        _log.debug('Done waiting for jobs before upload: %r', [j.name for j in self.enabled_jobs_before_upload])

        # Wait for any dangling background tasks attached to Tracker
        await self._tracker.await_tasks()

        # Don't submit if self._tracker_jobs thinks that's a bad idea.
        if self._tracker_jobs.submission_ok:
            await self._submit()

    async def _submit(self):
        _log.debug('%s: Submitting', self._tracker.name)
        try:
            self.signal.emit('logging_in')
            await self._tracker.login()
            self.signal.emit('logged_in')

            try:
                self.signal.emit('uploading')
                torrent_page_url = await self._tracker.upload(self._tracker_jobs)
                if torrent_page_url:
                    self.send(torrent_page_url)
                    self.signal.emit('uploaded')

            finally:
                self.signal.emit('logging_out')
                await self._tracker.logout()
                self.signal.emit('logged_out')

        except errors.RequestError as e:
            self.error(e)

    @property
    def enabled_jobs_before_upload(self):
        """
        Sequence of jobs to do before submission

        This is the same as :attr:`.TrackerJobsBase.jobs_before_upload` but
        with all `None` values and disabled jobs filtered out.
        """
        return tuple(
            job
            for job in self._tracker_jobs.jobs_before_upload
            if job and job.is_enabled
        )

    @property
    def enabled_jobs_after_upload(self):
        """
        Sequence of jobs to do after successful submission

        This is the same as :attr:`.TrackerJobsBase.jobs_after_upload` but with
        all `None` values and disabled jobs filtered out.
        """
        return tuple(
            job
            for job in self._tracker_jobs.jobs_after_upload
            if job and job.is_enabled
        )

    @property
    def hidden(self):
        """
        Hide this job if :attr:`~.base.TrackerJobsBase.submission_ok` is falsy

        This allows jobs to prevent submission.

        It also should mean this job is hidden until the submission happens
        because :attr:`~.base.TrackerJobsBase.submission_ok` should be falsy
        until all :attr:`~.base.TrackerJobsBase.jobs_before_upload` finished
        successfully.
        """
        return not self._tracker_jobs.submission_ok

    @property
    def final_job_before_upload(self):
        """
        If submission is prevented by :attr:`~.base.TrackerJobsBase.submission_ok`
        return the last item of
        :attr:`~.base.TrackerJobsBase.jobs_before_upload` if all jobs are
        finished

        Return `None` if :attr:`~.base.TrackerJobsBase.submission_ok` is truthy
        or the final job cannot be determined at the moment.
        """
        if not self._tracker_jobs.submission_ok:
            jobs = self.enabled_jobs_before_upload
            # Because jobs can enable/disable each other, we can't know the
            # final job until all jobs are finished.
            if jobs and all(job.is_finished for job in jobs):
                return jobs[-1]

    @property
    def output(self):
        """Output of this job or :attr:`final_job_before_upload` if it is not `None`"""
        final_job_before_upload = self.final_job_before_upload
        if final_job_before_upload:
            return final_job_before_upload.output
        else:
            return super().output

    @property
    def exit_code(self):
        """Exit code of this job or :attr:`final_job_before_upload` if it is not `None`"""
        final_job_before_upload = self.final_job_before_upload
        if final_job_before_upload:
            return final_job_before_upload.exit_code
        else:
            return super().exit_code
