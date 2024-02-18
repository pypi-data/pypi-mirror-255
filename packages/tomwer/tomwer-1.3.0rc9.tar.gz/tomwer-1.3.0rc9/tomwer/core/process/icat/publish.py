from __future__ import annotations
import os
import logging

from tomwer.core.process.task import Task
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.core.scan.edfscan import EDFTomoScan
from tomwer.core.volume.hdf5volume import HDF5VolumeIdentifier
from tomwer.core.volume.rawvolume import RawVolumeIdentifier
from tomwer.io.utils.raw_and_processed_data import file_is_on_processed_data
from tomoscan.identifier import VolumeIdentifier
from tomoscan.esrf.volume.singleframebase import VolumeSingleFrameBase

from processview.core.manager import DatasetState, ProcessManager

try:
    from pyicat_plus.client.main import IcatClient  # noqa F401
except ImportError:
    has_pyicat_plus = False
else:
    has_pyicat_plus = True

_logger = logging.getLogger(__name__)


class PublishProcessedDataFolderTask(
    Task,
    input_names=(
        "beamline",
        "proposal",
        "dataset",
        "path",
        "raw",
    ),
    optional_input_names=(
        "metadata",
        "dry_run",
    ),
):
    """publish a list of volume to icat for the provided beamline && dataset && proposal"""

    def run(self):
        beamline = self.inputs.beamline
        proposal = self.inputs.proposal
        dataset = self.inputs.dataset
        raw = self.inputs.raw
        metadata = self.get_input_value("metadata", {})
        path = self.inputs.path
        dry_run = self.get_input_value("dry_run", False)

        # checks (need because can be pass by a GUI and will set those values to empty string mostly)
        missing = []
        if beamline in (None, ""):
            missing.append("beamline")
        if proposal in (None, ""):
            missing.append("proposal")
        if dataset in (None, ""):
            missing.append("dataset")
        if raw is None or len(raw) == 0:
            missing.append("raw")

        if len(missing) > 0:
            mess = f"Missing information about {','.join(missing)}"
            _logger.error(mess)
            raise ValueError(mess)
        if not os.path.exists(path):
            raise ValueError(f"path: {path} doesn't exists")

        if not file_is_on_processed_data(str(path)):
            # for now it is safer to limit the publication of metadata to the folder contained in 'PROCESSED_DATA'
            raise ValueError(
                f"processed data dir ({path}) is not in a PROCESSED_DATA folder. Cannot publish it"
            )
        # publish
        if not has_pyicat_plus:
            raise ImportError("pyicat_plus not installed")

        if not dry_run:
            print("will publish")
            from pprint import pprint

            pprint(
                {
                    "beamline": beamline,
                    "proposal": proposal,
                    "dataset": dataset,
                    "path": path,
                    "metadata": metadata,
                    "raw": raw,
                }
            )
            icat_client = IcatClient(
                metadata_urls=("bcu-mq-01.esrf.fr:61613", "bcu-mq-02.esrf.fr:61613")
            )

            icat_client.store_processed_data(
                beamline=beamline,
                proposal=proposal,
                dataset=dataset,
                path=path,
                metadata=metadata,
                raw=raw,
            )


class PublishReconstructedVolumeFromScanTask(
    Task,
    input_names=(
        "data",
        "beamline",
        "proposal",
        "dataset",
    ),
    optional_input_names=(
        "metadata",
        "dry_run",
        "__process__",
    ),
):
    """
    Proxy to PublishProcessedDataTask
    publish processed data from a 'TomwerScanBase' instance. We expect volume to be registered under 'latest_vol_reconstructions' property.
    """

    def __init__(
        self, varinfo=None, inputs=None, node_id=None, node_attrs=None, execinfo=None
    ):
        super().__init__(varinfo, inputs, node_id, node_attrs, execinfo)
        scan = self.inputs.data

        if not isinstance(scan, TomwerScanBase):
            raise TypeError(f"scan is expected to be an instance of {TomwerScanBase}")
        if isinstance(scan, EDFTomoScan):
            raise TypeError(
                "EDFTomoScan is not handling for pushing processed data to icat"
            )
        else:
            raw = from_bliss_original_file_to_raw(scan.get_bliss_orginal_files())

        def get_volume_identifier_path_to_save(volume_identfier):
            assert isinstance(volume_identfier, VolumeIdentifier)
            if isinstance(
                volume_identfier, (HDF5VolumeIdentifier, RawVolumeIdentifier)
            ):
                return os.path.dirname(volume_identfier.file_path)
            elif isinstance(volume_identfier, VolumeSingleFrameBase):
                if volume_identfier.url is not None:
                    return volume_identfier.url.file_path()
                elif volume_identfier.data_url.file_path() is not None:
                    return volume_identfier.data_url.file_path()
            else:
                raise ValueError(
                    f"identifier type {type(volume_identfier)} is not handled"
                )

        paths_to_save = set(
            [
                get_volume_identifier_path_to_save(volume_id)
                for volume_id in scan.latest_vol_reconstructions
            ]
        )
        self._sub_tasks = [
            PublishProcessedDataFolderTask(
                inputs={
                    "beamline": self.inputs.beamline,
                    "proposal": self.inputs.proposal,
                    "dataset": self.inputs.dataset,
                    "path": path_to_save,
                    "raw": raw,
                    "metadata": scan.build_icat_metadata(),
                    "dry_run": self.get_input_value("dry_run", False),
                }
            )
            for path_to_save in paths_to_save
        ]

    def run(self):
        scan = self.inputs.data
        process = self.get_input_value("__process__", None)

        if process is not None:
            ProcessManager().notify_dataset_state(
                dataset=scan,
                process=process(),
                state=DatasetState.ON_GOING,
            )

        try:
            for sub_task in self._sub_tasks:
                sub_task.run()
        except Exception as e:
            if process is not None:
                ProcessManager().notify_dataset_state(
                    dataset=scan,
                    process=process(),
                    state=DatasetState.FAILED,
                )
                raise e
        else:
            if process is not None:
                ProcessManager().notify_dataset_state(
                    dataset=scan,
                    process=process(),
                    state=DatasetState.SUCCEED,
                )


def from_bliss_original_file_to_raw(bliss_original_files: tuple | None) -> tuple:
    """
    convert NXtomo 'bliss_original_files' to icat raw parameter (folder containing the raw)
    without '/mnt/multipath-shares' prefix
    """
    if bliss_original_files is None:
        return None

    # TODO: FIXME
    def fix_path(file_path):
        path = os.path.dirname(file_path)
        if "/mnt/multipath-shares" in path:
            # no simple workaround. abspath return a path with '/mnt/multipath-shares'
            _logger.info(
                "looks like raw data is given with '/mnt/multipath-shares' prefix. Icat will fail on it. Must remove it. No proper other handling found :()"
            )
            # small workaround to fix realpath. Should not be the case anymore so raise an error
            path.replace("/mnt/multipath-shares", "")
        return path

    return tuple([os.path.dirname(bliss_file) for bliss_file in bliss_original_files])
