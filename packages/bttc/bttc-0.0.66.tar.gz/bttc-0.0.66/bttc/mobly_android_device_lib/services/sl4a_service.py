"""Mobly service replace obsoleted SL4A service."""
from typing import Any, Dict, Optional

from mobly.controllers import android_device
from mobly.controllers.android_device_lib.services import base_service

from bttc.mobly_android_device_lib.services import sl4a_client


class Sl4aService(base_service.BaseService):
  """Service for managing SL4A's client."""

  def __init__(self,
               device: android_device.AndroidDevice,
               configs: Optional[Dict[Any, Any]] = None):
    """Initializes SL4A service."""
    del configs  # Unused param.
    self._ad = device
    self._sl4a_client = None

  def __getattr__(self, name: str) -> Any:
    """Forwards the getattr calls to the client itself."""
    if self._sl4a_client:
      return getattr(self._sl4a_client, name)
    return self.__getattribute__(name)

  @property
  def is_alive(self) -> bool:
    """Returns True if SL4A's client is running."""
    return self._sl4a_client is not None

  def start(self) -> None:
    """Starts SL4A app."""
    self._sl4a_client = sl4a_client.Sl4aClient(ad=self._ad)
    self._sl4a_client.start_app_and_connect()

  def stop(self) -> None:
    """Stops SL4A app."""
    if self.is_alive:
      assert self._sl4a_client is not None
      self._sl4a_client.stop_app()
      self._sl4a_client = None

  def pause(self) -> None:
    """Pauses SL4A app."""
    assert self._sl4a_client is not None
    # Need to stop dispatcher because it continuously polls the device.
    # It's not necessary to stop the sl4a client.
    self._sl4a_client.stop_event_dispatcher()

  def resume(self) -> None:
    """Resumes SL4A app."""
    assert self._sl4a_client is not None
    self._sl4a_client.restore_app_connection()
