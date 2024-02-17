"""Errors specific to AVRCP profile."""


class Error(Exception):
  """A base class for errors related to AVRCP."""


class UnknownPlaybackStateError(Error):
  """Fails in getting the playback state."""


class PlaybackError(Error):
  """Fails in playback operation."""


class AvrcpOperationError(Error):
  """Fails in AVRCP operation."""
