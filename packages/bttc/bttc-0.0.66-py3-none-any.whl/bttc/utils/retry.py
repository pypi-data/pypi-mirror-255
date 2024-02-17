"""Call a function with caller-controlled retry.

Retry on exceptions basic usage:

# Three retries with exponential backoff and fuzzing.
@retry.retry_on_exception(
    retry_intervals=retry.FuzzedExponentialIntervals(initial_delay_sec=1,
                                                     num_retries=3))
def AccessServer(...)
  # ...

@retry.logged_retry_on_exception(
    retry_intervals=retry.FuzzedExponentialIntervals(initial_delay_sec=2,
                                                     factor=5,  # 2, 10, 50, ...
                                                     num_retries=5,
                                                     max_delay_sec=300))
def MyOtherFunction():
  # Retries are logged to logging.warning.
  # ...
  pass

The wrapped function is called as normal, with the same arguments the
caller specified.  If no exception is raised, the normal result is
returned.  If an exception is raised, a number of retries will be
performed, with pauses in between.

When we run out of retries (or the caller decides not to retry a
specific exception, see below), the most recently raised exception
will be re-raised.

Only exceptions derived from the Exception class (including the
Exception class itself) will be retried.

Retry on return value basic usage:

@retry.retry_on_value(
    retry_value=False,
    retry_intervals=retry.FuzzedExponentialIntervals(
        initial_delay_sec=1, fuzz=0.1, num_retries=3))
def SomeFlakyTruthTesting():
  # May return False the first few times.
  # ...


is_even = lambda value: (value % 2) == 0
@retry.retry_on_value(retry_predicate=is_even, retry_intervals=...)
def TryForOddNumbers():
  # May return even values the first few times.
  # ...

All the same basic rules hold as the retry_on_exception decorator.  The
difference is that the decision to retry the method is based on return value
instead of an exception being raised.  One of retry_value or retry_predicate
should be specified, or retry_value will default to None.  Specifying both
options will cause retry_value to be ignored.

Default Behaviour:

The default behaviour is to retry after some fuzzed intervals.  While the
default intervals are often useful for the general case, if the precise details
matter, you should call FuzzedExponentialIntervals() to select something
suitable for your use case.  Using FuzzedExponentialIntervals is strongly
recommended.  Fuzzing prevents synchronized clients from accessing congested
resources at the same time during retry:
http://go/safe-client-behavior#exponential-back-off.  See above for examples.

As many retries will be performed as there are entries in retry_intervals.  The
logged_retry_on_exception decorator arranges for logging.warning to be called
between a failure and the sleep preceding the retry.  If there is not going to
be a retry, because we ran out of retries or the current exception is not
retryable, no message will be logged.

Do not pass a fixed list of numbers to retry_intervals.  Instead set it with a
call to FuzzedExponentialIntervals().


Args:

Optionally, you can specify parameters which control how often retries
occur, how many will be made, and in response to which exceptions.

retry_value:          The value that will cause the wrapped function to retry if
                      returned.  For retry_on_exception decorator, it expects an
                      exception type to test the raised exception with
                      isinstance to determine if the exception is retryable.

                      Example:

                      @retry.retry_on_exception(retry_value=OSError)
                      def CreateChildProcess(argv)
                        # ...

                      acceptable_errors = (OSError, ValueError)

                      @retry.retry_on_exception(retry_value=acceptable_errors)
                      def CreateChildProcess(argv)
                        # ...

retry_intervals:      Using the result of a call to FuzzedExponentialIntervals
                      is strongly recommended. See
                      http://go/safe-client-behavior#exponential-back-off for
                      more details.  This argument should be a sequence of, or a
                      callable returning a sequence of, retry intervals (usually
                      in seconds, but see the clock parameter).  When the end of
                      the retry_intervals sequence is encountered, no more
                      retries will be performed.  The sequence does not have to
                      be finite.  If this argument is not specified, an
                      unspecified default is used.

                      Examples:

                      @retry.retry_on_exception(
                          retry_intervals=retry.FuzzedExponentialIntervals(
                              initial_delay_sec=1, num_retries=3))
                      def Foo(...)
                        # ...

                      # We use a function here so that the flag value is fetched
                      # after flags have been parsed.
                      def get_intervals():
                        return FLAGS.retry_intervals

                      @retry.retry_on_exception(retry_intervals=get_intervals)
                      def Foo(...)
                        # ...

retry_predicate:      Something callable.  When the called function raises
                      an exception, the exception object is passed to this
                      callable to discover if we should retry.  If a true
                      value is returned, a retry occurs.  If this argument
                      is not specified, all exceptions are retried.

                      For retry_on_value type decorators, the return value is
                      passed to the callable instead of an exception instance.
                      Also, for retry_on_value type decorators, using
                      retry_predicate will cause retry_value to be ignored.

                      Example:

                      def IsEagainOSError(e):
                        if isinstance(e, OSError):
                          return e.errno == errno.EAGAIN
                        else:
                          return False

                      @retry.retry_on_exception(retry_predicate=IsEagainOSError)
                      def CreateChildProcess(argv)
                        # ...

info_callback:        Called after we decide to do a retry, but before
                      we sleep.  The single argument is a string
                      describing what is happening.  If you do not
                      specify a callback, no message is logged for
                      @retry.retry_on_exception, but
                      @retry.logged_retry_on_exception will log the
                      message to logging.warning, by default.  If an error
                      is not going to be retried, info_callback is not
                      called (the exception will be propagated up to the
                      caller, which has the option of logging a message itself).

                      Example:

                      def PacifyWatchdog(msg):
                        '''Let the watchdog know we are still alive.'''
                        watchdog.PatHead()
                        logging.warning(msg)

                      @retry.retry_on_exception(info_callback=PacifyWatchdog)
                      def SomeFunction()
                        # ...

error_callback:       If not None, this is called after all retry attempts
                      failed, and the operation should have retried otherwise.
                      The single argument is a string describing what is
                      happening.

                      Example:

                      @retry.retry_on_exception(error_callback=logging.error)
                      def SomeFunction()
                        # ...

clock:                The retry mechanism that sleeps between retries.
                      Rather than using the time module directly to do this, a
                      passed-in clock object is used. The default clock object
                      behaves like the time/asyncio module. This parameter can
                      be used for dependency injection in unit tests (see for
                      example retry.Clock.DoNotSleep), and a Clock class is
                      provided making it easy to skip sleeping during tests.

                      If the clock value has a sleep attribute, it's assumed
                      to be a function/method compatible with time.sleep.
                      Otherwise it's assumed to be a callable and it is used
                      directly as a function with a signature compatible
                      with time.sleep.

                      If the function being decorated is a coroutine, the
                      clock/its `sleep` method should be a coroutine that will
                      effect the sleep.

                      Example:
                      def _Intervals():
                        return retry.FuzzedExponentialIntervals(
                          initial_delay_sec=1, num_retries=3)

                      class MilliClock(object):
                        'Clock object for millisecond-granularity retries.'

                         def sleep(n):
                           time.sleep(n/1000.0)

                      @retry.retry_on_exception(
                          info_callback=lambda _: True, clock=MilliClock(),
                          retry_intervals=_Intervals())
                      def SomeFunction()
                        # ...

                      Or using a callable:

                      @retry.retry_on_exception(
                          ..., clock=lambda n: time.sleep(n/1000.0),
                          ...)
                      def SomeFunction()
                        # ...

                      If all you want to do is skip sleeping during unit tests
                      use the provided Clock class:
                      @retry.retry_on_exception(
                          clock=retry.Clock(),
                          info_callback=lambda _: True,
                          retry_intervals=itertools.repeat(100))
                      def SomeFunction()
                        # ...
                      def testSomeFunction(self):
                        with retry.Clock.DoNotSleep():
                          # ...

More examples:

def _Intervals():
  return retry.FuzzedExponentialIntervals(initial_delay_sec=1, num_retries=3)

@retry.retry_on_exception(retry_intervals=_Intervals(),
    retry_predicate=lambda e: not isinstance(e, ValueError),
    info_callback=logging.warning)
def Foo(msg):
  # ...

@retry.retry_on_exception(retry_intervals=_Intervals(),
    retry_predicate=lambda e: not isinstance(e, ValueError),
    info_callback=logging.warning)
async def Foo(msg):
  # ...

This makes Foo a retryable function/coroutine; up to three retries will be done.
ValueError exceptions will not ever be retried.  Information about retries will
be logged with logging.warning.


# Don't specify retry_intervals like this.  This is NOT RECOMMENDED.
@retry.retry_on_exception(retry_intervals=itertools.repeat(3))
def Bar(msg):
  # ...

This makes Bar a retryable function, retried forever with an interval of exactly
3 seconds.  This is far from ideal, and FuzzedExponentialIntervals() should have
been used instead.


class Baz(object):

  @retry.retry_on_exception()
  def Ugh(self, msg):
    print self._prefix, msg

Baz.Ugh() is a retryable method.


# Don't specify retry_intervals like this.
@retry.retry_on_exception(retry_intervals=itertools.repeat(3, 10))
def Qux(msg):
  # ...

This makes Qux a retryable function only up to 10 retries. After 10 retries, Qux
will start to behave like a non-retryable function, as the generator will run
out of generated values. If you want static amount of retries,
use retry.FuzzedExponentialIntervals(..., num_retries=10) or (less preferred)
[3] * 10.


Default retry properties:
        retry some default number of times after some default intervals
        retry all exceptions
        print no information
"""

import asyncio
import contextlib
import functools
import inspect
import itertools
import random
import sys
import time
import traceback
import typing
from typing import Any, Awaitable, cast, Generator, Callable, Iterator, Optional, Tuple, Union, Text, Type  # noqa

import logging
import six

if typing.TYPE_CHECKING:
  from google3.pyglib import _retry_typing

# We define a number of decorators in this module and their names
# usually produce a lint warning since they are functions which do not
# comply with google3 naming standards.  We don't silence these
# [g-bad-name] warnings since there are also other functions defined
# which do and should meet the standards.


class IncorrectRetryWrapperUsageError(ValueError):
  """Incorrect arguments were passed to a wrapper or decorator."""


class FuzzedExponentialIntervals(object):
  """Iterable for intervals that are exponentially spaced, with fuzzing.

  This class is suitable for use as the retry_intervals argument to
  retry_on_exception.

  On iteration, yields retry interval lengths, in seconds. Every iteration over
  this iterable will yield differently fuzzed interval lengths, as long as fuzz
  is nonzero.

  On retry, sleeps for an exponentially increasing amounts of time.
  Exponential backoff is required for congestion control (e.g., if a server
  is overloaded) [1]. Each sleep time is also fuzzed. Fuzzing (a.k.a. smearing)
  prevents synchronized clients from accessing congested resources at the same
  time during retry [2].

  [1] Pages 8-11: https://ee.lbl.gov/papers/congavoid.pdf

  [2] http://go/safe-client-behavior#exponential-back-off
  """

  def __init__(self,
               initial_delay_sec: float,
               num_retries: Union[int, Callable[[], int]],
               factor: float = 2,
               fuzz: float = 0.5,
               max_delay_sec: float = 60 * 60 * 4):
    """Create an instance of FuzzedExponentialIntervals.

    Args:
      initial_delay_sec: The delay before the first retry, in seconds.
      num_retries: The total number of times to retry, or a callable that
        returns such a number. The callable must always return the same
        integer value. Any exceptions from the callable are left unhandled
        by this class.
      factor: The exponential factor to use on subsequent retries.
      fuzz: A value between 0 and 1, indicating the fraction of fuzz. For a
        given delay d, the fuzzed delay is randomly chosen between
        [(1 - fuzz) * d, d].
      max_delay_sec: Maximum delay (in seconds). After this limit is reached,
        further tries use max_delay_sec instead of exponentially increasing
        the time. Defaults to 4 hours.

    Raises:
      ValueError: num_retries is not a int or a callable returning an int.
    """
    self._initial_delay_sec = initial_delay_sec
    # Note that we cannot validate num_retries by invoking the callable here,
    # since the whole point of the callable is so that people can use flags to
    # set it. Since flags are not yet parsed when decorators' __init__ method is
    # run, we must avoid calling num_retries() here.
    self._num_retries = (
        num_retries if callable(num_retries) else lambda: num_retries)
    self._factor = factor
    self._fuzz = fuzz
    self._max_delay_sec = max_delay_sec

  def __iter__(self) -> Generator[float, None, None]:
    current_delay_sec = min(self._max_delay_sec, self._initial_delay_sec)
    for _ in itertools.repeat(None, self._num_retries()):
      fuzz_multiplier = 1 - self._fuzz + random.random() * self._fuzz
      yield current_delay_sec * fuzz_multiplier
      current_delay_sec = min(self._max_delay_sec,
                              current_delay_sec * self._factor)


def SaneRetryIntervals(initial_delay_sec: float = 1.0,
                       num_retries: Union[int, Callable[[], int]] = 7,
                       factor: float = 2.0,
                       fuzz: float = 0.5,
                       max_delay_sec: float = 127.0):
  """Returns some reasonable retry intervals.

  Don't rely on these intervals being predictable and don't rely on them not
  changing over time.

  Args:
    initial_delay_sec: The delay before the first retry, in seconds.
    num_retries: The total number of times to retry, or a callable that
        returns such a number. The callable must always return the same
        integer value. Any exceptions from the callable are left unhandled
        by this class.
    factor: The exponential factor to use on subsequent retries.
    fuzz: A value between 0 and 1, indicating the fraction of fuzz. For a given
      delay d, the fuzzed delay is randomly chosen between [(1 - fuzz) * d, d].
    max_delay_sec: Maximum delay (in seconds). After this limit is reached,
      further tries use max_delay_sec instead of exponentially increasing the
      time. Defaults to 127 seconds.

  Returns:
    an iterable which produces fuzzed intervals.
  """
  return FuzzedExponentialIntervals(initial_delay_sec, num_retries, factor,
                                    fuzz, max_delay_sec)


def _IsCoroutineFunction(obj: Any) -> bool:
  """An equivalent of asyncio.iscoroutinefunction from Python 3.8+."""
  # https://bugs.python.org/issue28703
  # TODO(yileiyang): When google3 is on Python 3.8+, this can be deleted and
  # replaced with asyncio.iscoroutinefunction.
  return (hasattr(obj, "__code__") and asyncio.iscoroutinefunction(obj) and
          isinstance(obj.__code__.co_flags, int))


def _YieldFrom(iterator_or_coroutine: Union[Awaitable[Any], Iterator[Any]]):
  """Imitation of Py3's `yield from` expression with Py2-compatible syntax."""
  # TODO(yileiyang): When Python 2 is no longer supported, this can be deleted
  # and replaced with `yield from` expressions.
  if inspect.iscoroutine(iterator_or_coroutine):
    # inspect.iscoroutine explicitly checks for `async def` coroutines (which
    # have __await__).
    iterator = cast(Awaitable[Any], iterator_or_coroutine).__await__()
  else:
    iterator = iterator_or_coroutine
  try:
    while True:
      next(iterator)
  except StopIteration as end:
    if not end.args:
      return None
    else:
      return end.args[0]


class Clock(object):
  """Make it easy to skip sleeping during tests."""

  # Counter tracking the number of running DoNotSleep calls.
  # A counter is used rather than saving and restoring a bool to prevent the
  # following sequence from leaving sleep permanently disabled.
  # - DO_NOT_SLEEP = False
  # - test 1 calls DoNotSleep, DO_NOT_SLEEP is True, saved DO_NOT_SLEEP is False
  # - test 2 calls DoNotSleep, DO_NOT_SLEEP is True, saved DO_NOT_SLEEP is True
  # - test 1 finishes, DO_NOT_SLEEP is False because saved DO_NOT_SLEEP is False
  # - test 2 finishes, DO_NOT_SLEEP is True because saved DO_NOT_SLEEP is True
  # - From now on, DO_NOT_SLEEP will always be True.
  DO_NOT_SLEEP = 0

  @classmethod
  @contextlib.contextmanager
  def DoNotSleep(cls) -> Generator[None, None, None]:
    """Disable sleeping and reenable it afterwards.

    Sleeping will be disabled for *ALL* Clock objects: a test requiring sleeping
    to work normally cannot overlap with a test that requires sleeping to be
    disabled.  Nested or overlapping calls are handled correctly.

    Usage:
    def testSomeFunc(self):
      with retry.Clock.DoNotSleep():
        # SomeFunc will not sleep between retries.

    To disable sleeping for all test methods of a given TestCase, put
    `self.enter_context(retry.Clock.DoNotSleep())` in the TestCase's setUp
    method.

    Yields:
      None.
    """
    cls.DO_NOT_SLEEP += 1
    try:
      yield
    finally:
      cls.DO_NOT_SLEEP -= 1

  @classmethod
  def sleep(cls, secs: float) -> None:  # pylint: disable=g-bad-name
    if cls.DO_NOT_SLEEP:
      return
    return time.sleep(secs)


class AsyncClock(Clock):

  @classmethod
  async def sleep(cls, secs: float) -> None:  # pylint: disable=g-bad-name
    if cls.DO_NOT_SLEEP:
      return
    await asyncio.sleep(secs)


# Sentinel to use in `next(...)` instead of catching StopIteration.
_INTERVAL_SENTINEL = object()


def _CallWithExceptionRetry(
    description_str: Text,
    retry_value: Optional[Union[Type[Exception], Tuple[Type[Exception], ...]]],
    retry_intervals: Union[Iterator[float], Callable[[], Iterator[float]]],
    retry_predicate: Optional[Callable[[Exception], bool]],
    info_cb: Optional[Callable[[str], Any]],
    error_cb: Optional[Callable[[str], Any]],
    clock,
    is_async,
    func: Callable[..., Any],
    *args,
    **kwargs,
):
  """Call a function, using a generic strategy to retry on exception.

  The number of retries and the intervals between them is controlled
  by the caller.  However, in the general case the indicated function
  may be called once or several times.

  In the case where a retry occurs, this might happen after an earlier
  invocation of 'func' failed half-way through.  So, if 'func'
  modifies its arguments or changes externally-visible state, the
  behaviour may be unexpected.  You should be prepared to deal with
  the possibility that 'func' may be called several times, not fully
  completing each time.  This means that you may need to provide a
  wrapper around any function which can't directly deal with that.

  In general, you need to take special care if 'func' modifies its
  arguments in place or has side effects.

  Args:
    description_str:          Description of what we are doing
                              (on retry, this is passed to info_cb and error_cb)
    retry_value:              An exception type or tuple of multiple types that
                              are tested with isinstance() and retried if true.
    retry_intervals:          Desired retry intervals [1, 2, 4, 53, ...], or a
                              callable returning such intervals.
                              Usually in sec.
                              If the optional argument 'clock' is set, these
                              values are passed to clock.sleep().  Otherwise,
                              they are passed to time.sleep().
    retry_predicate:          Any exception object is passed to this function.
                              If True is returned, a retry is attempted.
    info_cb:                  Called with an informational message when we are
                              preparing to retry (i.e. never if everything
                              worked or if we never want a retry).
    error_cb:                 Called with an error message when we finished
                              retrying and the operation still fails.
    clock:                    A callable or coroutine compatible with
                              time.sleep/asyncio.sleep, or an object offering a
                              sleep() method.
    is_async:                 Whether to await the result of clock.sleep.
    func:                     The function we want to call.  It may be
                              called several times.
    *args:                    The list of arguments to be passed to func.
    **kwargs:                 Any keyword arguments to be passed.

  Returns:
    whatever func returns
  Raises:
    whatever exception func raises (if we run out of retries)
  """
  sleeper = getattr(clock, "sleep", clock)
  if not sleeper:
    sleeper = asyncio.sleep if is_async else time.sleep

  interval_iterator = _GetRetryIterator(retry_intervals)
  while True:
    try:
      return func(*args, **kwargs)
    except Exception as e:  # pylint: disable=broad-except
      e_traceback = sys.exc_info()[2]
      try:
        if retry_predicate and not retry_predicate(e) or (
            retry_value and not isinstance(e, retry_value)):
          # not retryable, re-raise the exception
          raise
        if info_cb or error_cb:
          # get the stack trace below the retry layer.
          e_traceback_str = "".join(traceback.format_tb(e_traceback))
          e_desc_str = "".join(traceback.format_exception_only(e.__class__, e))
          # get the stack trace above the retry layer,
          # remove record of this function and the above "retry_on_exception".
          stack_traceback_str = "".join(traceback.format_stack()[:-2])
        interval = next(interval_iterator, _INTERVAL_SENTINEL)
        if interval is _INTERVAL_SENTINEL:
          # Ran out of retries, re-raise the original exception.
          # Use the traceback we got when we caught the original exception.
          if error_cb:
            error_cb(f"CallWithExceptionRetry: ran out of retries for "
                     f"{description_str}. Caught exception: {e_desc_str}"
                     f"Call failed at (most recent call last):\n"
                     f"{stack_traceback_str}"
                     f"Traceback for above exception (most recent call last):\n"
                     f"{e_traceback_str}")
          six.reraise(type(e), e, e_traceback)
        if info_cb:
          info_cb(f"CallWithExceptionRetry: waiting for {interval} seconds "
                  f"before retrying {description_str} because we caught "
                  f"exception: {e_desc_str}"
                  f"Call failed at (most recent call last):\n"
                  f"{stack_traceback_str}"
                  f"Traceback for above exception (most recent call last):\n"
                  f"{e_traceback_str}")
        if is_async:
          _YieldFrom(sleeper(interval))
        else:
          sleeper(interval)
      finally:
        # traceback objects in locals can cause lots of reference cycles, drop
        # ours now that we don't need it any more:
        e_traceback = None


def _CallWithValueRetry(
    description_str: Text,
    retry_value: Any,
    retry_intervals: Union[Iterator[float], Callable[[], Iterator[float]]],
    retry_predicate: Callable[[Any], bool],
    info_cb: Optional[Callable[[str], Any]],
    error_cb: Optional[Callable[[str], Any]],
    clock,
    is_async,
    func: Callable[..., Any],
    *args,
    **kwargs,
):
  """Call a function, using a generic strategy to retry on certain value.

  The number of retries and the intervals between them is controlled
  by the caller.  However, in the general case the indicated function
  may be called once or several times.

  In the case where a retry occurs, this might happen after an earlier
  invocation of 'func' failed half-way through.  So, if 'func'
  modifies its arguments or changes externally-visible state, the
  behaviour may be unexpected.  You should be prepared to deal with
  the possibility that 'func' may be called several times, not fully
  completing each time.  This means that you may need to provide a
  wrapper around any function which can't directly deal with that.

  In general, you need to take special care if 'func' modifies its
  arguments in place or has side effects.

  Args:
    description_str:          Description of what we are doing
                              (on retry, this is passed to info_cb and error_cb)
    retry_value:              The value to retry on if returned by func.
    retry_intervals:          Desired retry intervals [1, 2, 4, 53, ...], or a
                              callable returning such intervals.
                              Usually in sec.
                              If the optional argument 'clock' is set, these
                              values are passed to clock.sleep().  Otherwise,
                              they are passed to time.sleep().
    retry_predicate:          Any return value is passed to this function.
                              If True is returned, a retry is attempted.
                              Setting retry_predicate will retry_value to be
                              ignored.
    info_cb:                  Called with an informational message when we are
                              preparing to retry (i.e. never if everything
                              worked or if we never want a retry).
    error_cb:                 Called with an error message when we finished
                              retrying and the operation still fails.
    clock:                    A callable compatible with time.sleep or
                              asyncio.sleep, or an object offering a sleep()
                              method; usually the time module.
    is_async:                 Whether to await the result of clock.sleep.
    func:                     The function we want to call.  It may be
                              called several times.
    *args:                    The list of arguments to be passed to func.
    **kwargs:                 Any keyword arguments to be passed.

  Returns:
    whatever func returns
  Raises:
    whatever exception func raises (if we run out of retries)
  """
  sleeper = getattr(clock, "sleep", clock)
  if not sleeper:
    sleeper = asyncio.sleep if is_async else time.sleep

  interval_iterator = _GetRetryIterator(retry_intervals)
  while True:
    retval = func(*args, **kwargs)
    if retry_predicate:
      if not retry_predicate(retval):
        # not retryable, return the current value
        return retval
    elif retval != retry_value:
      # not retryable, return the current value
      return retval

    if info_cb or error_cb:
      info = str(retval) or retval.__class__
    try:
      interval = next(interval_iterator)
      if info_cb:
        info_cb(f"CallWithValueRetry: waiting for {interval} seconds before "
                f"retrying {description_str} because return was: {info}")
      if is_async:
        _YieldFrom(sleeper(interval))
      else:
        sleeper(interval)
    except StopIteration:
      # ran out of retries, return the current value
      if error_cb:
        error_cb(f"CallWithValueRetry: ran out of retries for "
                 f"{description_str}, returning: {info}")
      return retval


def _GetRetryIterator(
    retry_intervals: Union[Iterator[float], Callable[[], Iterator[float]]]):
  """Get an iterator over the retry_intervals.

  Args:
    retry_intervals: A callable returning retry intervals. Use
      FuzzedExponentialIntervals(). For backward compatibility, an iterable of
      such intervals is also accepted, but this is suboptimal as the intervals
      are not fuzzed.

  Returns:
    iterator over intervals.
  """
  try:
    interval_iterator = iter(retry_intervals)
  except TypeError:  # retry_intervals is callable
    interval_iterator = iter(retry_intervals())
  return interval_iterator


def _GetRetryProperties(orig_retry_func_name: Text, kwargs):
  """Extract the various keyword parameters we need.

  Args:
    orig_retry_func_name: the first retry.py function called for
      this request (that is, the least deeply-nested retry function).
    kwargs: the keyword args passed to the retry function.
  Returns:
    (retry_value, retry_intervals, retry_predicate, info_callback,
    error_callback, clock)
    The meaning of these values is extensively documented in the doc
    comment for this module.
  Raises:
    IncorrectRetryWrapperUsageError: an unexpected keyword argument was passed.
  """
  default_values = (("retry_value", None),
                    ("retry_intervals", SaneRetryIntervals()),
                    ("retry_predicate", None),
                    ("info_callback", None),
                    ("error_callback", None),
                    ("clock", time))
  result = [kwargs.get(param_name, default_value)
            for param_name, default_value in default_values]

  expected_kwargs = frozenset([name for name, unused_value in default_values])
  for param_name, param_value in kwargs.items():
    if param_name not in expected_kwargs:
      msg = ("Unexpected keyword argument passed to %s: %s=%s"
             % (orig_retry_func_name, param_name, param_value))
      logging.error(msg)
      raise IncorrectRetryWrapperUsageError(msg)
  return result


def _RejectUnexpectedPositionalArgs(function_name: Text,
                                    actual_args: Tuple[Any]) -> None:
  """Issue an exception or a warning if the wrong number of args was passed.

  We only verify the number of positional arguments here.  Keyword
  arguments are verified in _GetRetryProperties.

  Args:
    function_name: name of the function on whose behalf we are checking args.
    actual_args: the actual positional arguments.
  Raises:
    IncorrectRetryWrapperUsageError: if more than one positional argument
      was specified.
  """
  extra = actual_args[1:]
  if extra:
    msg = ("Unexpected positional arguments passed to %s: %r"
           % (function_name, extra))
    logging.error(msg)
    raise IncorrectRetryWrapperUsageError(msg)


def _QualifiedFunctionName(func_name):
  """Qualify a function name with the name of this module."""
  return "%s.%s" % (__name__, func_name)


def retry_on_exception(*args, **kwargs):  # pylint: disable=invalid-name
  """Function decorator taking keyword args to control retrying on exception.

  Args:
    *args: if passed, a sequence whose only item is the function to be wrapped.
    **kwargs: keyword config parameters (see module doc comment)
  Returns:
    As per Python decorators.  If the function to be wrapped was passed in,
    the wrapped function is returned. Otherwise, the decorator function
    is returned.
  Raises:
    IncorrectRetryWrapperUsageError if unknown keyword arguments are supplied
    or if the wrong number of positional keyword arguments are supplied.
  """
  me = _QualifiedFunctionName(retry_on_exception.__name__)
  _RejectUnexpectedPositionalArgs(me, args)
  return _RetryDecorator(me, _CallWithExceptionRetry, *args, **kwargs)


def retry_on_value(*args, **kwargs):  # pylint: disable=invalid-name
  """Function decorator taking keyword args to control retrying on return value.

  Args:
    *args: if passed, a sequence whose only item is the function to be wrapped.
    **kwargs: keyword config parameters (see module doc comment)
  Returns:
    As per Python decorators.  If the function to be wrapped was passed in,
    the wrapped function is returned. Otherwise, the decorator function
    is returned.
  Raises:
    IncorrectRetryWrapperUsageError if unknown keyword arguments are supplied
    or if the wrong number of positional keyword arguments are supplied.
  """
  me = _QualifiedFunctionName(retry_on_value.__name__)
  _RejectUnexpectedPositionalArgs(me, args)
  return _RetryDecorator(me, _CallWithValueRetry, *args, **kwargs)


def _FilterFunctionAttributesForPython3(function: Callable[..., Any],
                                        attributes: Tuple[Text]) -> Tuple[Text]:
  """Filters out function attributes which don't match Py3 requirements.

  We do this to work around an incompatibility between Python 3 and
  the current version of Mox.  "z = mox.Mox().CreateMockAnything()"
  sets z.__qualname__ to a mox.mox.MockMethod object, while Python 3
  requires that attribute to be set to a string.

  If you are reading this comment because the use of Mox in your test
  is somehow once more incompatible, please consider switching from
  Mox to Mock instead of updating this code.

  Args:
    function: a function
    attributes: a tuple containing a list of attribute names.
  Returns:
    a tuple containing the list of attribute names we can safely copy.
  """
  result = []
  checks = {"__qualname__": str, "__annotations__": dict, "__name__": str}
  for attrib_name in attributes:
    if not hasattr(function, attrib_name):
      continue
    if attrib_name not in checks:
      continue
    val = getattr(function, attrib_name)
    if not isinstance(val, checks[attrib_name]):
      continue
    result.append(attrib_name)
  return tuple(result)


def _RetryDecorator(orig_retry_func_name, retry_function, *args, **kwargs):
  """Function decorator taking keyword arguments to control retrying.

  Args:
    orig_retry_func_name: name of the retry.py entry point originally called.
    retry_function: method containing the retry logic
    *args: if passed, a sequence whose only item is the function to be wrapped.
    **kwargs: keyword config parameters (see module doc comment)
  Returns:
    As per Python decorators.  If the function to be wrapped was passed in,
    the wrapped function is returned. Otherwise, the decorator function
    is returned.
  """
  _RejectUnexpectedPositionalArgs(orig_retry_func_name, args)
  retry_v, intervals, retry_p, info_cb, error_cb, clock = _GetRetryProperties(
      orig_retry_func_name, kwargs)

  def Decorator(function):
    """The decorator; its only job is to return the wrapper function."""

    # Only copy attributes that the original function (or other callable)
    # actually has; callables may not have a __name__, for example.
    # In that particular case, stringifying the callable itself is the most
    # likely thing to provide useful information.
    try:
      function_name = getattr(function, "__name__")
    except AttributeError:
      function_name = str(function)
    wrapper_assignments = _FilterFunctionAttributesForPython3(
        function,
        tuple((
            attr for attr in functools.WRAPPER_ASSIGNMENTS
            if getattr(function, attr, None) is not None
        )))

    # We resolve sleeper here so that we can check if it meets our requirements
    # and fail at decoration time. However this sleeper is not passed to the
    # retry functions. They will resolve sleeper again at runtime so that users
    # can mock clock methods and they will resolve correctly at execution time.
    sleeper = getattr(clock, "sleep", clock)

    if _IsCoroutineFunction(function):
      if not sleeper:
        sleeper = asyncio.sleep
      if not callable(sleeper):
        raise IncorrectRetryWrapperUsageError(
            "The given clock/its `sleep` method is not callable."
        )
      if not _IsCoroutineFunction(sleeper):
        raise IncorrectRetryWrapperUsageError(
            "The wrapped function is a coroutine, "
            "but the given clock is not a coroutine, nor is its `sleep` method."
        )

      # The function we are wrapping is a coroutine. Define a coroutine version
      # of the wrapper function and return that. Additionally, wrap `function`
      # (the client function to be retried) with a lambda that will _YieldFrom
      # it (because it's a coroutine). This lets us use the same `_CallWith*`
      # functions as retry_functions without modifying them: they see a normal
      # function that returns or raises and they can determine whether to retry
      # the function call. The _YieldFrom around the client function and the
      # `@asyncio.coroutine` decorator on AsyncWrapper combine to allow
      # asynchronous execution while the retry logic remains unaware of it.
      new_func = lambda *args, **kwargs: _YieldFrom(function(*args, **kwargs))  # noqa

      @asyncio.coroutine
      @functools.wraps(function, assigned=wrapper_assignments)
      def AsyncWrapper(*wrapper_args, **wrapper_kwargs):
        """This is the wrapper function itself; coroutine version."""
        # logging.vlog(2, "In async wrapper: calling %s to invoke %s",
        #             retry_function.__name__, function_name)
        return retry_function(function_name, retry_v, intervals, retry_p,
                              info_cb, error_cb, clock, True, new_func,
                              *wrapper_args, **wrapper_kwargs)

      return AsyncWrapper

    if not sleeper:
      sleeper = time.sleep
    if not callable(sleeper):
      raise IncorrectRetryWrapperUsageError(
          "The given clock/its `sleep` method is not callable."
      )
    if _IsCoroutineFunction(sleeper):
      raise IncorrectRetryWrapperUsageError(
          "The wrapped function is synchronous, "
          "but the given clock/its `sleep` method is a coroutine."
      )

    # logging.vlog(
    #    2, "Decorator: wrapping %s (for %s) around %s: assignments are %r",
    #    retry_function.__name__, orig_retry_func_name, function_name,
    #    dict([(a, getattr(function, a)) for a in wrapper_assignments]))

    @functools.wraps(function, assigned=wrapper_assignments)
    def Wrapper(*wrapper_args, **wrapper_kwargs):
      """This is the wrapper function itself."""
      # logging.vlog(2, "In wrapper: calling %s to invoke %s",
      #             retry_function.__name__, function_name)
      return retry_function(function_name, retry_v, intervals, retry_p, info_cb,
                            error_cb, clock, False, function, *wrapper_args,
                            **wrapper_kwargs)

    return Wrapper

  if args:
    # The sole argument is the function to be wrapped.
    return Decorator(args[0])
  else:
    return Decorator


def logged_retry_on_exception(*args, **kwargs):  # pylint: disable=invalid-name
  """Function decorator taking keyword arguments to control retrying.

  This is just like @retry.retry_on_exception, except that a message
  is logged by default with logging.warning.

  Args:
    *args:   if passed, a sequence whose first item is the function to
            be wrapped.
    **kwargs: keyword config parameters (see module doc comment)
  Returns:
    As per Python decorators.  If the function to be wrapped was passed in,
    the wrapped function is returned. Otherwise, the decorator function
    is returned.
  """
  _RejectUnexpectedPositionalArgs(
      _QualifiedFunctionName(logged_retry_on_exception.__name__), args)
  modified_kwargs = kwargs.copy()
  modified_kwargs.setdefault("info_callback", logging.warning)
  return retry_on_exception(*args, **modified_kwargs)


def logged_retry_on_value(*args, **kwargs):  # pylint: disable=invalid-name
  """Function decorator taking keyword arguments to control retrying.

  This is just like @retry.retry_on_value, except that a message is logged
  by default with logging.warning.

  Args:
    *args:   if passed, a sequence whose first item is the function to be
      wrapped.
    **kwargs: keyword config parameters (see module doc comment)

  Returns:
    As per Python decorators.  If the function to be wrapped was passed in,
    the wrapped function is returned. Otherwise, the decorator function
    is returned.
  """
  _RejectUnexpectedPositionalArgs(
      _QualifiedFunctionName(logged_retry_on_value.__name__), args)
  modified_kwargs = kwargs.copy()
  modified_kwargs.setdefault("info_callback", logging.warning)
  return retry_on_value(*args, **modified_kwargs)


if typing.TYPE_CHECKING:
  # For type checking purposes only. This allows Pytype to correctly preserve
  # method signatures and detect errors in decorated methods.
  # pylint: disable=used-before-assignment
  retry_on_exception = _retry_typing.RetryDecorator  # noqa
  retry_on_value = _retry_typing.RetryDecorator  # noqa
  logged_retry_on_exception = _retry_typing.RetryDecorator  # noqa
  logged_retry_on_value = _retry_typing.RetryDecorator  # noqa
