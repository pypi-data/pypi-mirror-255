import platform
from silx.gui import qt
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.gui.utils.qt_utils import block_signals
from tomwer.gui.utils.buttons import PadlockButton


class PublishProcessedDataWidget(qt.QWidget):
    sigConfigChanged = qt.Signal()
    """emit when the configuration changed"""

    KNOW_BEAMLINES = sorted(
        ("bm05", "bm18", "id11", "id15a", "id16a", "id16b", "id17", "id19")
    )

    _TOOLTIP_PAD_LOCKS = "when receive a new scan the value will be updated if valid informations are found. If the field is lock then no update will be done automatically."

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setLayout(qt.QGridLayout())

        # beamline
        self._beamlineCB = qt.QComboBox(self)
        self._beamlineCB.setEditable(True)
        self._beamlineCB.addItems(self.KNOW_BEAMLINES)
        self._beamlineCB.lineEdit().setPlaceholderText("beamline name")
        self.layout().addWidget(
            qt.QLabel("beamline", self),
            0,
            0,
            1,
            1,
        )
        self.layout().addWidget(
            self._beamlineCB,
            0,
            1,
            1,
            1,
        )
        self._beamlinePLB = PadlockButton(self)
        self._beamlinePLB.setToolTip(self._TOOLTIP_PAD_LOCKS)
        self.layout().addWidget(
            self._beamlinePLB,
            0,
            2,
            1,
            1,
        )

        # proposal
        self._proposalQLE = qt.QLineEdit("", self)
        self._proposalQLE.setPlaceholderText("proposal name")
        self.layout().addWidget(
            qt.QLabel("proposal", self),
            1,
            0,
            1,
            1,
        )
        self.layout().addWidget(
            self._proposalQLE,
            1,
            1,
            1,
            1,
        )
        self._proposalPLB = PadlockButton(self)
        self._proposalPLB.setToolTip(self._TOOLTIP_PAD_LOCKS)
        self.layout().addWidget(
            self._proposalPLB,
            1,
            2,
            1,
            1,
        )

        # dataset
        self._datasetQLE = qt.QLineEdit("", self)
        self._datasetQLE.setPlaceholderText("dataset name")
        self.layout().addWidget(
            qt.QLabel("dataset", self),
            2,
            0,
            1,
            1,
        )
        self.layout().addWidget(
            self._datasetQLE,
            2,
            1,
            1,
            1,
        )
        self._datasetPLB = PadlockButton(self)
        self._datasetPLB.setToolTip(self._TOOLTIP_PAD_LOCKS)
        self.layout().addWidget(
            self._datasetPLB,
            2,
            2,
            1,
            1,
        )

        # set up
        default_beamline = self.getDefaultBeamline()
        if default_beamline is not None:
            self._beamlineCB.setCurrentText(default_beamline)

        # connect signal / slot
        self._beamlinePLB.toggled.connect(self._configChanged)
        self._proposalPLB.toggled.connect(self._configChanged)
        self._datasetPLB.toggled.connect(self._configChanged)
        self._beamlineCB.currentTextChanged.connect(self._configChanged)
        self._proposalQLE.textEdited.connect(self._configChanged)
        self._datasetQLE.textEdited.connect(self._configChanged)

    @staticmethod
    def getDefaultBeamline():
        hostname = platform.node()
        for beamline in PublishProcessedDataWidget.KNOW_BEAMLINES:
            if beamline in hostname:
                return beamline

        return None

    def set_auto_update(self, update: bool):
        self._beamlinePLB.setChecked(not update)
        self._proposalPLB.setChecked(not update)
        self._datasetPLB.setChecked(not update)

    def _configChanged(self, *args, **kwargs):
        self.sigConfigChanged.emit()

    def getConfiguration(self) -> dict:
        return {
            "beamline_auto_update": not self._beamlinePLB.isChecked(),
            "dataset_auto_update": not self._datasetPLB.isChecked(),
            "proposal_auto_update": not self._proposalPLB.isChecked(),
            "beamline": self._beamlineCB.currentText(),
            "dataset": self._datasetQLE.text(),
            "proposal": self._proposalQLE.text(),
        }

    def setConfiguration(self, configuration: dict):
        with block_signals(self):
            # handle beamline
            beamline = configuration.get("beamline", None)
            if beamline is not None:
                self._beamlineCB.setCurrentText(beamline)
            beamline_auto_update = configuration.get("beamline_auto_update", None)
            if beamline_auto_update is not None:
                self._beamlinePLB.setChecked(not beamline_auto_update)

            # handle dataset
            dataset = configuration.get("dataset", None)
            if dataset is not None:
                self._datasetQLE.setText(dataset)
            dataset_auto_update = configuration.get("dataset_auto_update", None)
            if dataset_auto_update is not None:
                self._datasetPLB.setChecked(not dataset_auto_update)

            # handle proposal
            proposal = configuration.get("proposal", None)
            if proposal is not None:
                self._proposalQLE.setText(proposal)
            proposal_auto_update = configuration.get("proposal_auto_update", None)
            if proposal_auto_update is not None:
                self._proposalPLB.setChecked(not proposal_auto_update)

        self._configChanged()

    def setScan(self, scan: TomwerScanBase):
        if not isinstance(scan, TomwerScanBase):
            raise TypeError(
                f"scan is expected to be an instance of {TomwerScanBase}, {type(scan)} provided instead"
            )

        new_config = {}
        if not self._proposalPLB.isChecked():
            new_config["proposal"] = scan.get_proposal_name()
        if not self._beamlinePLB.isChecked():
            new_config["beamline"] = scan.instrument_name
        if not self._datasetPLB.isChecked():
            new_config["dataset"] = scan.sample_name

        self.setConfiguration(new_config)
