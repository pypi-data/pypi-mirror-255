#  Pyrofork - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#  Copyright (C) 2022-present Mayuri-Chan <https://github.com/Mayuri-Chan>
#
#  This file is part of Pyrofork.
#
#  Pyrofork is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrofork is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrofork.  If not, see <http://www.gnu.org/licenses/>.

from io import BytesIO

from pyrofork.raw.core.primitives import Int, Long, Int128, Int256, Bool, Bytes, String, Double, Vector
from pyrofork.raw.core import TLObject
from pyrofork import raw
from typing import List, Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


class GetGroupCall(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``173``
        - ID: ``41845DB``

    Parameters:
        call (:obj:`InputGroupCall <pyrofork.raw.base.InputGroupCall>`):
            N/A

        limit (``int`` ``32-bit``):
            N/A

    Returns:
        :obj:`phone.GroupCall <pyrofork.raw.base.phone.GroupCall>`
    """

    __slots__: List[str] = ["call", "limit"]

    ID = 0x41845db
    QUALNAME = "functions.phone.GetGroupCall"

    def __init__(self, *, call: "raw.base.InputGroupCall", limit: int) -> None:
        self.call = call  # InputGroupCall
        self.limit = limit  # int

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "GetGroupCall":
        # No flags
        
        call = TLObject.read(b)
        
        limit = Int.read(b)
        
        return GetGroupCall(call=call, limit=limit)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.call.write())
        
        b.write(Int(self.limit))
        
        return b.getvalue()
