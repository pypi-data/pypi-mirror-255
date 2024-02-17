"""Errors specific to HFP profile."""


class Error(Exception):
  """A base class for errors related to HFP."""


class CallStateTimeoutError(Error):
  """Fails to wait for specific call state."""


class CallError(Error):
  """Fails in call operation."""


class AnswerCallError(Error):
  """Fails in answering call."""


class UnknownCallStateError(Error):
  """Unknown call state name."""
