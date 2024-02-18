"""
Subtitles information
"""

import re

from .. import utils
from . import LazyModule

import logging  # isort:skip
_log = logging.getLogger(__name__)

langcodes = LazyModule(module='langcodes', namespace=globals())


# Map various strings to canonical sutitle format names
_subtitle_formats = {
    # Matroska Codec ID
    # Reference: https://www.matroska.org/technical/codec_specs.html
    'S_HDMV/PGS': 'PGS',     # Blu-ray
    'S_VOBSUB': 'VobSub',    # DVD
    'S_TEXT/UTF8': 'SRT',    # SubRip
    'S_TEXT/SSA': 'SSA',     # SubStation Alpha
    'S_TEXT/ASS': 'ASS',     # Advanced SubStation Alpha
    'S_TEXT/WEBVTT': 'VTT',  # Web Video Text Tracks

    # File extension
    'srt': 'SRT',     # SubRip
    'ssa': 'SSA',     # SubStation Alpha
    'ass': 'ASS',     # Advanced SubStation Alpha
    'vtt': 'VTT',     # Web Video Text Tracks
    'idx': 'VobSub',  # DVD
    'sub': 'VobSub',  # DVD
}


class Subtitle:
    """
    Dataclass that stores information about a subtitle track

    :param language: BCP47 language code with optional country code (e.g. "en",
        "en-UK", "es-419", "zh-HANS")

        References:
            https://www.matroska.org/technical/notes.html [Language Codes]
            https://en.wikipedia.org/wiki/IETF_language_tag

        If `language` is not a valid language code, the `language` and
        `region` attributes are empty strings.

    :param bool forced: Whether the subtitle track should always be played
    :param bool format: Subtitle format (e.g. "SRT", "VobSub", "PGS")

    :raise ValueError: if `language` is invalid
    """

    def __init__(self, *, language, forced, format):
        # Parse and normalize `language`
        try:
            lc = langcodes.Language.get(language)
        except ValueError:
            self._language = ''
            self._region = ''
        else:
            self._language = lc.language
            self._region = lc.territory or ''

        self._forced = bool(forced)
        self._format = str(format or '')

    @property
    def language(self):
        """
        Language part of the `language` initialization argument, e.g. "en",
        "es", "zh", etc.
        """
        return self._language

    @property
    def region(self):
        """
        Region part of the `language` initialization argument, e.g. "UK",
        "419", "HANS", etc.
        """
        return self._region

    @property
    def forced(self):
        """Whether the subtitle track should always be played"""
        return self._forced

    @property
    def format(self):
        """Subtitle format (e.g. "SRT", "VobSub", "PGS")"""
        return self._format

    def __repr__(self):
        if self.region:
            language = f'{self.language}-{self.region}'
        else:
            language = self.language
        return f'{type(self).__name__}(language={language!r}, forced={self.forced!r}, format={self.format!r})'

    def __hash__(self):
        return hash((self.language, self.region, self.forced, self.format))

    def __eq__(self, other):
        return hash(self) == hash(other)


def get_subtitles(content_path):
    """
    Return sequence of :class:`Subtitle` objects from all subtitle sources

    This function combines all ``get_subtitles_*`` functions.

    :param content_path: Path to release file or directory
    """
    subtitles = set()
    subtitles.update(get_subtitles_from_mediainfo(content_path))
    subtitles.update(get_subtitles_from_text_files(content_path))
    subtitles.update(get_subtitles_from_idx_files(content_path))
    subtitles.update(get_subtitles_from_dvd_tree(content_path))
    return subtitles


def get_subtitles_from_mediainfo(content_path):
    """
    Return sequence of :class:`Subtitle` objects from ``mediainfo`` output

    Only the first video is used to find subtitles (see :func:`find_videos`).

    :param content_path: Path to release file or directory
    """
    subtitles = set()
    all_tracks = utils.video.tracks(content_path)
    try:
        subtitle_tracks = all_tracks['Text']
    except KeyError:
        pass
    else:
        for track in subtitle_tracks:
            subtitle = Subtitle(
                language=track.get('Language', ''),
                forced=(track.get('Forced') == 'Yes'),
                format=_subtitle_formats.get(track.get('CodecID')),
            )
            _log.debug('Found subtitle language in mediainfo: %r', subtitle)
            subtitles.add(subtitle)
    _log.debug('Subtitles from mediainfo: %r', subtitles)
    return subtitles


_srt_filename_regex = re.compile(r'(?:\.([a-z]{2,3})|)\.(\w+)$')

def get_subtitles_from_text_files(content_path):
    """
    Return sequence of :class:`Subtitle` objects from subtitle file names

    For a video file named "foo.mkv", the subtitle language can be in the file
    name, e.g. "foo.en.srt" or "foo.eng.ass".

    If `content_path` is a directory, it is searched recursively for subtitle
    files.

    If `content_path` is not a directory, the returned sequence is empty.

    :param content_path: Path to release file or directory
    """
    subtitles = set()
    for filepath in utils.fs.file_list(content_path, extensions=('srt', 'ssa', 'ass', 'vtt')):
        filename = utils.fs.basename(filepath)
        match = _srt_filename_regex.search(filename)

        if match:
            language = match.group(1) or ''
            extension = match.group(2).lower()
            format = _subtitle_formats.get(extension, '')
        else:
            language = ''
            format = ''

        subtitle = Subtitle(
            language=language,
            forced=False,
            format=format,
        )
        _log.debug('Found text subtitle: %s: %r', filepath, subtitle)
        subtitles.add(subtitle)

    _log.debug('Subtitles from text files: %r', subtitles)
    return subtitles


def get_subtitles_from_idx_files(content_path):
    """
    Return sequence of :class:`Subtitle` objects from ``*.idx`` files

    For .idx/.sub pairs, the .idx file can contain the language.

    If `content_path` is a directory, it is searched recursively for ``*.idx``
    files.

    If `content_path` is not a directory, the returned sequence is empty.

    :param content_path: Path to release file or directory
    """
    subtitles = set()
    for idx_filepath in utils.fs.file_list(content_path, extensions=('idx',)):
        try:
            language = _get_language_code_from_idx_file(idx_filepath)
        except OSError as e:
            _log.debug('Ignoring exception from reading %r: %r', idx_filepath, e)
        else:
            subtitle = Subtitle(
                language=language,
                forced=False,
                format=_subtitle_formats['idx'],
            )
            _log.debug('Found IDX subtitle: %s: %r', idx_filepath, subtitle)
            subtitles.add(subtitle)
    _log.debug('Subtitles from idx files: %r', subtitles)
    return subtitles


_idx_language_regex = re.compile(r'^id:\s*([a-z]{2,3})\b')

def _get_language_code_from_idx_file(idx_filepath):
    # Example: "id: de, index: 0"
    # Expect 2-letter and 3-letter codes.
    with open(idx_filepath, 'r') as f:
        for line in f.readlines():
            match = _idx_language_regex.search(line)
            if match:
                language = match.group(1)
                _log.debug('Found subtitle language in %s: %r', idx_filepath, language)
                return language
    return ''


def get_subtitles_from_dvd_tree(content_path):
    """
    Return sequence of :class:`Subtitle` objects from ``VIDEO_TS``
    subdirectory

    If `content_path` is not a directory or does not contain a ``VIDEO_TS``
    subdirectory, the returned sequence is empty.

    :param content_path: Path directory that contains ``VIDEO_TS`` subdirectory
    """
    subtitles = set()
    main_videos = utils.video.find_videos(content_path)
    for main_video in main_videos:
        if utils.fs.file_extension(main_video) == 'vob':
            ifo_filepath = utils.video.vob2ifo(main_video)
            for sub in get_subtitles_from_mediainfo(ifo_filepath):
                sub._format = _subtitle_formats['S_VOBSUB']
                subtitles.add(sub)
    _log.debug('Subtitles from DVD tree(s): %r', subtitles)
    return subtitles
