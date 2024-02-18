from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x33473058, name="types.InputMediaDocument")
class InputMediaDocument(TLObject):
    flags: Int = TLField(is_flags=True)
    spoiler: bool = TLField(flag=1 << 2)
    id: TLObject = TLField()
    ttl_seconds: Optional[Int] = TLField(flag=1 << 0)
    query: Optional[str] = TLField(flag=1 << 1)
