"""Define nabu Axis"""

from silx.utils.enum import Enum as _Enum


class NabuPlane(_Enum):
    YZ = "YZ"
    XZ = "XZ"
    XY = "XY"
