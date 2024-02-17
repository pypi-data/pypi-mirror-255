"""Utility to hold decorators to examine the conditions of device."""
import functools
import logging

from bttc.mobly_android_device_lib.services import sl4a_service
from typing import Any, Callable, Optional


def require_sl4a(
    func: Optional[Callable[..., Any]] = None,
    *,
    auto_init: bool = True) -> Callable[..., Any]:
  """Decorator to examine if the android device is ready for SL4A.

  Args:
    func: The decorated function.
    auto_init: True to initialize SL4A service automatically if necessary.

  Returns:
    The wrapper of decorated function.

  Raises:
    Exception: SL4A is not ready in target device `ad`.
  """
  def decorate_func(func: Optional[Callable[..., Any]]) -> Callable[..., Any]:
    @functools.wraps(func)
    def func_wrapper(*args, **kwargs):
      ad = args[0]
      if ad.sl4a is None:
        logging.warning('SL4A is not initialized yet from %s!', ad)

        if auto_init:
          ad.services.register('sl4a', sl4a_service.Sl4aService)
        else:
          raise Exception(f'SL4A is not ready in {ad}')

      return func(*args, **kwargs)

    return func_wrapper

  if func is None:
    # decorator was called with argument(s)
    return decorate_func
  else:
    # decorator was called without argument
    return decorate_func(func)
