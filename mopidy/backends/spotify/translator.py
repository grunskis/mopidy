import datetime as dt
import logging

from spotify import Link, SpotifyError

from mopidy import settings
from mopidy.backends.spotify import ENCODING
from mopidy.models import Artist, Album, Track, Playlist

logger = logging.getLogger('mopidy.backends.spotify.translator')

class SpotifyTranslator(object):
    @classmethod
    def to_mopidy_artist(cls, spotify_artist):
        if not spotify_artist.is_loaded():
            return Artist(name=u'[loading...]')
        return Artist(
            uri=str(Link.from_artist(spotify_artist)),
            name=spotify_artist.name().decode(ENCODING),
        )

    @classmethod
    def to_mopidy_album(cls, spotify_album):
        if not spotify_album.is_loaded():
            return Album(name=u'[loading...]')
        # TODO pyspotify got much more data on albums than this
        return Album(name=spotify_album.name().decode(ENCODING))

    @classmethod
    def to_mopidy_track(cls, spotify_track):
        if not spotify_track.is_loaded():
            return Track(name=u'[loading...]')
        uri = str(Link.from_track(spotify_track, 0))
        if dt.MINYEAR <= int(spotify_track.album().year()) <= dt.MAXYEAR:
            date = dt.date(spotify_track.album().year(), 1, 1)
        else:
            date = None
        return Track(
            uri=uri,
            name=spotify_track.name().decode(ENCODING),
            artists=[cls.to_mopidy_artist(a) for a in spotify_track.artists()],
            album=cls.to_mopidy_album(spotify_track.album()),
            track_no=spotify_track.index(),
            date=date,
            length=spotify_track.duration(),
            bitrate=(settings.SPOTIFY_HIGH_BITRATE and 320 or 160),
        )

    @classmethod
    def to_mopidy_playlist(cls, spotify_playlist):
        if not spotify_playlist.is_loaded():
            return Playlist(name=u'[loading...]')
        # FIXME Replace this try-except with a check on the playlist type,
        # which is currently not supported by pyspotify, to avoid handling
        # playlist folder boundaries like normal playlists.
        try:
            return Playlist(
                uri=str(Link.from_playlist(spotify_playlist)),
                name=spotify_playlist.name().decode(ENCODING),
                tracks=[cls.to_mopidy_track(t) for t in spotify_playlist],
            )
        except SpotifyError, e:
            logger.warning(u'Failed translating Spotify playlist '
                '(probably a playlist folder boundary): %s', e)
