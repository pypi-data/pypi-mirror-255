"""JSON RPC interface to android scripting engine."""
import time
from typing import Optional

from mobly import utils
from mobly.controllers import android_device
from mobly.controllers.android_device_lib import adb
from mobly.controllers.android_device_lib import event_dispatcher
from bttc.mobly_android_device_lib import jsonrpc_client_base


_APP_NAME = 'SL4A'
_PACKAGE_NAME = 'com.googlecode.android_scripting'
_DEVICE_SIDE_PORT = 8080
_APP_START_RETRIES = 10


class Sl4aClient(jsonrpc_client_base.JsonRpcClientBase):
  """A client for interacting with SL4A using Mobly Snippet Lib.

  Attributes:
    ed: Event dispatcher instance for this SL4A client.
    device_port: Port of the Android device side.
  """

  def __init__(self, ad: android_device.AndroidDevice):
    """Initializes an SL4A client."""
    super().__init__(app_name=_APP_NAME, ad=ad)
    self._ad = ad
    self._adb = ad.adb
    self._user_id = self._adb.current_user_id
    self._conn = None
    self.ed = None
    self.device_port = _DEVICE_SIDE_PORT

  def start_app_and_connect(self) -> None:
    """Starts SL4A app on the android device and connects to it.

    Raises:
      AppStartError: SL4A is not installed.
      AppRestoreConnectionError: When the app was not able to be started.
    """
    # Check that SL4A is installed.
    if not utils.grep(
        _PACKAGE_NAME,
        self._adb.shell(
            ['pm', 'list', 'package', '--user', str(self._user_id)])):
      raise jsonrpc_client_base.AppStartError(
          self._ad,
          f'{self._adb.serial} is not installed on {_APP_NAME} for '
          f'user {self._user_id}')
    self.disable_hidden_api_blacklist()

    # SL4A has problems connecting after disconnection, so kill the apk and
    # try connecting again.
    try:
      self.stop_app()
    except Exception as e:  # pylint: disable=broad-except
      self.log.warning(e)

    # Starts SL4A app by adb command.
    self._adb.shell([
        'am', 'start',
        '-a', f'{_PACKAGE_NAME}.action.LAUNCH_SERVER',
        '--ei', f'{_PACKAGE_NAME}.extra.USE_SERVICE_PORT',
        str(self.device_port),
        f'{_PACKAGE_NAME}/.activity.ScriptingLayerServiceLauncher'])

    # Try to start the connection (not restore the connectivity).
    # The function name restore_app_connection is used here is for the
    # purpose of reusing the same code as it does when restoring the
    # connection. And we do not want to come up with another function
    # name to complicate the API. Change the name if necessary.
    self.restore_app_connection()

  def restore_app_connection(self, port: Optional[int] = None) -> None:
    """Restores the sl4a after device got disconnected.

    Instead of creating new instance of the client:
      - Uses the given port (or find a new available host_port if none is
      given).
      - Tries to connect to remote server with selected port.

    Args:
      port: If given, this is the host port from which to connect to remote
        device port. If not provided, find a new available port as host
        port.

    Raises:
      AppRestoreConnectionError: When the app was not able to be started.
    """
    self.host_port = port or utils.get_available_host_port()
    self._retry_connect()
    self.ed = self._start_event_client()

  def stop_app(self):
    if self._conn:
      # Be polite; let the dest know we're shutting down.
      try:
        self.closeSl4aSession()
      except Exception:  # pylint: disable=broad-except
        self.log.exception('Failed to gracefully shut down %s.',
                           self.app_name)

      # Closes the socket connection.
      self.stop_event_dispatcher()

    # Terminates SL4A app.
    self._adb.shell(f'am force-stop {_PACKAGE_NAME}')

  def stop_event_dispatcher(self) -> None:
    """Stops Event dispatcher."""
    if self.ed is None:
      return
    try:
      self.ed.clean_up()
    except Exception as e:  # pylint: disable=broad-except
      self.log.debug(str(e))
    self.ed = None

  def clear_host_port(self) -> None:
    """Stops the adb port forwarding of the host port used by this client.
    """
    if not self._is_host_port_using():
      return
    try:
      self._ad.adb.forward(['--remove', 'tcp:%d' % self.host_port])
    except adb.AdbError:
      self.log.debug('Host port "%s" has been removed.', self.host_port)
    self.host_port = None

  def _is_host_port_using(self):
    """Returns True if the host port is using by adb."""
    return self.host_port in adb.list_occupied_adb_ports()

  def _retry_connect(self):
    """Connects to SL4A app with retry.

    Raises:
      AppRestoreConnectionError: Failed to connect.
    """
    self._adb.forward([f'tcp:{self.host_port}', f'tcp:{self.device_port}'])
    for _ in range(_APP_START_RETRIES):
      self.log.debug('Attempting to connect %s.', self.app_name)
      try:
        self.connect()
        return
      except Exception:  # pylint: disable=broad-except
        self.log.debug('%s is not yet running, retrying',
                       self.app_name,
                       exc_info=True)
      time.sleep(1)
    raise jsonrpc_client_base.AppRestoreConnectionError(
        self._ad,
        f'{self.app_name} failed to connect for {self._adb.serial} at '
        f'host port {self.host_port}, device port {self.device_port}')

  def _start_event_client(self):
    """Starts an EventDispatcher for the current SL4A session.

    Returns:
      Event dispatcher instance for this SL4A client.
    """
    event_client = Sl4aClient(self._ad)
    event_client.host_port = self.host_port
    event_client.device_port = self.device_port
    event_client.connect(uid=self.uid,
                         cmd=jsonrpc_client_base.JsonRpcCommand.CONTINUE)
    ed = event_dispatcher.EventDispatcher(event_client)
    ed.start()
    return ed
