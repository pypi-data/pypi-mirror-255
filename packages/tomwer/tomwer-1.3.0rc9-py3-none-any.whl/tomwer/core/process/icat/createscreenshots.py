import numpy
from tomwer.core.process.task import Task
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.core.utils.dictutils import concatenate_dict
from tomwer.core.process.icat.screenshots import IcatScreenshots
from tomwer.core.process.icat.gallery import deduce_dataset_gallery_location

from processview.core.manager import DatasetState, ProcessManager


def get_closest_projection(angle, angles_list):
    idx_closest = numpy.argmin(numpy.abs(angles_list - angle))
    return angles_list[idx_closest]


def select_angles(angles_list: tuple, each_angle: int) -> tuple:
    angles_list = sorted(angles_list)
    if len(angles_list) > 0:
        start_angle = angles_list[0]
        stop_angle = angles_list[-1]
        picked_angle = numpy.arange(start_angle, stop_angle + 1, step=each_angle)
        return tuple(
            [get_closest_projection(angle, angles_list) for angle in picked_angle]
        )
    else:
        return tuple()


class CreateRawDataScreenshotsTask(
    Task,
    input_names=("data",),  # screenshots as instance of :class:Screenshots
    optional_input_names=(
        "__process__",
        "raw_projections_required",
        "raw_projections_each",
        "raw_darks_required",
        "raw_flats_required",
    ),
    output_names=("screenshots",),
):
    """
    simple task to create screenshots from raw data
    One raw projection will be picked each 'raw_projections_each' angle (expected in degree)
    If 'with_flat' then will pick the first flat of each serie
    If 'with_dark' then will pick the first dark of each serie
    """

    def run(self):
        process = self.get_input_value("__process__", None)
        scan = self.inputs.data
        if not isinstance(scan, TomwerScanBase):
            raise TypeError(
                f"scan is expected to be an instance of {TomwerScanBase}. Get {type(scan)} instead"
            )
        if process is not None:
            ProcessManager().notify_dataset_state(
                dataset=scan,
                process=process(),
                state=DatasetState.ON_GOING,
            )

        raw_projections_required = self.get_input_value(
            "raw_projections_required", True
        )
        proj_each = self.get_input_value("raw_projections_each", 90)
        raw_flats_required = self.get_input_value("raw_flats_required", True)
        raw_darks_required = self.get_input_value("raw_darks_required", True)

        screenshots_urls = {}
        # dict with screenshot name as key and DataUrl as value
        if raw_darks_required and len(scan.darks) > 0:
            screenshots_urls["dark"] = next(iter(scan.darks.values()))
        if raw_flats_required and len(scan.flats) > 0:
            screenshots_urls["flat"] = next(iter(scan.flats.values()))
        if raw_projections_required:
            projections = scan.projections_with_angle()
            picked_angles = select_angles(
                angles_list=sorted(projections.keys()),
                each_angle=proj_each,
            )
            screenshots_urls = concatenate_dict(
                screenshots_urls,
                {
                    f"projection_{angle:.1f}": projections[angle]
                    for angle in picked_angles
                },
            )

        self.outputs.screenshots = IcatScreenshots(
            data_dir=deduce_dataset_gallery_location(scan),
            screenshots=screenshots_urls,
            scan=scan,
        )

        if process is not None:
            ProcessManager().notify_dataset_state(
                dataset=scan,
                process=process(),
                state=DatasetState.SUCCEED,
            )
