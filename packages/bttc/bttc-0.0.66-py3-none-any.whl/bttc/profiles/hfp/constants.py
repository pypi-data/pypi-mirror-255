"""Constants used in HFP profile."""
import enum


@enum.unique
class AudioRoute(enum.Enum):
  """Enumeration of Audio source.

  The settings here have to sync up with "Constant for Audio Route" defined in
  go/audio_route_constant
  """
  EARPIECE = 'EARPIECE'
  BLUETOOTH = 'BLUETOOTH'
  SPEAKER = 'SPEAKER'
  WIRED_HEADSET = 'WIRED_HEADSET'
  WIRED_OR_EARPIECE = 'WIRED_OR_EARPIECE'
