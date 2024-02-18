import functools

from . import JobWidgetBase


class MediainfoJobWidget(JobWidgetBase):

    is_interactive = False

    def setup(self):
        pass

    @functools.cached_property
    def runtime_widget(self):
        return None
