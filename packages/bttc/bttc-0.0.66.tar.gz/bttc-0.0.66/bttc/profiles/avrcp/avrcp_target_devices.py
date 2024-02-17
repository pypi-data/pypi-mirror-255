"""AVRCP target device implementation from AVRCP interface AvrcpTargetDevice."""

import time

from mobly import signals
from mobly.controllers.android_device_lib.services import sl4a_service
from mobly.snippet import errors as mobly_snippet_errors

from bttc import constants
from bttc.profiles.avrcp import avrcp_facade
from bttc.profiles.avrcp import errors
from bttc.utils import retry
from bttc.utils import typing_utils


class AndroidAvrcpTargetDevice(avrcp_facade.AvrcpTargetDevice):
  """Android AVRCP target device."""

  def __init__(self, device: typing_utils.AndroidLike):
    super().__init__(device.log)
    self._device = device

  @property
  def _sl4a(self) -> sl4a_service.Sl4aService:
    if self._device.sl4a is None:
      raise ValueError('No SL4A service is registered for a device.')
    return self._device.sl4a

  def _start_avrcp_media_browser_service(self, timeout_sec: int = 10):
    """Starts AVRCP media browser service.

    Args:
      timeout_sec: number of seconds to wait for the AVRCP media browser service
          be active.

    Raises:
      signals.ControllerError: raise if AVRCP media browser service on the
          device fails to be started.
    """
    self._sl4a.bluetoothMediaPhoneSL4AMBSStart()
    end_time = time.monotonic() + timeout_sec
    while time.monotonic() < end_time:
      # Checks if media session "BluetoothSL4AAudioSrcMBS" is active.
      # e.g.: active_sessions = ['BluetoothSL4AAudioSrcMBS']
      active_sessions = self._sl4a.bluetoothMediaGetActiveMediaSessions()
      if 'BluetoothSL4AAudioSrcMBS' in active_sessions:
        return

      time.sleep(1)

    raise signals.ControllerError('Failed to start AvrcpMediaBrowserService.')

  @retry.retry_on_exception(
      retry_value=(signals.ControllerError, errors.UnknownPlaybackStateError),
      retry_intervals=retry.FuzzedExponentialIntervals(
          initial_delay_sec=1, num_retries=5, factor=1.1))
  def get_playback_state(self) -> avrcp_facade.PlaybackStateEnum:
    """Gets the playback state of device.

    Returns:
      The playback state.

    Raises:
      errors.UnknownPlaybackStateError: Raised if failed to catch the playback
        state information from Bluetooth manager log.
    """
    self._start_avrcp_media_browser_service()
    try:
      state = self._sl4a.bluetoothMediaGetCurrentPlaybackState()['state']
      return avrcp_facade.PlaybackStateEnum(state)
    except (mobly_snippet_errors.Error, ValueError) as err:
      raise errors.UnknownPlaybackStateError(
          f'Failed to catch information of playback state with error {err}.')

  def wait_for_playback_state(self, state: avrcp_facade.PlaybackStateEnum,
                              timeout_sec: int = 20) -> bool:
    """Waits for the playback to be the expected state.

    Args:
      state: Playback state to wait for.
      timeout_sec: Timeout in second to wait for the expected playback state.

    Returns:
      True iff the playback is changed to the expected state before timeout.
    """
    end_time = time.monotonic() + timeout_sec
    while time.monotonic() < end_time:
      if self.get_playback_state() == state:
        return True

      time.sleep(1)

    return False

  def is_music_playing(self) -> bool:
    """Checks if the music is playing.

    Returns:
      True iff the music is playing.
    """
    return self.get_playback_state() == avrcp_facade.PlaybackStateEnum.PLAY

  def play_music(self) -> bool:
    """Plays the music if it is not playing.

    Returns:
      True iff the music playback can reach the state as PLAY.
    """
    if not self.is_music_playing():
      return self.play()

    self.log.info('The music is already playing.')
    return True

  def play(self) -> bool:
    """Plays the music.

    Returns:
      True iff the music playback can reach the state as PLAY.
    """
    # Starts BluetoothSL4AAudioSrcMBS on the phone.
    self._sl4a.bluetoothMediaPhoneSL4AMBSStart()
    time.sleep(1)  # Waits for BluetoothSL4AAudioSrcMBS to be active.

    # Changes the playback state to playing.
    self._sl4a.bluetoothMediaHandleMediaCommandOnPhone(
        constants.MediaCommandEnum.PLAY.command)

    return self.wait_for_playback_state(avrcp_facade.PlaybackStateEnum.PLAY)

  def stop(self) -> bool:
    """Stops the music."""
    self._sl4a.bluetoothMediaPhoneSL4AMBSStop()
    time.sleep(1)
    return self.wait_for_playback_state(avrcp_facade.PlaybackStateEnum.STOP)

  def pause(self) -> bool:
    """Pauses the music.

    Returns:
      True iff the music playback can reach the state as PAUSE.
    """
    self._sl4a.bluetoothMediaHandleMediaCommandOnPhone(
        constants.MediaCommandEnum.PAUSE.command)

    return self.wait_for_playback_state(avrcp_facade.PlaybackStateEnum.PAUSE)

  def track_next(self):
    """Skips to the next track."""
    self._sl4a.bluetoothMediaHandleMediaCommandOnPhone(
        constants.MediaCommandEnum.NEXT.command)

  def track_previous(self):
    """Skips to the previous track."""
    self._sl4a.bluetoothMediaHandleMediaCommandOnPhone(
        constants.MediaCommandEnum.PREVIOUS.command)
