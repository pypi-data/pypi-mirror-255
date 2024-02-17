
from dataclasses import dataclass
from typing import Sequence, List
from bttc import errors
import re


@dataclass
class BondedDevice:
  """Dataclass for bonded devices"""
  mac_address: str
  device_name: str
  device_type: str


def parse_bluetooth_crash_info(log_content: str) -> Sequence[str]:
  """Parses the BT manager log to collect crash information.

  For this function to work, we expect below log snippet from given log content:

  ===
  Bluetooth crashed 2 times
  12-17 10:23:00
  12-17 11:29:13
  ===

  If there is no crash, log will look like:
  ===
  Bluetooth crashed 0 times
  ===

  Args:
    log_content: The dumped BT manager log.

  Returns:
    Sequence of crash time string in format '%m-%d %H:%M:%S'.

  Raises:
    errors.LogParseError:
      Fail to parse the log. It doesn't contain the key words.
  """
  lines = log_content.split('\n')
  for line_num, line in enumerate(lines):
    match_object = re.search(
      r'Bluetooth crashed (?P<crash_time>\d+) time', line)
    if match_object is None:
      continue

    crash_time = int(match_object.group('crash_time'))
    if crash_time > 0:
      begin_crash_time_num = line_num + 1
      return [
          line.strip()
          for line in lines[begin_crash_time_num:begin_crash_time_num +
                            crash_time]
      ]
    return []

  raise errors.LogParseError(log_content)


def parse_bonded_device_info(log_content: str) -> List[BondedDevice]:
  """Parses the BT manager log to collect bonded device information.

  For this function to work, we expect below log snippet from given log content:

  ===
  Bonded devices:
    28:6F:40:57:AC:44 [ DUAL ] JBL TOUR ONE M2
    CC:98:8B:C0:F2:B8 [ DUAL ] WH-1000XM3
  ===

  If there is no bonded device, log will look like:
  ===
  Bonded devices:

  ===

  Args:
    log_content: The dumped BT manager log.

  Returns:
    List[BondedDevice] : Dataclass of BondedDevice.
      Ex:
        [BondedDevice(mac_address='74:45:CE:F2:0F:EA',
                      device_name='WI-XB400',
                      device_type='DUAL')]
  Raises:
    errors.LogParseError:
      Fail to parse the log. It doesn't contain the key words.
  """
  if re.search(r'Bonded devices:\n', log_content) is not None:
    output = re.finditer(
      r'(?P<mac_address>\w{2}:\w{2}:\w{2}:\w{2}:\w{2}:\w{2})'
      r'\s\[\s+(?P<device_type>.*?)\s+\]\s(?P<device_name>.*?)\n',
      log_content,
    )
    bonded_devices = []
    for device in output:
      mac_address = device.group('mac_address')
      device_type = device.group('device_type')
      device_name = device.group('device_name')
      bonded_devices.append(
        BondedDevice(mac_address=mac_address,
                     device_name=device_name,
                     device_type=device_type))
    return bonded_devices

  raise errors.LogParseError(log_content)
