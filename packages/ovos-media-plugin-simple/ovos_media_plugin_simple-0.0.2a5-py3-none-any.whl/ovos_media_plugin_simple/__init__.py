import mimetypes
import re
import signal
import subprocess
import time
from distutils.spawn import find_executable
from time import sleep

from ovos_plugin_manager.templates.media import AudioPlayerBackend
from ovos_utils.log import LOG
from requests import Session


def find_mime(path):
    mime = None
    if path.startswith('http'):
        response = Session().head(path, allow_redirects=True)
        if 200 <= response.status_code < 300:
            mime = response.headers['content-type']
    if not mime:
        mime = mimetypes.guess_type(path)[0]
    # Remove any http address arguments
    if not mime:
        mime = mimetypes.guess_type(re.sub(r'\?.*$', '', path))[0]

    if mime:
        return mime.split('/')
    else:
        return (None, None)


def play_audio(uri, play_cmd):
    """ Play a audio file.

        Returns: subprocess.Popen object
    """
    play_wav_cmd = play_cmd.split() + [uri]

    try:
        return subprocess.Popen(play_wav_cmd)
    except Exception as e:
        LOG.error(f"Failed to play: {play_wav_cmd}")
        LOG.debug(f"Error: {e}")
        return None


class SimpleAudioService(AudioPlayerBackend):
    sox_play = find_executable("play")
    pulse_play = find_executable("paplay")
    alsa_play = find_executable("aplay")
    mpg123_play = find_executable("mpg123")

    def __init__(self, config, bus=None):
        super().__init__(config, bus)
        self.process = None
        self._stop_signal = False
        self._is_playing = False
        self._paused = False
        self.ts = 0

        self.supports_mime_hints = True
        mimetypes.init()

    def on_track_start(self):
        self.ts = time.time()
        # Indicate to audio service which track is being played
        if self._track_start_callback:
            self._track_start_callback(self._now_playing)

    def on_track_end(self):
        self._is_playing = False
        self._paused = False
        self.process = None
        self.ts = 0
        if self._track_start_callback:
            self._track_start_callback(None)

    def on_track_error(self):
        self._is_playing = False
        self._paused = False
        self.process = None
        self.ts = 0
        self.ocp_error()

    # simple player internals
    def _get_track(self, track_data):
        if isinstance(track_data, list):
            track = track_data[0]
            mime = track_data[1]
            mime = mime.split('/')
        else:  # Assume string
            track = track_data
            mime = find_mime(track)
        return track, mime

    def _is_process_running(self):
        return self.process and self.process.poll() is None

    def _stop_running_process(self):
        if self._is_process_running():
            if self._paused:
                # The child process must be "unpaused" in order to be stopped
                self.process.send_signal(signal.SIGCONT)
            self.process.terminate()
            countdown = 10
            while self._is_process_running() and countdown > 0:
                sleep(0.1)
                countdown -= 1

            if self._is_process_running():
                # Failed to shutdown when asked nicely.  Force the issue.
                LOG.debug("Killing currently playing audio...")
                self.process.kill()
        self.process = None

    @property
    def player_cmd(self):
        """determine the best command to play a stream"""
        # sox should handle almost every format, but fails in some urls
        if self.sox_play:
            track = self._now_playing
            # NOTE: some urls like youtube streams will cause extension detection to fail
            # let's handle it explicitly
            ext = track.split("?")[0].split(".")[-1]
            player = self.sox_play + f" --type {ext}"

        # determine best available player
        else:
            track, mime = self._get_track(self._now_playing)
            LOG.debug(f'Mime info: {mime}')

            # wav file
            player = None
            if 'wav' in mime[1]:
                player = self.pulse_play
            # guess mp3
            elif self.mpg123_play:
                player = self.mpg123_play

            # fallback to alsa, only wav files will play correctly
            player = player or self.alsa_play
        return player

    # audio service
    def supported_uris(self):
        uris = ['file', 'http']
        if self.sox_play:
            uris.append("https")
        return uris

    def play(self, repeat=False):
        """ Play playlist using simple. """
        # Stop any existing audio playback
        self._stop_running_process()

        self._is_playing = True
        self._paused = False

        # Replace file:// uri's with normal paths
        uri = self._now_playing.replace('file://', '')

        self.on_track_start()
        try:
            self.process = play_audio(uri, self.player_cmd)
        except FileNotFoundError as e:
            LOG.error(f'Couldn\'t play audio, {e}')
            self.process = None
            self.on_track_error()
        except Exception as e:
            LOG.exception(repr(e))
            self.process = None
            self.on_track_error()

        # Wait for completion or stop request
        while (self._is_process_running() and not self._stop_signal):
            sleep(0.25)

        if self._stop_signal:
            self._stop_running_process()

        self.on_track_end()

    def stop(self):
        """ Stop simple playback. """
        LOG.info('SimpleService Stop')
        if self._is_playing:
            self._stop_signal = True
            while self._is_playing:
                sleep(0.1)
            self._stop_signal = False
            return True
        return False

    def pause(self):
        """ Pause simple playback. """
        if self.process and not self._paused:
            # Suspend the playback process
            self.process.send_signal(signal.SIGSTOP)
            self._paused = True

    def resume(self):
        """ Resume paused playback. """
        if self.process and self._paused:
            # Resume the playback process
            self.process.send_signal(signal.SIGCONT)
            self._paused = False

    def lower_volume(self):
        """Lower volume.

        This method is used to implement audio ducking. It will be called when
        OpenVoiceOS is listening or speaking to make sure the media playing isn't
        interfering.
        """
        # Not available in this plugin

    def restore_volume(self):
        """Restore normal volume.

        Called when to restore the playback volume to previous level after
        OpenVoiceOS has lowered it using lower_volume().
        """
        # Not available in this plugin

    def get_track_length(self) -> int:
        """
        getting the duration of the audio in milliseconds
        """
        # we only can estimate how much we already played as a minimum value
        return self.get_track_position()

    def get_track_position(self) -> int:
        """
        get current position in milliseconds
        """
        # approximate given timestamp of playback start
        if self.ts:
            return int((time.time() - self.ts) * 1000)
        return 0

    def set_track_position(self, milliseconds):
        """
        go to position in milliseconds
          Args:
                milliseconds (int): number of milliseconds of final position
        """
        # Not available in this plugin
