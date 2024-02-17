"""AVRCP Profile facade entry point."""
from __future__ import annotations

import os
from typing import TypeAlias, Union

from mobly.controllers import android_device

from bttc import general_utils
from bttc.profiles.avrcp import avrcp_facade
from bttc.profiles.avrcp import avrcp_target_devices


ANDROID_DEVICE: TypeAlias = android_device.AndroidDevice


def get_facade(
    ad: Union[ANDROID_DEVICE, str],
    music_files: list[str]) -> avrcp_facade.AvrcpFacade:
  """Gets AVRCP Facade."""
  if isinstance(ad, str) or not hasattr(ad, general_utils.BINDING_KEYWORD):
    ad = general_utils.bind(ad, init_sl4a=True)
  elif not hasattr(ad, general_utils.BINDING_KEYWORD):
    init_sl4a = ad.sl4a is None
    ad = general_utils.bind(ad, init_sl4a=init_sl4a)

  if not hasattr(ad, general_utils.BINDING_KEYWORD):
    raise ValueError(
        f'submodule {general_utils.BINDING_KEYWORD} is not loaded!')

  if ad.sl4a is None:
    raise ValueError('SL4A service is required from AVRCP Facade!')

  if not music_files:
    raise ValueError('At least one music file should be provided!')

  for music_file_path in music_files:
    src_file_name = os.path.basename(music_file_path)
    dst_full_file_path = os.path.join(
        avrcp_facade.ANDROID_TEST_MEDIA_PATH, src_file_name)
    print(f'Pushing file {music_file_path} to {dst_full_file_path} ...')
    ad.gm.push_file(music_file_path, dst_full_file_path)

  return avrcp_facade.AvrcpFacade(
      avrcp_target_devices.AndroidAvrcpTargetDevice(ad))
