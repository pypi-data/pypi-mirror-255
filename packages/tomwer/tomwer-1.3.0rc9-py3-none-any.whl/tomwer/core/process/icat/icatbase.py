import weakref
from tomwer.core.scan.scanbase import TomwerScanBase


class IcatProcessedDataBase:
    """
    Container class to get all the information about processed data to be publish
    """

    def __init__(self, data_dir: str, scan: TomwerScanBase) -> None:
        self._output_dir = data_dir
        # output dir for the screenshots. The default is expected to be provided by the task creating the screenshot.
        # it can be overwrite by the 'SaveScreenshotTask' if an output dir is provided
        self._scan = weakref.ref(scan) if scan is not None else scan

    @property
    def data_dir(self):
        return self._output_dir

    @property
    def scan(self):
        return self._scan() if self._scan is not None else None

    @property
    def metadata(self) -> dict:
        scan = self.scan
        if scan is not None:
            return scan.build_icat_metadata()
        else:
            return {}

    def to_dict(self):
        return {
            "output_dir": self.data_dir,
            "icat_metadata": self.metadata,
        }
