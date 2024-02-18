"""utils around screenshots.
"""

from .icatbase import IcatProcessedDataBase
from tomwer.core.scan.scanbase import TomwerScanBase


class IcatScreenshots(IcatProcessedDataBase):
    """Class to define an icat process publishing screenshot (so to the galery)"""

    def __init__(self, data_dir: str, screenshots: dict, scan: TomwerScanBase) -> None:
        super().__init__(data_dir, scan)
        if not isinstance(screenshots, dict):
            raise TypeError(
                f"Screenshots is expected to be a dict. Get {type(screenshots)} instead."
            )

        self._screenshots = screenshots

    @property
    def screenshots(self):
        return self._screenshots

    def to_dict(self):
        res = super().to_dict()
        res["screenshots_as_dict"] = self.screenshots
        return res
