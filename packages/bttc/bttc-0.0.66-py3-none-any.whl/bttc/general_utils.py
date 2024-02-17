"""General utilities used in Phone testing."""
import logging
import os
import re
import sys
from functools import partial

from bttc import bt_utils
from bttc import constants
from bttc import errors
from bttc.utils import device_factory
from bttc.utils import key_events_handler
from bttc.utils import typing_utils
from mobly import utils
from mobly.controllers import android_device
from mobly.controllers.android_device_lib import adb

import functools
import shlex
from typing import Any, TypeAlias, Union


BINDING_KEYWORD = 'gm'
AUTO_LOAD = True
ANDROID_DEVICE: TypeAlias = android_device.AndroidDevice


class GModule:
  """General module to hold extended functions define in this module."""

  def __init__(self, ad: ANDROID_DEVICE):
    self._ad: ANDROID_DEVICE = ad
    self.dumpsys = partial(dumpsys, self._ad)
    self.get_call_state = partial(get_call_state, self._ad)
    self.get_device_time = partial(get_device_time, self._ad)
    self.get_ui_xml = partial(get_ui_xml, self._ad)
    self.is_apk_installed = partial(is_apk_installed, self._ad)
    self.push_file = partial(push_file, self._ad)
    self.shell = bt_utils.safe_adb_shell(ad)
    self.take_screenshot = partial(take_screenshot, self._ad)

  @property
  def airplane_mode_state(self) -> bool:
    return get_airplane_mode(self._ad)

  @property
  def call_state(self) -> str:
    return self.get_call_state()

  @property
  def device_time(self) -> str:
    return self.get_device_time()

  @property
  def sdk(self) -> str:
    return get_sdk_version(self._ad)

  @property
  def sim_operator(self):
    return get_sim_operator(self._ad)

  def quick_setting_page(self):
    return go_bt_quick_setting_page(self._ad)


def bind(
    ad: Union[ANDROID_DEVICE, str],
    init_mbs: bool = False, init_sl4a: bool = False) -> ANDROID_DEVICE:
  """Binds the input device with functions defined in current module.

  Sample Usage:
  ```python
  >>> from bttc import general_utils
  >>> ad = general_utils.bind('07311JECB08252', init_mbs=True, init_sl4a=True)
  >>> ad.gm.sim_operator
  'Chunghwa Telecom'
  >>> ad.gm.call_state
  'IDLE'
  ```
  """
  device = device_factory.get(ad, init_mbs=init_mbs, init_sl4a=init_sl4a)
  device.load_config({BINDING_KEYWORD: GModule(device)})
  device.ke = key_events_handler.KeyEventHandler(device)

  return device


_CMD_GET_AIRPLANE_MODE_SETTING = 'settings get global airplane_mode_on'


def get_airplane_mode(device: typing_utils.AdbDevice) -> bool:
  """Gets the state of airplane mode.

  Args:
    device: Adb like device.

  Raises:
    adb.Error: Fail to execute adb command.
    ValueError: The output of adb command is unexpected.

  Returns:
    True iff the airplane mode is on.
  """
  shell_output = device.adb.shell(
      _CMD_GET_AIRPLANE_MODE_SETTING).decode(
          constants.ADB_SHELL_CMD_OUTPUT_ENCODING).strip()
  device.log.info('Current airplane mode is %s', shell_output)
  try:
    return bool(int(shell_output))
  except ValueError as ex:
    device.log.warning('Unknown adb output=%s', ex)
    raise


def get_call_state(device: typing_utils.AdbDevice) -> str:
  """Gets call state from dumpsys telecom log.

  For this function to work, we expect below log snippet from given log content:

  Call state is IDLE:
  ```
  mCallAudioManager:
    All calls:
    Active dialing, or connecting calls:
    Ringing calls:
    Holding calls:
    Foreground call:
    null
  ```

  Call state is ACTIVE if there is a single call:
  ```
  mCallAudioManager:
    All calls:
      TC@1
    Active dialing, or connecting calls:
      TC@1
    Ringing calls:
    Holding calls:
    Foreground call:
    [Call id=TC@1, state=ACTIVE, ...
  ```

  Call state is RINGING if there is two calls:
  ```
  mCallAudioManager:
    All calls:
      TC@1
      TC@2
    Active dialing, or connecting calls:
      TC@1
    Ringing calls:
      TC@2
    Holding calls:
    Foreground call:
    [Call id=TC@1, state=ACTIVE, ...
  ```

  Args:
    device: Adb like device.

  Returns:
    Call state of the device.

  Raises:
    adb.Error: If the output of adb commout is not expected.
  """
  output = dumpsys(device, 'telecom', 'mCallAudioManager', '-A11')
  pattern = r'(Ringing) calls:\n\s+TC@\d|Call id=.+state=(\w+)|null'
  match = re.search(pattern, output)
  if match is None:
    raise adb.Error('Failed to execute command for dumpsys telecom')

  return (match.group(1) or match.group(2) or 'IDLE').upper()


_CMD_GET_SDK_VERSION = 'getprop ro.build.version.sdk'


def get_device_time(device: typing_utils.AdbDevice) -> str:
  """Gets device epoch time and transfer to logcat timestamp format."""
  return device.adb.shell(
      'date +"%m-%d %H:%M:%S.000"').decode().splitlines()[0]


@functools.lru_cache
def get_sdk_version(device: typing_utils.AdbDevice) -> int:
  """Gets SDK version of given device.

  Args:
    device: Adb like device.

  Returns:
    SDK version of given device.
  """
  return int(device.adb.shell(shlex.split(_CMD_GET_SDK_VERSION)))


def get_sim_operator(ad: ANDROID_DEVICE) -> str:
  """Gets SIM operator.

  Args:
    ad: Android phone device object.

  Returns:
    SIM Operator or empty string if no SIM card.
  """
  return ad.adb.getprop('gsm.operator.alpha').split(',')[0]


def go_bt_quick_setting_page(ad: ANDROID_DEVICE):
  """Opens Quick Settings."""
  ad.adb.shell(['cmd', 'statusbar', 'expand-settings'])


def dumpsys(ad: typing_utils.AdbDevice,
            service: str,
            keyword: str,
            grep_argument: str = '') -> str:
  """Searches dumpsys log by grep argument and keyword.

  Args:
    ad: Adb like object.
    service: Service name such as "bluetooth_manager".
    keyword: Keyword for search.
    grep_argument: Grep argument for search.

  Returns:
    String of dumpsys that contain keyword.

  Raises:
    UnicodeDecodeError: Fails to conduct the default decoding.
  """
  return ad.adb.shell(
      shlex.split('dumpsys {} | grep {} "{}"'.format(
          shlex.quote(service), grep_argument, shlex.quote(keyword)))).decode()


def get_ui_xml(ad: Any, xml_out_file_path: str) -> str:
  """Gets the XML object of current UI.

  Args:
    ad: Device to dump UI from.
    xml_out_file_path: The host file path to output current UI xml content.

  Returns:
    Current UI xml content.

  Raises:
    errors.MethodError: Fail to dump UI xml.
  """
  dump_xml_name = 'window_dump.xml'
  internal_dump_xml_path = f'/sdcard/{dump_xml_name}'
  ui_xml_content = None
  try:
    ui_xml_content = ad.ui.dump() or ''
  except AttributeError:
    pass

  if not ui_xml_content:
    ad.log.warning('Failed to retrieve UI xml from uiautomator!')
    ad.log.info('Trying `uiautomator dump`...')
    ad.adb.shell(
        f'test -f {internal_dump_xml_path} && rm {internal_dump_xml_path}'
        " || echo 'no need to clean exist dumped xml file'")
    shell_obj = bt_utils.safe_adb_shell(ad)

    last_rt = 0
    last_message = None
    for retry_num in range(5):
      shell_obj('uiautomator dump')
      stdout, stderr, rt = shell_obj(f'test -f {internal_dump_xml_path}')
      if rt != 0:
        # When the dumped xml file doesn't exist, we can try to recover it by
        #   wake up the device and dump again.
        ad.log.warning(
            'Dumped file=%s is missing (rt=%d): %s',
            internal_dump_xml_path, rt, stderr)
        ad.log.warning('Wake up the device to recover this issue...')
        ke_handler = key_events_handler.KeyEventHandler(ad)
        ke_handler.key_wakeup()
        ad.log.info('Collect UI xml again...(retry=%d)', retry_num + 1)
        last_rt = rt
        last_message = f'{stdout}\n{stderr}'
      else:
        break
    else:
      raise errors.MethodError(
          sys._getframe().f_code.co_name,
          f'Failed to retrieve XML content by uiautomator (rt={last_rt}):\n'
          f'{last_message}')
    ad.adb.pull(
        shlex.split(f'{internal_dump_xml_path} {xml_out_file_path}'))
    ui_xml_content = open(xml_out_file_path).read()
  else:
    with open(xml_out_file_path, 'w') as fo:
      fo.write(ui_xml_content)

  if not ui_xml_content:
    raise errors.MethodError(
        sys._getframe().f_code.co_name,
        'Failed to get XML content of current UI!')

  return ui_xml_content


def is_apk_installed(device: typing_utils.AdbDevice, package_name: str,
                     is_full: bool = False) -> bool:
  """Checks if the given apk is installed.

  Below is the output of partial package:
  ```
  # pm list packages
  ...
  package:com.google.android.GoogleCamera
  ```
  Here the partial package name will be:
  'com.google.android.GoogleCamera'

  Below is the output of full package:
  ```
  # pm list packages -f
  ...
  package:/product/app/GoogleCamera/GoogleCamera.apk=com.google.android.GoogleCamera
  ```
  Here the full package name will be:
  '/product/app/GoogleCamera/GoogleCamera.apk=com.google.android.GoogleCamera'

  Args:
    device: Adb like device.
    package_name: APK package name.
    is_full: The given `package_name` is of full path if True. False means the
      `package_name` is partial.

  Returns:
    True iff the given APK package name installed.
  """
  command = (f'pm list packages {"-f" if is_full else ""} '
             f'| grep -w "package:{package_name}"')
  stdout, _, ret_code = bt_utils.safe_adb_shell(device)(command)

  return ret_code == 0 and package_name in stdout


def push_file(
    ad: typing_utils.AdbDevice, src_file_path: str, dst_file_path: str,
    push_timeout_sec: int = 300,
    overwrite_existing: bool = True) -> bool:
  """Pushes file from host file system into given phone.

  Args:
    ad: Adb like object.
    src_file_path: Source file path from host.
    dst_file_path: Destination file path in Phone `ad`.
    push_timeout_sec: How long to wait for the push to finish in seconds.
    overwrite_existing: True to allow overwriting; False to skip push if
        the destination file exist.

  Returns:
    True iff file is pushed successfully.
  """
  src_file_path = os.path.expanduser(src_file_path)

  if not os.path.isfile(src_file_path):
    logging.warning('Source file %s does not exist!', src_file_path)
    return False

  if not overwrite_existing and ad.adb.path_exists(dst_file_path):
    logging.debug(
        "Skip pushing {} to {} as it already exists on device".format(
            src_file_path, dst_file_path))
    return True

  out = ad.adb.push(
      [src_file_path, dst_file_path],
      timeout=push_timeout_sec).decode().rstrip()
  if 'error' in out:
    logging.warning(
        'Failed to copy %s to %s: %s', src_file_path, dst_file_path, out)
    return False

  return True


def take_screenshot(
    ad: typing_utils.AdbDevice,
    host_destination: str,
    file_name: str | None = None) -> str:
  """Takes a screenshot of the device.

  Args:
    ad: Adb like device.
    host_destination: Full path to the directory to save in the host.
    file_name: The file name as screen shot result.

  Returns:
    Full path to the screenshot file on the host.
  """
  if file_name is None:
    time_stamp_string = utils.get_current_human_time().strip()
    time_stamp_string = time_stamp_string.replace(' ', '_').replace(':', '-')
    file_name = f'screenshot_{time_stamp_string}.png'

  device_path = os.path.join('/storage/emulated/0/', file_name)
  ad.adb.shell(shlex.split(f'screencap -p {device_path}'))
  os.makedirs(host_destination, exist_ok=True)
  screenshot_path = os.path.join(host_destination, file_name)
  ad.adb.pull(shlex.split(f'{device_path} {screenshot_path}'))
  ad.log.info('Screenshot taken at %s', screenshot_path)
  ad.adb.shell(shlex.split(f'rm {device_path}'))
  return screenshot_path
