"""Module to hold common dataclass and enum."""
import enum


class StrEnum(str, enum.Enum):
  """Accepts only string values."""


class BTLogLevel(StrEnum):
  """BT log level."""
  DEBUG = 'LOG_DEBUG'
  VERBOSE = 'LOG_VERBOSE'
