"""Errors specific to iPerf testing."""


class Error(Exception):
  """A base class for errors related to iPerf testing."""


class UnknownStateError(Error):
  """Under unexpected state."""


class IPerfClientWifiError(Error):
  """Failed to retrieve Wifi IP from iPerf client."""
