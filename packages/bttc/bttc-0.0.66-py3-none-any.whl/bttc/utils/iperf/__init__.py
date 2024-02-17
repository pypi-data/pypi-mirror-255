"""Entry pacakge of iPerf facade interface."""

from __future__ import annotations
import atexit
from bttc import general_utils
from bttc.utils.iperf import errors
import dataclasses
import enum
import subprocess
from mobly import utils as mobly_utils
from mobly.controllers import android_device
import re
import time
from typing import TypeAlias, Union, Optional


ANDROID_DEVICE: TypeAlias = android_device.AndroidDevice


_AllocateIPerfFacades: list[IPerfFacade] = []


@enum.unique
class IPerfStatusEnum(enum.Enum):
  """iPerf testing status."""

  STOP = 'Stop'
  INIT = 'Init'
  TESTING = 'Testing'


@dataclasses.dataclass
class IPerfTestResult:
    is_done: bool
    output: str


class IPerfFacade:
  """iPerf Facade.

  Before using this class to conduct testing, below conditions must be met:
  1. Open Hotspot of phone at either iPerf server or iPerf client.
  2. Connect phone as iPerf client with phone as iPerf server through hotspot.
  """

  def __init__(
      self, iperf_server: ANDROID_DEVICE, iperf_client: ANDROID_DEVICE,
      iperf_server_as_hotspot: bool = True):
    self._iperf_server: ANDROID_DEVICE = iperf_server
    self._iperf_client: ANDROID_DEVICE = iperf_client
    self._iperf_server_process: Optional[subprocess.Popen] = None
    self._status = IPerfStatusEnum.STOP
    self._iperf_client_wifi_ip: Optional[str] = None
    self._iperf_server_as_hotspot = iperf_server_as_hotspot

  @property
  def iperf_client(self) -> ANDROID_DEVICE:
    """Gets iPerf client."""
    return self._iperf_client

  @property
  def iperf_server(self) -> ANDROID_DEVICE:
    """Gets iPerf server."""
    return self._iperf_server

  @property
  def status(self) -> IPerfStatusEnum:
    """Status of iPerf testing."""
    return self._status

  @property
  def iperf_client_ip(self) -> str:
    """Gets iPerf client IP address.

    Returns:
      iPerf client IP address.

    Raises:
      errors.IPerfClientWifiError:
          Failed to parse the output for WiFi IP address or failed to
          execute the adb command to retrieve the WiFi information.
    """
    stdout, stderr, rt = self.iperf_server.gm.shell(
        'dumpsys wifi | grep mDhcpResultsParcelable')
    if rt != 0 or stderr:
      raise errors.IPerfClientWifiError(
          f'Failed to get iPerf client IP address with rt={rt}: {stderr}')

    matcher = re.search(
       r'IP address ([0-9]+[.][0-9]+[.][0-9]+[.][0-9]+)/\d+\s+Gateway', stdout)
    if not matcher:
      raise errors.IPerfClientWifiError(
          f'Unexpected output from retrieving iPerf client IP: {stdout}')

    return matcher.group(1)

  @property
  def iperf_client_wifi_ip(self) -> str:
    """Gets iPerf client Wifi IP address.

    Returns:
      iPerf client Wifi IP address. (e.g.: "192.168.137.174")

    Raises:
      errors.IPerfClientWifiError:
          Failed to parse the output for WiFi IP address or failed to
          execute the adb command to retrieve the WiFi information.
    """
    stdout, stderr, rt = self.iperf_client.gm.shell(
        'dumpsys wifi | grep mDhcpResultsParcelable')
    if rt != 0 or stderr:
      raise errors.IPerfClientWifiError(
          f'Failed to get WiFi IP from iPerf client with rt={rt}: {stderr}')

    matcher = re.search(
        r'Gateway\s+([0-9]+[.][0-9]+[.][0-9]+[.][0-9]+)\s+DNS', stdout)
    if not matcher:
      raise errors.IPerfClientWifiError(
          f'Unexpected output from retrieving iPerf client Wifi IP: {stdout}')

    return matcher.group(1)

  def init(self):
    """Launches iPerf server and get iPerf client WiFi IP."""
    if (
        self._iperf_server_process is None or
        self._iperf_server_process.poll() is not None):
      self.iperf_server.log.info('Starting iPerf server...')
      cmd = f'adb -s {self.iperf_server.serial} shell iperf3 -s'
      self._iperf_server_process = mobly_utils.start_standing_subprocess(
          cmd.split())
      self.iperf_server.log.info(
          'iPerf is starting with PID=%s', self._iperf_server_process.pid)
    else:
      self.iperf_server.log.info(
          'iPerf is already starting with PID=%s',
          self._iperf_server_process.pid)

    self._status = IPerfStatusEnum.INIT

  def start_test(self, time_sec: int = 5) -> IPerfTestResult:
    """Start iPerf testing.

    Returns:
      iPerf testing result.
    """
    test_result = IPerfTestResult(False, '')
    if self.status != IPerfStatusEnum.INIT:
      test_result.output = f'Under unexpected status={self.status}'
      return test_result

    try:
      self.iperf_client.log.info('Starting iperf client...')
      self._status = IPerfStatusEnum.TESTING
      ip = (
          self.iperf_client_wifi_ip if self._iperf_server_as_hotspot
          else self.iperf_client_ip)
      cmd = (
          f'adb -s {self.iperf_client.serial} shell iperf3 -c'
          f'{ip} -t {time_sec}')
      iperf_client_test_process = mobly_utils.start_standing_subprocess(
          cmd.split())
      while iperf_client_test_process.poll() is None:
        self.iperf_client.log.debug(
            'Waiting for testing...{sleep_count}s/{time_sec}s')
        time.sleep(1)

      out, err = iperf_client_test_process.communicate()
      out = out.decode()
      err = err.decode()
      rc = iperf_client_test_process.returncode
      if rc != 0:
        message = 'Something went wrong with return code={rc}: {out + err}'
        self.iperf_client.log.warning(message)
        test_result.output = message
        return test_result

      test_result.is_done = True
      test_result.output = out
      return test_result
    except Exception as ex:
      test_result.output = str(ex)
    finally:
      self._status = IPerfStatusEnum.INIT

    return test_result

  def uninit(self):
    """Stops iPerf server and testing."""
    if self._iperf_server_process and self._iperf_server_process.poll() is None:
      mobly_utils.stop_standing_subprocess(self._iperf_server_process)
      self._iperf_server_process = None

    self._status = IPerfStatusEnum.STOP


def get_iperf_facade(
    iperf_server: Union[ANDROID_DEVICE, str],
    iperf_client: Union[ANDROID_DEVICE, str],
    iperf_server_as_hotspot: bool = True) -> IPerfFacade:
  """Get iPerf facade instance.

  Args:
    iperf_server: The iPerf server serial or device instance.
    iperf_client: The iPerf client serial or device instance.
    iperf_server_as_hotspot: True to treat `iperf_server` as WiFi hotspot;
        False to treat `iperf_client` as WiFi hotspot.

  Returns:
    iPerf facade instance.
  """
  if (
      isinstance(iperf_server, str) or
      not hasattr(iperf_server, general_utils.BINDING_KEYWORD)):
    iperf_server = general_utils.bind(iperf_server)

  if (
      isinstance(iperf_client, str) or
      not hasattr(iperf_client, general_utils.BINDING_KEYWORD)):
    iperf_client = general_utils.bind(iperf_client)

  iperf_facade = IPerfFacade(
      iperf_server, iperf_client,
      iperf_server_as_hotspot=iperf_server_as_hotspot)
  _AllocateIPerfFacades.append(iperf_facade)
  return iperf_facade


def _free_allocated_iperf_facades():
  """Frees allocated iperf facade object(s)."""
  for facade in _AllocateIPerfFacades:
    if facade != IPerfStatusEnum.STOP:
      facade.uninit()


atexit.register(_free_allocated_iperf_facades)
