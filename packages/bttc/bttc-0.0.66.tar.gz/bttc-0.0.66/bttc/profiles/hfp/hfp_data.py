"""Dataclass and enum used in HFP testing."""

from __future__ import annotations

import enum

from bttc.profiles.hfp import errors


@enum.unique
class CallStateEnum(str, enum.Enum):
  """Enum of phone call state."""
  RINGING = "RINGING"
  IDLE = "IDLE"
  DIALING = "DIALING"
  ACTIVE = "ACTIVE"
  ON_HOLD = "ON_HOLD"
  CONNECTING = "CONNECTING"
  CONNECTED = "CONNECTED"
  DISCONNECTING = "DISCONNECTING"
  DISCONNECTED = "DISCONNECTED"
  ANSWERING = "ANSWERING"
  ANSWERED = "ANSWERED"

  @classmethod
  def from_str(cls, name: str) -> CallStateEnum:
    """Turns string into call state enum.

    Args:
      name: Name of call state enum in string.

    Returns:
      Corresponding call state enum.

    Raises:
      UnknownCallStateError: Given call state name is unknown.
    """
    for call_state_enum in cls:  # pytype: disable=missing-parameter
      if name == call_state_enum.value:
        return call_state_enum

    raise errors.UnknownCallStateError(f"Unknown call state name={name}")
