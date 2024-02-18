from __future__ import annotations
import os
import logging
from silx.utils.enum import Enum as _Enum
from tomwer.io.utils.raw_and_processed_data import (
    to_processed_data_path,
    to_raw_data_path,
)
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.core.utils.scanutils import format_output_location

_logger = logging.getLogger(__name__)


PROCESS_FOLDER_NAME = "reconstructed_volumes"


class ProcessDataOutputDirMode(_Enum):
    IN_SCAN_FOLDER = "same folder as scan"
    PROCESSED_DATA_FOLDER = "PROCESSED_DATA folder"
    RAW_DATA_FOLDER = "RAW_DATA folder"
    OTHER = "other"


class NabuOutputFileFormat(_Enum):
    TIFF = "tiff"
    HDF5 = "hdf5"
    JP2K = "jp2"
    EDF = "edf"
    RAW = "vol"

    @classmethod
    def from_value(cls, value):
        if isinstance(value, str):
            value = value.lstrip(".")
        return super().from_value(value)


def get_file_format(file_str):
    extension = os.path.splitext(file_str.lower())[-1]
    extension = extension.lstrip(".")
    if extension in ("tiff", "tif"):
        return NabuOutputFileFormat.TIFF
    elif extension in ("hdf5", "hdf", "h5"):
        return NabuOutputFileFormat.HDF5
    elif extension in ("jp2", "jp2k", "jpg2k"):
        return NabuOutputFileFormat.JP2K
    elif extension in ("edf",):
        return NabuOutputFileFormat.EDF
    elif extension in ("vol", "raw"):
        return NabuOutputFileFormat.RAW
    else:
        raise ValueError(f"Unrecognized file extension {extension} from {file_str}")


def get_output_folder_from_scan(
    mode: ProcessDataOutputDirMode,
    scan: TomwerScanBase,
    nabu_location: str | None,
    file_basename: str,
    file_format: NabuOutputFileFormat,
) -> tuple[str, str]:
    """
    :return: (location, location_cfg_files). Location is the nabu configuration field 'output/location' 'location_cfg_files' is the information on where to save the nabu configuration file

    """
    output_mode = ProcessDataOutputDirMode.from_value(mode)
    file_format = NabuOutputFileFormat.from_value(file_format)

    if output_mode is ProcessDataOutputDirMode.OTHER and nabu_location in ("", None):
        _logger.info(
            "output dir requested is other bit no path provided. Fall back on the output dir to the scan folder"
        )
        # note: this is only an info because we expect to pass by this one for all .ows configuration (before 1.3 version)
        # as there was no different option by the time
        output_mode = ProcessDataOutputDirMode.IN_SCAN_FOLDER

    if output_mode is ProcessDataOutputDirMode.OTHER:
        assert nabu_location not in (
            "",
            None,
        ), "nabu_location not provided when expected"
        location = format_output_location(nabu_location, scan=scan)
        location_cfg_files = location
    elif output_mode in (
        ProcessDataOutputDirMode.IN_SCAN_FOLDER,
        ProcessDataOutputDirMode.PROCESSED_DATA_FOLDER,
        ProcessDataOutputDirMode.RAW_DATA_FOLDER,
    ):
        # otherwise default location will be the data root level
        location = os.path.join(scan.path, PROCESS_FOLDER_NAME)
        location_cfg_files = location
        if file_format in (
            NabuOutputFileFormat.EDF.value,
            NabuOutputFileFormat.TIFF.value,
            NabuOutputFileFormat.JP2K.value,
        ):  # if user specify the location
            location = "/".join([location, file_basename])
        if output_mode is ProcessDataOutputDirMode.PROCESSED_DATA_FOLDER:
            location = to_processed_data_path(location)
            location_cfg_files = to_processed_data_path(location_cfg_files)
        if output_mode is ProcessDataOutputDirMode.RAW_DATA_FOLDER:
            location = to_raw_data_path(location)
            location_cfg_files = to_raw_data_path(location_cfg_files)
    else:
        raise NotImplementedError(f"mode {output_mode.value} is not implemented yet")

    return location, location_cfg_files
