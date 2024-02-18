import weakref
from typing import Optional
from silx.gui import qt
from ewoksorange.bindings.owwidgets import OWEwoksWidgetOneThreadPerRun
from orangewidget import gui
from orangewidget.settings import Setting

import tomwer.core.process.icat.publish
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.gui.icat.publish import PublishProcessedDataWidget

from processview.core.superviseprocess import SuperviseProcess


class PublishProcessedDataOW(
    OWEwoksWidgetOneThreadPerRun,
    SuperviseProcess,
    ewokstaskclass=tomwer.core.process.icat.publish.PublishReconstructedVolumeFromScanTask,
):
    """
    This widget can receive 'data' (scan) and but some screenshot to be pushed on GALLERY.
    """

    name = "Publish processed data to icat"
    id = "orangecontrib.widgets.tomwer.icat.PublishProcessedDataOW.PublishProcessedDataOW"
    description = "Publish processed data to icat. \n For now we expect processed data to be reconstructed volume"
    icon = "icons/publish.svg"
    priority = 64
    keywords = [
        "tomography",
        "tomwer",
        "tomo_obj",
        "processed data",
        "PROCESSED_DATA",
        "publish",
        "icat",
        "icatplus",
        "pyicatplus",
        "pyicat-plus",
    ]

    want_main_area = True
    want_control_area = False
    resizing_enabled = True

    _ewoks_default_inputs = Setting({})

    _ewoks_inputs_to_hide_from_orange = (
        "__process__",
        "beamline",
        "proposal",
        "dataset",
        "dry_run",
        "path",
    )

    def __init__(self, parent=None):
        super().__init__(parent)
        SuperviseProcess.__init__(self)
        self._widget = PublishProcessedDataWidget(parent=self)
        layout = gui.vBox(self.mainArea, self.name).layout()
        layout.addWidget(self._widget)
        self._scan = None

        # load settings
        self._widget.setConfiguration(self._ewoks_default_inputs)

        # connect signal / slot
        self._widget.sigConfigChanged.connect(self._updateSettings)

    def _updateSettings(self):
        self._ewoks_default_inputs = self._widget.getConfiguration()

    def setScan(self, scan: TomwerScanBase):
        self._scan = weakref.ref(scan)
        self._widget.setScan(scan=scan)

    def getScan(self) -> Optional[TomwerScanBase]:
        if self._scan is None:
            return None
        else:
            return self._scan()

    def handleNewSignals(self) -> None:
        """Invoked by the workflow signal propagation manager after all
        signals handlers have been called.
        """
        # update the widget when receive the scan (proposal, dataset...)
        scan = self.get_task_input_value("data", None)
        if scan is None:
            return
        elif scan != self.getScan():
            self._widget.setScan(scan)
            super().handleNewSignals()
        else:
            super().handleNewSignals()

    def get_task_inputs(self):
        task_inputs = super().get_task_inputs()
        configuration = self._widget.getConfiguration()

        task_inputs["beamline"] = configuration["beamline"]
        task_inputs["proposal"] = configuration["proposal"]
        task_inputs["dataset"] = configuration["dataset"]
        task_inputs["__process__"] = weakref.ref(self)

        print("get task inputs")
        from pprint import pprint

        pprint(task_inputs)

        return task_inputs

    def sizeHint(self):
        return qt.QSize(500, 200)
