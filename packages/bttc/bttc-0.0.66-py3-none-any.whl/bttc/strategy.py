"""BT working strategy module."""

import abc

from bttc import constants


class UnsupportedProfileConnectionError(Exception):
  """Error casued by unsupported connection of profile."""

  def __init__(self, profile: constants.BluetoothProfile):
    super().__init__()
    self._profile = profile

  def __str__(self):
    return f'Connection with profile={self._profile.name} is not supported yet!'


class ConnectionStrategy(abc.ABC):
  """Bluetooth profile connection strategy."""

  @abc.abstractmethod
  def is_connected(self) -> bool:
    """Checks the connection of target profile.

    Returns:
      True iff and target profile is connected.
    """
    raise NotImplementedError

  @abc.abstractmethod
  def connect(self, timeout_sec: int = 30) -> bool:
    """Builds connection of target profile.

    Args:
      timeout_sec: Number of seconds to wait for connection.

    Returns:
      True iff the connection is carried out successfully.
    """
    raise NotImplementedError
