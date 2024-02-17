"""HFP Profile facade entry point."""
from bttc.utils import typing_utils
from bttc.profiles.hfp import hfp_facade
from bttc.profiles.hfp import hfp_devices


def get_phones_hfp_facade(
    caller: typing_utils.AndroidLike,
    caller_phone_number: str,
    callee: typing_utils.AndroidLike,
    callee_phone_number: str) -> hfp_facade.HFPFacade:
  """Get HFP facade by two phone devices."""
  ad_phone_caller = hfp_devices.AndroidPhone(caller, caller_phone_number)
  ad_phone_callee = hfp_devices.AndroidPhone(callee, callee_phone_number)

  return hfp_facade.HFPFacade(
      caller_device=ad_phone_caller,
      callee_device=ad_phone_callee)
