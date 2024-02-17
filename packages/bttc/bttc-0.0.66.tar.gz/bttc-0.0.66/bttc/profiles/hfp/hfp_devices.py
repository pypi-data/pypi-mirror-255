"""Phone implementation from HFP interface PhoneDevice."""

import shlex
import time

from mobly.controllers.android_device_lib import adb

from bttc import general_utils
from bttc.utils import key_events_handler
from bttc.utils import retry
from bttc.utils import typing_utils
from bttc.profiles.hfp import constants
from bttc.profiles.hfp import errors
from bttc.profiles.hfp import hfp_data
from bttc.profiles.hfp import hfp_facade


_RECOVER_ADB_RETRIES = 10
_RECOVER_PHONE_STATE_RETRIES = 10
_SHELL_MAKE_CALL = ('am start -a android.intent.action.CALL -d '
                    'tel:{phone_number}')
_SHELL_LAUNCH_INCALL_UI = (
    'am start -n '
    'com.google.android.dialer/com.android.incallui.LegacyInCallActivity')


class AndroidPhone(hfp_facade.PhoneDevice):
  """Android phone device."""

  def __init__(self, device: typing_utils.AndroidLike,
               phone_number: str):
    super().__init__(phone_number, device.log)
    self._device = general_utils.bind(device)
    self._key_event_handler = (
        key_events_handler.KeyEventHandler(self._device))

  def to_phone_device(self) -> hfp_facade.PhoneDevice:
    """Translates into phone device.

    Returns:
      Phone device.
    """
    return self

  @retry.retry_on_exception(
      retry_value=adb.AdbError,
      retry_intervals=retry.FuzzedExponentialIntervals(
          initial_delay_sec=1, num_retries=_RECOVER_ADB_RETRIES, factor=1.1))
  def is_incall(self) -> bool:
    """Checks if the device is in call or not.

    The output of dumpsys here will look like:
    ```
    Telecom.isInCall(): true
    ```

    Returns:
      True iff the device is in call.
    """
    return (
        'true' in self._device.gm.dumpsys('bluetooth_manager', 'isInCall'))

  @retry.retry_on_exception(
      retry_value=adb.Error,
      retry_intervals=retry.FuzzedExponentialIntervals(
          initial_delay_sec=1, num_retries=_RECOVER_ADB_RETRIES, factor=1.1))
  def get_call_state(self) -> hfp_data.CallStateEnum:
    """Gets the call state of device.

    Returns:
      The call state.

    Raises:
      BrokenPipeError: If called while the socket is disconnected.
      jsonrpc_client_base.Error: Something wrong with SL4A API call.
    """
    return hfp_data.CallStateEnum.from_str(self._device.gm.call_state)

  def wait_for_call_state(self,
                          state: hfp_data.CallStateEnum,
                          timeout_sec: int = 30,
                          wait_interval: int = 3) -> bool:
    """Waits for specific call state.

    Args:
      state: Call state to wait for.
      timeout_sec: Timeout in seconds to wait for the target call state.
      wait_interval: Number of seconds to wait between polling.

    Returns:
      True if the device reaches the target call state.

    Raises:
      BrokenPipeError: If called while the socket is disconnected.
      jsonrpc_client_base.Error: Something wrong with SL4A API call.
    """
    end_time = time.monotonic() + timeout_sec
    while time.monotonic() < end_time:
      if self.get_call_state() == state:
        return True

      time.sleep(wait_interval)

    return False

  def call(self, callee: hfp_facade.PhoneDevice) -> hfp_facade.CallResult:
    """Calls the target device.

    The adb shell output will look like:
    ```
    Starting: Intent { act=android.intent.action.CALL dat=tel:xxx }
    ```

    Args:
      callee: The target device to call.

    Returns:
      dataclass CallResult to represent calling result.
    """
    self._device.adb.shell(
        shlex.split(_SHELL_MAKE_CALL.format(phone_number=callee.phone_number)))

    return hfp_facade.CallResult(self, callee)

  def end_call(self) -> bool:
    """Ends the call.

    Returns:
      True iff the device can reach call state as IDLE.
    """
    call_state = self.get_call_state()
    if call_state != hfp_data.CallStateEnum.IDLE:
      self._device.ke.key_endcall()

    return self.wait_for_call_state(hfp_data.CallStateEnum.IDLE)

  @retry.logged_retry_on_value(
      retry_value=False,
      retry_intervals=retry.FuzzedExponentialIntervals(
          initial_delay_sec=4, num_retries=_RECOVER_PHONE_STATE_RETRIES,
          factor=1.1))
  def answer_call(self) -> bool:
    """Answers the call.

    Returns:
      True iff the device answers call successfully.
    """
    for _ in range(10):
      call_state = self.get_call_state()
      if call_state in (hfp_data.CallStateEnum.ACTIVE,
                        hfp_data.CallStateEnum.ON_HOLD,
                        hfp_data.CallStateEnum.ANSWERING,
                        hfp_data.CallStateEnum.ANSWERED,
                        hfp_data.CallStateEnum.CONNECTING,
                        hfp_data.CallStateEnum.CONNECTED):
        self._device.log.info('%s is already on call!', self)
        return True
      elif call_state in (hfp_data.CallStateEnum.IDLE,
                          hfp_data.CallStateEnum.DIALING,
                          hfp_data.CallStateEnum.DISCONNECTING,
                          hfp_data.CallStateEnum.DISCONNECTED):
        self._device.log.info(
            '%s is under unexpected call state=%s to answer call!', self,
            call_state)
      elif call_state == hfp_data.CallStateEnum.RINGING:
        self._device.log.info('%s is answering the call...', self)
        self._key_event_handler.key_call()
        return self.wait_for_call_state(hfp_data.CallStateEnum.ACTIVE)

      time.sleep(2)
    raise errors.AnswerCallError(
        f'Failed to answer call from {self._device}!')

  def reject_call(self) -> bool:
    """Rejects the call.

    Returns:
      True iff the device rejects call successfully.
    """
    call_state = self.get_call_state()
    if call_state in (hfp_data.CallStateEnum.IDLE,
                      hfp_data.CallStateEnum.DISCONNECTING,
                      hfp_data.CallStateEnum.DISCONNECTED):
      self._device.log.warning('%s is not on call!', self)
      return True
    elif call_state == hfp_data.CallStateEnum.DIALING:
      self._device.log.warning(
          '%s is under unexpected call state=%s to reject call!', self,
          call_state)
      return False
    elif call_state in (hfp_data.CallStateEnum.RINGING,
                        hfp_data.CallStateEnum.ACTIVE,
                        hfp_data.CallStateEnum.ON_HOLD,
                        hfp_data.CallStateEnum.ANSWERING,
                        hfp_data.CallStateEnum.ANSWERED,
                        hfp_data.CallStateEnum.CONNECTING,
                        hfp_data.CallStateEnum.CONNECTED):
      self._device.log.info('%s is rejecting the call...', self)
      self._device.ke.key_endcall()

    return self.wait_for_call_state(hfp_data.CallStateEnum.IDLE)

  def mute_call(self) -> bool:
    """Mutes the call.

    Returns:
      True iff the device mutes call successfully.
    """
    # call_state = self.get_call_state()
    # if call_state != hfp_data.CallStateEnum.ACTIVE:
    #   self._device.log.warning(
    #       '%s is under unexpected call state=%s to mute call!', self,
    #       call_state)
    #   return False
    #
    # self._device.adb.shell(shlex.split(_SHELL_LAUNCH_INCALL_UI))
    # self._device.aud(text='Mute').click()
    # self._device.log.info('call is being muted!')
    # return True
    raise Exception('Not supported yet!')

  def set_call_volume(self, volume: int):
    """Sets volume of call."""
    self._device.sl4a.setVoiceCallVolume(volume)

  def set_call_audio_route(self, audio_route: constants.AudioRoute):
    """Sets call audio route.

    Args:
      audio_route: Audio route to switch to.
    """
    self._device.sl4a.telecomCallSetAudioRoute(audio_route.value)
