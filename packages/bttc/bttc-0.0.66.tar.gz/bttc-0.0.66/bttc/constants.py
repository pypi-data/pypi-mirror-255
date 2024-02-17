"""Module to hold constants used in BT operations."""
import enum


ADB_SHELL_CMD_OUTPUT_ENCODING = 'utf-8'


class BluetoothProfile(enum.IntEnum):
  """Enum class for bluetooth profile types.

  The enumeration here should sync up with go/public_api_of_bt_profiles
  """
  HEADSET = 1
  A2DP = 2
  HEALTH = 3
  HID_HOST = 4
  PAN = 5
  PBAP = 6
  GATT = 7
  GATT_SERVER = 8
  MAP = 9
  SAP = 10
  A2DP_SINK = 11
  AVRCP_CONTROLLER = 12
  AVRCP = 13
  HEADSET_CLIENT = 16
  PBAP_CLIENT = 17
  MAP_MCE = 18
  HID_DEVICE = 19
  OPP = 20
  HEARING_AID = 21
  UNKNOWN = 99


class BluetoothConnectionPolicy(enum.IntEnum):
  """Enum class for bluetooth connection policy.

  Bluetooth connection policy is defined in go/public_api_of_bt_profiles
  """
  CONNECTION_POLICY_UNKNOWN = -1
  CONNECTION_POLICY_FORBIDDEN = 0
  CONNECTION_POLICY_ALLOWED = 100


class MediaCommandEnum(enum.Enum):
  """Enum class for media passthrough commands."""

  def __new__(cls, *args, **kwds):
    value = len(cls.__members__) + 1
    obj = object.__new__(cls)
    obj._value_ = value
    return obj

  def __init__(self, command, event_name):
    self.command = command
    self.event_name = event_name

  PLAY = 'play', 'playReceived'
  PAUSE = 'pause', 'pauseReceived'
  NEXT = 'skipNext', 'skipNextReceived'
  PREVIOUS = 'skipPrev', 'skipPrevReceived'
