import logging

from silx.utils.enum import Enum as _Enum

_logger = logging.getLogger(__name__)


class AxisModeMetadata:
    """
    Util class to store metadata regarding processing of a mode.

    Ease processing and display
    Maybe this function should be part of nabu ?
    """

    def __init__(
        self,
        lockable,
        tooltip="",
        computing_constrains=(),
        allows_padding=False,
        valid_inputs=(),
        valid_sides=(),
    ) -> None:
        self._lockable = lockable
        self._tooltip = tooltip
        self._computing_constrains = computing_constrains
        self._allows_padding = allows_padding
        self._valid_inputs = valid_inputs
        self._valid_sides = valid_sides

    @property
    def is_lockable(self) -> bool:
        return self._lockable

    @property
    def tooltip(self) -> str:
        return self._tooltip

    @property
    def computing_constrains(self) -> tuple:
        return self._computing_constrains

    @property
    def allows_padding(self) -> bool:
        return self._allows_padding

    @property
    def valid_inputs(self) -> tuple:
        return self._valid_inputs

    @property
    def valid_sides(self) -> tuple:
        return self._valid_sides


class _InputType(_Enum):
    SINOGRAM = "sinogram"
    RADIOS_X2 = "2 radios"
    COMPOSITE = "composite"


class _Constrain(_Enum):
    FULL_TURN = "full turn"


class AxisMode(_Enum):
    centered = "centered"
    global_ = "global"
    manual = "manual"
    growing_window_sinogram = "sino-growing-window"
    growing_window_radios = "radios-growing-window"
    sliding_window_sinogram = "sino-sliding-window"
    sliding_window_radios = "radios-sliding-window"
    sino_coarse_to_fine = "sino-coarse-to-fine"
    composite_coarse_to_fine = "composite-coarse-to-fine"
    sino_fourier_angles = "sino-fourier-angles"
    octave_accurate_radios = "radios-octave-accurate"
    read = "read"
    # alias to composite_coarse_to_fine with near mode
    near = "near"

    @classmethod
    def from_value(cls, value):
        # ensure backward compatiblity with workflow defined before COR method on sinograms
        if value == "growing-window":
            _logger.warning(
                "Axis mode requested is 'growing-window'. To insure backward compatibility replace it by 'growing-window-radios'"
            )
            value = AxisMode.growing_window_radios
        elif value == "sliding-window":
            _logger.warning(
                "Axis mode requested is 'sliding-window'. To insure backward compatibility replace it by 'sliding-window-radios'"
            )
            value = AxisMode.sliding_window_radios

        return super().from_value(value=value)


AXIS_MODE_METADATAS = {
    # manual
    AxisMode.manual: AxisModeMetadata(
        lockable=False,
        tooltip="Enter or find manually the COR value",
        computing_constrains=(),
        allows_padding=False,
        valid_inputs=(_InputType.RADIOS_X2,),
    ),
    # read
    AxisMode.read: AxisModeMetadata(
        lockable=False,
        tooltip="Read COR value from a file",
        computing_constrains=(),
        allows_padding=False,
        valid_inputs=None,
    ),
    # radio algorithm
    AxisMode.centered: AxisModeMetadata(
        lockable=True,
        tooltip="Dedicated to fullfield. Previously named 'accurate'",
        computing_constrains=(),
        allows_padding=True,
        valid_inputs=(_InputType.RADIOS_X2,),
    ),
    AxisMode.global_: AxisModeMetadata(
        lockable=True,
        tooltip="Algorithm which can work for both half acquisition and standard ('full field') acquisition",
        computing_constrains=(),
        allows_padding=True,
        valid_inputs=(_InputType.RADIOS_X2,),
    ),
    AxisMode.growing_window_radios: AxisModeMetadata(
        lockable=True,
        tooltip="A auto-Cor method",
        computing_constrains=(),
        allows_padding=True,
        valid_inputs=(_InputType.RADIOS_X2,),
        valid_sides=("left", "right", "center", "all"),
    ),
    AxisMode.sliding_window_radios: AxisModeMetadata(
        lockable=True,
        tooltip="A method for estimating semi-automatically the CoR position. You have to provide a hint on where the CoR is (left, center, right).",
        computing_constrains=(),
        allows_padding=True,
        valid_inputs=(_InputType.RADIOS_X2,),
        valid_sides=("left", "right", "center", "near"),
    ),
    AxisMode.octave_accurate_radios: AxisModeMetadata(
        lockable=True,
        tooltip="Same method as the 'accurate' octave code",
        computing_constrains=(),
        allows_padding=True,
        valid_inputs=(_InputType.RADIOS_X2,),
        valid_sides=("center",),
    ),
    # sinogram algorithm
    AxisMode.growing_window_sinogram: AxisModeMetadata(
        lockable=True,
        tooltip="A auto-Cor method",
        computing_constrains=(),
        allows_padding=True,
        valid_inputs=(_InputType.SINOGRAM,),
        valid_sides=("left", "right", "center", "all"),
    ),
    AxisMode.sliding_window_sinogram: AxisModeMetadata(
        lockable=True,
        tooltip="A method for estimating semi-automatically the CoR position. You have to provide a hint on where the CoR is (left, center, right).",
        computing_constrains=(),
        allows_padding=True,
        valid_inputs=(_InputType.SINOGRAM,),
        valid_sides=("left", "right", "center", "near"),
    ),
    AxisMode.sino_coarse_to_fine: AxisModeMetadata(
        lockable=True,
        tooltip="Estimate CoR from sinogram. Only works for 360 degrees scans.",
        computing_constrains=(_Constrain.FULL_TURN,),
        allows_padding=True,
        valid_inputs=(_InputType.SINOGRAM,),
    ),
    AxisMode.sino_fourier_angles: AxisModeMetadata(
        lockable=True,
        tooltip="",
        computing_constrains=(_Constrain.FULL_TURN,),
        allows_padding=True,
        valid_inputs=(_InputType.SINOGRAM,),
        valid_sides=(
            "left",
            "right",
            "center",
            "near",
        ),
    ),
    # coarse-to-fine algorithm
    AxisMode.composite_coarse_to_fine: AxisModeMetadata(
        lockable=True,
        tooltip="A auto-Cor method",
        computing_constrains=(_Constrain.FULL_TURN,),
        allows_padding=True,
        valid_inputs=(_InputType.COMPOSITE,),
        valid_sides=("left", "right", "center", "near"),
    ),
    AxisMode.near: AxisModeMetadata(
        lockable=True,
        tooltip="Alias to composite_coarse_to_fine",
        computing_constrains=(_Constrain.FULL_TURN,),
        allows_padding=True,
        valid_inputs=(_InputType.COMPOSITE,),
        valid_sides=("left", "right", "center", "near"),
    ),
}
