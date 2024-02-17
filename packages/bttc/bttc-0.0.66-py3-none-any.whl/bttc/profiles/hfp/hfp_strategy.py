"""Profile HFP Strategy module."""
import time

from typing import Optional
from mobly.controllers import android_device
from bttc import constants
from bttc import strategy


class HFPConnectionStrategy(strategy.ConnectionStrategy):
  """HFP connection strategy."""

  def __init__(self,
               hfp_client_ad: android_device.AndroidDevice,
               hfp_ag_ad: android_device.AndroidDevice,
               hfp_client_ad_mac_address: Optional[str] = None,
               hfp_ag_ad_mac_address: Optional[str] = None):
    self._hfp_client_ad = hfp_client_ad
    self._hfp_ag_ad = hfp_ag_ad
    self._hfp_client_ad_mac_address = (
        hfp_client_ad_mac_address if hfp_client_ad_mac_address is not None
        else self._hfp_client_ad.sl4a.bluetoothGetLocalAddress())
    self._hfp_ag_ad_mac_address = (
        hfp_ag_ad_mac_address if hfp_ag_ad_mac_address is not None
        else self._hfp_ag_ad.sl4a.bluetoothGetLocalAddress())

  def is_connected(self) -> bool:
    """Checks the connection of HFP.

    Returns:
      True iff HFP is connected.
    """
    return self._hfp_client_ad.sl4a.bluetoothHfpClientGetConnectionStatus(
        self._hfp_ag_ad_mac_address)

  def connect(self, timeout_sec: int = 30) -> bool:
    """Builds connection of HFP profile.

    Args:
      timeout_sec: Number of seconds to wait for connection.

    Returns:
      True iff the connection is carried out successfully.
    """
    if self.is_connected():
      self._hfp_client_ad.log.info(
          'The HFP connection between %s and %s is already connected.',
          self._hfp_client_ad.serial, self._hfp_ag_ad.serial)
      return True

    pri_ad_local_name = self._hfp_client_ad.sl4a.bluetoothGetLocalName()
    for policy in [
        constants.BluetoothConnectionPolicy.CONNECTION_POLICY_FORBIDDEN,
        constants.BluetoothConnectionPolicy.CONNECTION_POLICY_ALLOWED]:
      self._hfp_client_ad.log.info(
          'Sets profile HFP on %s for %s to policy %s',
          pri_ad_local_name, self._hfp_ag_ad_mac_address, policy)
      self._hfp_client_ad.sl4a.bluetoothHfpClientSetPriority(
          self._hfp_ag_ad_mac_address, policy.value)

    self._hfp_client_ad.sl4a.bluetoothConnectBonded(self._hfp_ag_ad_mac_address)

    end_time = time.monotonic() + timeout_sec
    while time.monotonic() < end_time:
      if self.is_connected():
        self._hfp_client_ad.log.info(
            'The HFP connection between %s and %s is established.',
            self._hfp_client_ad.serial, self._hfp_ag_ad.serial)
        return True
      time.sleep(1)

    self._hfp_client_ad.log.warning(
        'Failed to connect between %s and %s for profile HFP!',
        self._hfp_client_ad.serial, self._hfp_ag_ad.serial)
    return False
