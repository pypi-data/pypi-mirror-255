"""AVRCP Profile facade entry point."""
from __future__ import annotations

from mobly.controllers import android_device

from bttc import general_utils
from bttc.profiles.avrcp import avrcp_facade
from bttc.profiles.avrcp import avrcp_target_devices
from bttc.utils import typing_utils


ANDROID_DEVICE: TypeAlias = android_device.AndroidDevice


def get_avrcp_facade(
    ad: Union[ANDROID_DEVICE, str],
    music_files: list[str]) -> avrcp_facade.AvrcpFacade:
  """Gets AVRCP Facade."""
  if isinstance(ad, str) or not hasattr(ad, general_utils.BINDING_KEYWORD):
    ad = general_utils.bind(ad, init_sl4a=True)
  elif not hasattr(ad, general_utils.BINDING_KEYWORD):
    init_sl4a = ad.sl4a is None
    ad = general_utils.bind(ad, init_sl4a=init_sl4a)

  if ad.sl4a is None:
    raise ValueError('SL4A service is required from AVRCP Facade!')

  if not music_files:
    raise ValueError('At least one music file should be provided!')

  for music_file_path in music_files:
    ad.push_file(music_file_path, avrcp_facade.ANDROID_TEST_MEDIA_PATH)

  return avrcp_facade.AvrcpFacade(
      avrcp_target_devices.AndroidAvrcpTargetDevice(ad))
