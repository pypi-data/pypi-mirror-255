"""BCST AVRCP Facade module."""
from __future__ import annotations

import abc
import enum

from bttc.profiles.avrcp import errors
from bttc.utils import typing_utils


# The audio source path of BluetoothMediaPlayback in the SL4A app.
ANDROID_TEST_MEDIA_PATH = '/sdcard/Music/test'


@enum.unique
class PlaybackStateEnum(enum.IntEnum):
  """Enum of playback state."""
  PLAY = 3
  PAUSE = 2
  STOP = 1


class AvrcpTargetDevice(abc.ABC):
  """Abstract AVRCP target device for AVRCP testing.

  Attributes:
    log: Logger object, literal meaning
  """

  def __init__(self, log: typing_utils.LogProtocol):
    self.log = log

  @abc.abstractmethod
  def get_playback_state(self) -> PlaybackStateEnum:
    """Gets the playback state of device.

    Returns:
      The playback state.
    """
    raise NotImplementedError

  @abc.abstractmethod
  def wait_for_playback_state(self, state: PlaybackStateEnum,
                              timeout_sec: int) -> bool:
    """Waits for the playback to be the expected state.

    Args:
      state: Playback state to wait for.
      timeout_sec: Timeout in second to wait for the expected playback state.

    Returns:
      True iff the playback is changed to the expected state before timeout.
    """
    raise NotImplementedError

  @abc.abstractmethod
  def play(self) -> bool:
    """Plays the music."""
    raise NotImplementedError

  @abc.abstractmethod
  def stop(self) -> bool:
    """Stops the music."""
    raise NotImplementedError

  @abc.abstractmethod
  def pause(self) -> bool:
    """Pauses the music."""
    raise NotImplementedError

  @abc.abstractmethod
  def track_next(self):
    """Skips to the next track."""
    raise NotImplementedError

  @abc.abstractmethod
  def track_previous(self):
    """Skips to the previous track."""
    raise NotImplementedError


class AvrcpFacade:
  """AVRCP Facade class."""

  def __init__(self, device: AvrcpTargetDevice):
    self._device = device

  @property
  def state(self) -> PlaybackStateEnum:
    """Gets playback state."""
    return self._device.get_playback_state()

  def play(self):
    """Plays the music."""
    if not self._device.play_music():
      raise errors.AvrcpOperationError('Failed to play music!')

  def stop(self):
    self._device.stop()

  def pause(self):
    """Pauses the music."""
    if not self._device.pause():
      raise errors.AvrcpOperationError('Failed to pause music!')

  def track_next(self):
    """Skips to the next track."""
    self._device.track_next()

  def track_previous(self):
    """Skips to the previous track."""
    self._device.track_previous()
