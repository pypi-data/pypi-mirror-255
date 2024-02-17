"""Utility to support common BLE operations/methods."""
from functools import partial
import logging
import queue

from mobly import asserts as mobly_asserts
from mobly.controllers import android_device
from bttc.mobly_android_device_lib.services import sl4a_service
from bttc.utils import ad_checker
from bttc.utils import typing_utils

from typing import Union


BINDING_KEYWORD = 'ble'
AndroidLike = typing_utils.AndroidLike


class BleModule:
  """BLE module to hold extended functions define in this module."""

  def __init__(self, ad: AndroidLike):
    self._ad = ad
    self.assert_scanning = partial(assert_scanning, ad)
    self.scan_and_get_device_address = (
        partial(scan_and_get_device_address, ad))


def assert_scanning(
    ad: AndroidLike,
    device_name: str) -> None:
  """Asserts that the ad's scanning can find given BT device name.

  Args:
    ad: Android like device.
    device_name: string, the name of BLE device.

  Raises:
    mobly.signals.TestFailure: Failed in scanning with given `device_name`.
  """
  try:
    bt_address = scan_and_get_device_address(ad, device_name, timeout_sec=90)
    logging.debug('BT device has BT address as %s', bt_address)
  except Exception:
    mobly_asserts.fail(
        msg=f'No BLE event with desired BE device name={device_name}',
        extras={'ad_info': str(ad)})


def bind(
    ad: Union[AndroidLike, str],
    init_mbs: bool = False, init_sl4a: bool = False) -> AndroidLike:
  """Binds the input device with functions defined in current module.

  Sample Usage:
  ```python
  >>> from bttc import ble_utils
  >>> ad = general_utils.bind('07311JECB08252', init_mbs=True, init_sl4a=True)
  >>> ad.ble.assert_scanning('Morgan')
  ```
  """
  device = None
  if isinstance(ad, str):
    device = android_device.create([{'serial': ad}])[0]
  else:
    device = ad

  device.load_config({BINDING_KEYWORD: BleModule(device)})

  if init_mbs:
    device.load_snippet(
        'mbs',
        'com.google.android.mobly.snippet.bundled')

  if init_sl4a and not device.services.has_service_by_name('sl4a'):
    device.services.register('sl4a', sl4a_service.Sl4aService)

  return device


@ad_checker.require_sl4a
def scan_and_get_device_address(
    ad: AndroidLike,
    device_name: str,
    timeout_sec: float = 30) -> str:
  """Searchs a BLE device by BLE scanner and returns it's BLE mac address.

  Args:
    ad: Android like device.
    device_name: string, the name of BLE device.
    timeout_sec: int, number of seconds to wait for finding the advertisement.

  Returns:
    String of the BLE mac address.

  Raises:
    Error: Raised if failed to get the BLE device address
  """
  filter_list = ad.sl4a.bleGenFilterList()
  scan_settings = ad.sl4a.bleBuildScanSetting()
  scan_callback = ad.sl4a.bleGenScanCallback()
  ad.sl4a.bleSetScanFilterDeviceName(device_name)
  ad.sl4a.bleBuildScanFilter(filter_list)
  ad.sl4a.bleStartBleScan(filter_list, scan_settings, scan_callback)
  try:
    event = ad.ed.pop_event(
        'BleScan%sonScanResults' % scan_callback, timeout_sec)
  except queue.Empty:
    raise android_device.DeviceError(
        ad,
        f'Timed out {timeout_sec}s after waiting for phone finding '
        f'BLE device: {device_name}.') from None
  finally:
    ad.sl4a.bleStopBleScan(scan_callback)

  return event['data']['Result']['deviceInfo']['address']
