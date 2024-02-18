import logging
import os
from math import floor

import numpy
from nxtomomill.converter.hdf5.utils import PROCESSED_DATA_DIR_NAME, RAW_DATA_DIR_NAME
from PIL import Image
from silx.io.url import DataUrl
from silx.utils.enum import Enum as _Enum
from tomoscan.esrf.scan.utils import get_data
from tomoscan.esrf.volume.hdf5volume import HDF5Volume
from tomoscan.esrf.volume.singleframebase import VolumeSingleFrameBase

from tomwer.io.utils.raw_and_processed_data import to_processed_data_path
from tomwer.core.scan.edfscan import EDFTomoScan
from tomwer.core.process.task import Task
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.core.volume.volumebase import TomwerVolumeBase
from tomwer.core.process.icat.screenshots import IcatScreenshots
from tomwer.core.process.icat.publish import (
    PublishProcessedDataFolderTask,
    from_bliss_original_file_to_raw,
)
from processview.core.manager import DatasetState, ProcessManager

_logger = logging.getLogger(__name__)

PROPOSAL_GALLERY_DIR_NAME = "GALLERY"
DATASET_GALLERY_DIR_NAME = "gallery"


class OutputFormat(_Enum):
    """possible output format to save screenshots"""

    PNG = "png"
    JPEG = "jpg"


class Binning(_Enum):
    ONE_BY_ONE = "1x1"
    TWO_BY_TWO = "2x2"
    FOUR_BY_FOUR = "4x4"
    HEIGHT_BY_HEIGHT = "8x8"
    SIXTEEN_BY_SIXTEEN = "16x16"
    THIRTY_TWO_BY_THIRTY_TWO = "32x32"
    SIXTY_FOUR_BY_SIXTY_FOUR = "64x64"
    ONE_HUNDRED_TWENTY_HEIGHT_BY_ONE_HUNDRED_TWENTY_HEIGHT = "128x128"

    @staticmethod
    def _bin_data(data, binning):
        if not isinstance(data, numpy.ndarray):
            raise TypeError("data should be a numpy array")
        if not data.ndim == 2:
            raise ValueError("data is expected to be 2d")
        binning = Binning.from_value(binning)
        if binning is Binning.ONE_BY_ONE:
            return data
        elif binning is Binning.TWO_BY_TWO:
            return data[::2, ::2]
        elif binning is Binning.FOUR_BY_FOUR:
            return data[::4, ::4]
        elif binning is Binning.HEIGHT_BY_HEIGHT:
            return data[::8, ::8]
        elif binning is Binning.SIXTEEN_BY_SIXTEEN:
            return data[::16, ::16]
        elif binning is Binning.THIRTY_TWO_BY_THIRTY_TWO:
            return data[::32, ::32]
        elif binning is Binning.SIXTY_FOUR_BY_SIXTY_FOUR:
            return data[::64, ::64]
        else:
            raise NotImplementedError


def deduce_dataset_gallery_location(scan_obj: TomwerScanBase) -> str:
    """
    From scan path deduce the 'dataset' path to the gallery.
    Warning: dataset gallery is different then the 'proposal' gallery
    """
    if not isinstance(scan_obj, TomwerScanBase):
        raise TypeError(f"'scan_obj' is expected to be an instance of {TomwerScanBase}")

    file_path = os.path.abspath(scan_obj.path)

    split_path = file_path.split(os.sep)
    # reverse it to find the lower level value of 'PROCESSED_DATA_DIR_NAME' or 'RAW_DATA_DIR_NAME' if by any 'chance' has several in the path
    # then we will replace the 'lower one' in the string. This is where the GALLERY will be added
    split_path = split_path[::-1]
    # check if already contain in a "PROCESSED_DATA" directory
    try:
        index_processed_data = split_path.index(PROCESSED_DATA_DIR_NAME)
    except ValueError:
        pass
        index_processed_data = None
    try:
        index_raw_data = split_path.index(RAW_DATA_DIR_NAME)
    except ValueError:
        # if the value is not in the list
        index_raw_data = None

    if index_processed_data is None and index_raw_data is None:
        # if not in any "PROCESSED_DATA" or "RAW_DATA" directory
        return scan_obj.get_relative_file(
            file_name=DATASET_GALLERY_DIR_NAME, with_dataset_prefix=False
        )
    elif index_processed_data is not None and index_raw_data is not None:
        if index_raw_data > index_processed_data:
            # if PROCESSED_DATA lower in the path than RAW_DATA
            split_path[index_processed_data] = RAW_DATA_DIR_NAME
    # reorder path to original
    split_path = list(split_path[::-1])
    split_path.append(DATASET_GALLERY_DIR_NAME)
    # move it to PPROCESSED_DATA when possible
    path = os.sep.join(split_path)
    path = to_processed_data_path(path)
    return path


def deduce_proposal_GALLERY_location(scan_obj: TomwerScanBase) -> str:
    """
    Policy: look if the scan_obj.path is in 'PROCESSED_DATA_DIR_NAME' or 'RAW_DATA_DIR_NAME' directories.
    If find any (before any 'GALLERY_DIR_NAME' directory) replace it "GALLERY_DIR_NAME".
    If none of those are found then create it at the same level as the scan

    :param TomwerScanBase scan_obj: scan_obj for which we want the GALLERY directory
    :return: gallery path (to save screeshots for example)
    """
    if not isinstance(scan_obj, TomwerScanBase):
        raise TypeError(f"'scan_obj' is expected to be an instance of {TomwerScanBase}")

    file_path = os.path.abspath(scan_obj.path)

    split_path = file_path.split(os.sep)
    # reverse it to find the lower level value of 'PROCESSED_DATA_DIR_NAME' or 'RAW_DATA_DIR_NAME' if by any 'chance' has several in the path
    # then we will replace the 'lower one' in the string. This is where the GALLERY will be added
    split_path = split_path[::-1]
    # check if already contain in a "PROCESSED_DATA" directory
    try:
        index_processed_data = split_path.index(PROCESSED_DATA_DIR_NAME)
    except ValueError:
        pass
        index_processed_data = None
    try:
        index_raw_data = split_path.index(RAW_DATA_DIR_NAME)
    except ValueError:
        # if the value is not in the list
        index_raw_data = None

    if index_processed_data is None and index_raw_data is None:
        # if not in any "PROCESSED_DATA" or "RAW_DATA" directory
        return scan_obj.get_relative_file(
            file_name=PROPOSAL_GALLERY_DIR_NAME, with_dataset_prefix=False
        )
    elif index_processed_data is not None and index_raw_data is not None:
        if index_raw_data > index_processed_data:
            # if PROCESSED_DATA lower in the path than RAW_DATA
            split_path[index_processed_data] = PROPOSAL_GALLERY_DIR_NAME
        else:
            # if RAW_DATA lower in the path than PROCESSED_DATA
            split_path[index_raw_data] = PROPOSAL_GALLERY_DIR_NAME
    elif index_raw_data is not None:
        # if the path contains only PROCESSED_DATA or RAW_DATA (expected behavior for online acquistion)
        split_path[index_raw_data] = PROPOSAL_GALLERY_DIR_NAME
    else:
        assert index_processed_data is not None, "index_processed_data is None"
        split_path[index_processed_data] = PROPOSAL_GALLERY_DIR_NAME

    # reorder path to original
    split_path = split_path[::-1]
    return os.sep.join(split_path)


def select_screenshot_from_volume(volume: TomwerVolumeBase) -> dict:
    """
    return a subset of url for a volume.
    Warning: this function will be called each time a nabu slice or a nabu volume is executer from orangecontrig.
    So it must stay 'low processing' function to avoid slowing down everything
    """
    if not isinstance(volume, TomwerVolumeBase):
        raise TypeError(
            f"volume is expected to be an instance of {TomwerVolumeBase}. Get {type(volume)}"
        )

    if isinstance(volume, VolumeSingleFrameBase):
        volume_urls = tuple(volume.browse_data_urls())
        # lets take the three equally spaced slices (3/6, 4/6 and 5/6)
        n_slices = len(volume_urls)
        # note: using a dict ensure to get a set of DataUrl in case an Url is used several time
        # workaround: DataUrl is not hashable
        screenshots = {
            f"{os.path.splitext(os.path.basename(volume_urls[floor(i * n_slices / 6)].file_path()))}": volume_urls[
                floor(i * n_slices / 6)
            ]
            for i in range(2, 5)
        }
        return screenshots
    elif isinstance(volume, HDF5Volume):
        volume_url = next(volume.browse_data_urls())
        n_slices = volume.get_volume_shape()[0]
        # note: using a dict ensure to get a set of DataUrl in case an Url is used several time
        # workaround: DataUrl is not hashable
        screenshots = {
            f"{os.path.splitext(os.path.basename(volume_url.file_path()))[0]}_{floor(i / 6 * n_slices)}": DataUrl(
                file_path=volume_url.file_path(),
                data_path=volume_url.data_path(),
                scheme="silx",
                data_slice=floor(i / 6 * n_slices),
            )
            for i in range(2, 5)
        }
        return screenshots
    else:
        _logger.warning(
            f"volume {type(volume)} does not allow to create screenshot for now"
        )
        return ()


class SaveScreenshotsToGalleryTask(
    Task,
    input_names=("screenshots",),  # screenshots as instance of :class:Screenshots
    optional_input_names=("format", "overwrite", "binning"),
):
    """simple task to do the binding between orange design and 'SaveScreenshotsTask'"""

    def run(self):
        if not isinstance(self.inputs.screenshots, IcatScreenshots):
            raise TypeError(
                f"'screenshots' is expected to be an instance of {IcatScreenshots}. get {type(self.inputs.screenshots)}"
            )

        inputs = self.inputs.screenshots.to_dict()
        if self.get_input_value("overwrite", None) is not None:
            inputs["overwrite"] = self.inputs.overwrite
        if self.get_input_value("format", None) is not None:
            inputs["format"] = self.inputs.format
        if self.get_input_value("binning", None) is not None:
            inputs["binning"] = self.inputs.binning
        task = SaveScreenshotsTask(
            inputs=inputs,
        )
        task.run()


class SaveScreenshotsTask(
    Task,
    input_names=("screenshots_as_dict", "output_dir"),
    optional_input_names=("format", "overwrite", "binning"),
):
    """Task which save a set of screenshot to the output_dir under required format"""

    def run(self):
        format = OutputFormat.from_value(
            self.get_input_value("format", OutputFormat.PNG)
        )
        overwrite = self.get_input_value("overwrite", False)
        binning = self.get_input_value("binning", Binning.ONE_BY_ONE)

        os.makedirs(self.inputs.output_dir, exist_ok=True)
        for screenshot_name, data_url in self.inputs.screenshots_as_dict.items():
            if not isinstance(data_url, DataUrl):
                raise TypeError("screenshot values are expected to DataUrl")
            data = get_data(data_url)
            if not isinstance(data, numpy.ndarray) and data.ndim != 2:
                raise TypeError("screenshot are expected to be 2D numpy arrays")
            if not isinstance(screenshot_name, str):
                raise TypeError(
                    f"screenshot keys are expected to be str. Get {type(screenshot_name)}"
                )

            if data.ndim == 3 and data.shape[0] == 1:
                data = data.reshape(data.shape[1:])
            elif data.ndim != 2:
                raise ValueError(
                    f"only 2D grayscale image are handled. Get {data.shape}"
                )
            # if qt is available use it as this is simpler and more powerful
            # clamp data in 0-256
            data = data.astype(numpy.float32)
            data = Binning._bin_data(data=data, binning=binning)
            data *= 255.0 / data.max()

            # do a rescale else use qt instead
            img = Image.fromarray(data, mode=None)
            img = img.convert("L")
            output_file = os.path.join(
                self.inputs.output_dir,
                ".".join([screenshot_name, format.value]),
            )
            if not overwrite and os.path.exists(output_file):
                raise OSError(f"File already exists ({output_file})")
            img.save(output_file)


class SaveToGalleryAndPublishTask(
    Task,
    input_names=(
        "screenshots",
        "beamline",
        "dataset",
        "proposal",
        "format",
    ),
    optional_input_names=(
        "dry_run",
        "__process__",
    ),
):
    def __init__(
        self, varinfo=None, inputs=None, node_id=None, node_attrs=None, execinfo=None
    ):
        super().__init__(varinfo, inputs, node_id, node_attrs, execinfo)
        self._process = self.get_input_value("__process__", None)
        self._task_save = SaveScreenshotsToGalleryTask(
            inputs=inputs,
        )

        scan = self.inputs.screenshots.scan
        if isinstance(scan, EDFTomoScan):
            raise TypeError(
                "scan is an EDFTomoScan. Not handled for publishing processed data to icat"
            )
        raw = from_bliss_original_file_to_raw(scan.get_bliss_orginal_files())

        path = self.inputs.screenshots.data_dir
        # path = os.path.dirname(self.inputs.screenshots.data_dir)

        self._task_publish = PublishProcessedDataFolderTask(
            inputs={
                "beamline": self.inputs.beamline,
                "dataset": self.inputs.dataset,
                "proposal": self.inputs.proposal,
                "path": path,  # must be the dataset path
                "raw": raw,
                "dry_run": self.get_input_value("dry_run", False),
                "metadata": self.inputs.screenshots.metadata,
            },
        )

    def run(self):
        if self._process is not None:
            ProcessManager().notify_dataset_state(
                dataset=self.inputs.screenshots.scan,
                process=self._process(),
                state=DatasetState.ON_GOING,
            )
        # save screenshots to gallery
        try:
            self._task_save.run()
        except Exception as e:
            if self._process is not None:
                ProcessManager().notify_dataset_state(
                    dataset=self.inputs.screenshots.scan,
                    process=self._process(),
                    state=DatasetState.FAILED,
                    details=str(e),
                )
            raise e

        # publication
        try:
            self._task_publish.run()
        except Exception as e:
            if self._process is not None:
                ProcessManager().notify_dataset_state(
                    dataset=self.inputs.screenshots.scan,
                    process=self._process(),
                    state=DatasetState.FAILED,
                    details=str(e),
                )
            raise e
        else:
            if self._process is not None:
                ProcessManager().notify_dataset_state(
                    dataset=self.inputs.screenshots.scan,
                    process=self._process(),
                    state=DatasetState.SUCCEED,
                )
