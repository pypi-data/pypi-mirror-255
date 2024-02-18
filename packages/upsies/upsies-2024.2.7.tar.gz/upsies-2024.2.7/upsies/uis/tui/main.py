"""
Entry point
"""

import asyncio
import sys
import threading

from ... import __changelog__, __homepage__, __project_name__, application_setup, application_shutdown, errors
from ...utils import update
from . import commands, utils


def main(args=None):
    sys.exit(_main(args))


def _main(args=None):
    cmd = None
    newer_version_thread = None

    try:
        if utils.is_tty():
            from .tui import TUI
            ui = TUI()
            # Find latest version in a background thread
            newer_version_thread = _UpgradeCheck()
        else:
            from .headless import Headless
            ui = Headless()

        cmd = commands.run(args)
        application_setup(cmd.config)
        exit_code = ui.run(cmd.jobs_active)

    # UI was terminated by user prematurely
    except KeyboardInterrupt as e:
        print(e, file=sys.stderr)
        return 1

    except (errors.UiError, errors.DependencyError, errors.ContentError) as e:
        print(e, file=sys.stderr)
        return 1

    except Exception as e:
        # Unexpected exception
        import traceback
        traceback.print_exception(type(e), e, e.__traceback__)
        print()

        # Exceptions from subprocesses should save their traceback.
        # See errors.SubprocessError.
        if hasattr(e, 'original_traceback'):
            print(e.original_traceback)
            print()

        print(f'Please report the traceback above as a bug: {__homepage__}', file=sys.stderr)
        return 1

    else:
        # Print last job's output to stdout for use in output redirection.
        # Ignore disabled jobs.
        if exit_code == 0:
            for j in reversed(cmd.jobs_active):
                if j.is_enabled:
                    if j.output:
                        print('\n'.join(j.output))
                    break

        # If we found a newer version, inform the user about it.
        if newer_version_thread and newer_version_thread.result:
            msg = (
                '\n' + ('━' * 78) + '\n'
                + '\n'
                + f'  \\O/   {__project_name__} {newer_version_thread.result} has been released.\n'
                + '   |\n'
                + f'  / \\   Changes: {__changelog__}\n'
            )
            print(msg, file=sys.stderr)

        return exit_code

    finally:
        if cmd is not None:
            # Cleanup cache, close HTTP session, etc.
            application_shutdown(cmd.config)


class _UpgradeCheck(threading.Thread):
    def __init__(self):
        self.result = None
        # daemon=True allows the application to exit if this thread is still
        # running. We don't want to wait for slow/unresponsive web servers.
        super().__init__(daemon=True)
        self.start()

    def run(self):
        try:
            newer_version = asyncio.run(update.get_newer_version())
        except errors.RequestError:
            pass
        else:
            if newer_version:
                self.result = newer_version
