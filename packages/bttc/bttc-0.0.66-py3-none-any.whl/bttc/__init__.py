"""BTTC

BT testing common utilities.
"""
from bttc import utils_loader
from bttc.utils import device_factory
from ppadb import client


__version__ = "0.0.66"
__author__ = 'John Lee/Yuan Long Luo/Denny Chai'
__credits__ = 'Google Pixel PQM'


def get(
    serial_number: str,
    required_func_module_names: set | None = None,
    init_mbs: bool = False, init_sl4a: bool = False):
  """Gets device by its serial number."""
  required_func_module_names = required_func_module_names or {}
  func_module_info = utils_loader.get_func_modules()
  device = device_factory.get(
      serial_number, init_mbs=init_mbs, init_sl4a=init_sl4a)
  for module_name, module_info in func_module_info.items():
    if module_name in required_func_module_names or module_info.auto_load:
      module_info.module.bind(device)

  return device


def get_all(
    required_func_module_names: set | None = None,
    init_mbs: bool = False, init_sl4a: bool = False):
  """Gets all connected device(s) from local."""
  device_info = {}
  adb_client = client.Client(host='localhost', port=5037)
  for device in adb_client.devices():
    device_info[device.serial] = get(
        device.serial,
        required_func_module_names=required_func_module_names,
        init_mbs=init_mbs,
        init_sl4a=init_sl4a)

  return device_info
