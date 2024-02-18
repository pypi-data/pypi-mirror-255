"""
Standardized configuration and setup howto
"""

from ... import __project_name__, utils


class Howto:
    def __init__(self, tracker_cls):
        self._tracker_cls = tracker_cls
        self._section = -1

    def join(self, *sections):
        return '\n'.join(sections).strip()

    @property
    def current_section(self):
        return self._section

    @property
    def next_section(self):
        self._section += 1
        return self._section

    @property
    def introduction(self):
        return utils.string.evaluate_fstring(
            self.join(
                (
                    '{howto.next_section}. How To Read This Howto\n'
                    '\n'
                    '   {howto.current_section}.1 Words in ALL_CAPS_AND_WITH_UNDERSCORES are placeholders.\n'
                    '   {howto.current_section}.2 Everything after "$" is a terminal command.\n'
                ),
            ),
            howto=self,
        )

    @property
    def screenshots(self):
        def imghost_names(tracker):
            return ', '.join(
                tracker.TrackerConfig.defaults["image_host"].item_type.options
            )

        return utils.string.evaluate_fstring(
            self.join(
                (
                    '{howto.next_section}. Screenshots (Optional)\n'
                    '\n'
                    '   {howto.current_section}.1 Specify how many screenshots to make.\n'
                    '       $ {executable} set trackers.{tracker.name}.screenshots NUMBER_OF_SCREENSHOTS\n'
                ),
                (
                    '   {howto.current_section}.2 Specify where to host images.\n'
                    '       $ {executable} set trackers.{tracker.name}.image_host IMAGE_HOST,IMAGE_HOST,...\n'
                    '       If IMAGE_HOST is down, try the next one.\n'
                    '       Supported services: {imghost_names(tracker)}\n'
                    '\n'
                    '   {howto.current_section}.3 Configure image hosting service.\n'
                    '       $ {executable} upload-images IMAGE_HOST --help\n'
                ),
            ),
            howto=self,
            tracker=self._tracker_cls,
            executable=__project_name__,
            imghost_names=imghost_names,
        )

    @property
    def autoseed(self):
        return utils.string.evaluate_fstring(
            self.join(
                (
                    '{howto.next_section}. Add Uploaded Torrents To Client (Optional)\n'
                    '\n'
                    '   {howto.current_section}.1 Specify which client to add uploaded torrents to.\n'
                    '       $ {executable} set trackers.{tracker.name}.add_to CLIENT_NAME\n'
                    '       Supported clients: {client_names}\n'
                ),
                (
                    '   {howto.current_section}.2 Specify your client connection.\n'
                    '       $ {executable} set clients.CLIENT_NAME.url URL\n'
                    '       $ {executable} set clients.CLIENT_NAME.username USERNAME\n'
                    '       $ {executable} set clients.CLIENT_NAME.password PASSWORD\n'
                    '\n'
                    '{howto.next_section}. Copy Uploaded Torrents To Directory (Optional)\n'
                    '\n'
                    '   $ {executable} set trackers.{tracker.name}.copy_to /path/to/directory\n'
                ),
            ),
            howto=self,
            tracker=self._tracker_cls,
            executable=__project_name__,
            client_names=', '.join(utils.btclient.client_names()),
        )

    @property
    def reuse_torrents(self):
        return utils.string.evaluate_fstring(
            self.join(
                (
                    '{howto.next_section}. Reuse Existing Torrents (Optional)\n'
                    '\n'
                    '    You can skip the hashing when creating a torrent by specifying\n'
                    '    a directory path that contains the torrents you are seeding.\n'
                    '    A matching torrent is found by searching the directory recursively\n'
                    '    for a torrent with the same size and file names. If such a torrent is\n'
                    '    found, a few pieces of each file are hashed to verify the match.\n'
                    '\n'
                    '    $ {executable} set config.torrent-create.reuse_torrent_paths TORRENT_DIRECTORY\n'
                ),
            ),
            howto=self,
            executable=__project_name__,
        )

    @property
    def upload(self):
        return utils.string.evaluate_fstring(
            self.join(
                (
                    '{howto.next_section}. Upload\n'
                    '\n'
                    '   $ {executable} submit {tracker.name} --help\n'
                    '   $ {executable} submit {tracker.name} /path/to/content\n'
                ),
            ),
            howto=self,
            tracker=self._tracker_cls,
            executable=__project_name__,
        )
