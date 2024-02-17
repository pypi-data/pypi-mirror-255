"""Utility to support common WiFi operations/methods."""
from __future__ import annotations

from bttc import bt_utils
from bttc import common_data
from bttc import errors
from bttc.utils import device_factory
from functools import partial

from mobly.controllers import android_device

import re
from typing import TypeAlias, Union


BINDING_KEYWORD = 'wifi'
ANDROID_DEVICE: TypeAlias = android_device.AndroidDevice


class WiFiModule:
  """WiFi module to hold WiFi related functions define in this module."""

  def __init__(self, ad: ANDROID_DEVICE):
    self._ad = ad
    self.status = partial(get_status, ad=ad)
    self.scan = partial(start_scan, ad=ad)

  @property
  def ssid_name(self) -> str:
    return get_ssid_name(self._ad)


def bind(
    ad: Union[ANDROID_DEVICE, str],
    init_mbs: bool = False, init_sl4a: bool = False) -> ANDROID_DEVICE:
  """Binds the input device with functions defined in current module.

  Sample Usage:
  ```python
  >>> from bttc import wifi_utils
  >>> dut = wifi_utils.bind('35121FDJG0005P')
  >>> dut.wifi.status()
  <WifiStatus.ENABLED: 'enabled'>
  >>> dut.wifi.ssid_name
  'Pixel_5413'
  >>> dut.wifi.scan()  # Start WiFi scan
  ```

  Args:
    ad: If string is given, it stands for serial of device. Otherwise, it should
        be the Android device object.

  Returns:
    The device with binded functions defined in current module.
  """
  device = device_factory.get(ad, init_mbs=init_mbs, init_sl4a=init_sl4a)
  device.load_config({BINDING_KEYWORD: WiFiModule(device)})
  return device


class WifiStatus(common_data.StrEnum):
  ENABLED = 'enabled'
  DISABLED = 'disabled'

  @classmethod
  def from_str(cls, input_str: str) -> WifiStatus:
    """Gets Wifi status enum from string."""
    for wifi_status_enum in cls:
      if wifi_status_enum == input_str.strip():
        return wifi_status_enum

    raise errors.UnknownWiFiStatusError(input_str)


def get_status(ad: android_device.AndroidDevice) -> WifiStatus:
  """Gets WiFi status."""
  std, _, return_code = bt_utils.safe_adb_shell(ad)('dumpsys wifi')

  if return_code != 0:
    raise errors.AdbExecutionError(return_code, std)

  # e.g.: Wi-Fi is disabled
  matcher = re.search('Wi-Fi is (.*)', std)
  if matcher:
    return WifiStatus.from_str(matcher.group(1).strip())
  else:
    raise errors.UnknownWiFiStatusError(std)


def get_ssid_name(ad: android_device.AndroidDevice) -> str | None:
  """Gets WiFi SSID name."""
  std, _, return_code = bt_utils.safe_adb_shell(ad)(
      'wpa_cli -iwlan0 -g@android:wpa_wlan0 IFNAME=wlan0 status ')

  if return_code != 0:
    raise errors.AdbExecutionError(
        return_code, std, guiding_msg='Check if Wifi is enabled!')

  # e.g.: ssid=Pixel_5413
  matcher = re.search(r'^ssid\s*=\s*(.*)', std, re.M)
  if matcher:
    return matcher.group(1).strip()
  else:
    raise errors.AdbUnknownOutputError(std)


def start_scan(ad: android_device.AndroidDevice):
  """Starts WiFi scan."""
  std, _, return_code = bt_utils.safe_adb_shell(ad)(
      'cmd wifi start-scan')

  if return_code != 0:
    raise errors.AdbExecutionError(return_code, std)
