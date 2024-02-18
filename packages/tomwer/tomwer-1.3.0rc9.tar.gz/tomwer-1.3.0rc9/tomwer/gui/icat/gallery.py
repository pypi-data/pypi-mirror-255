import os
from silx.gui import qt
from silx.utils.enum import Enum as _Enum
from tomwer.core.process.icat.gallery import OutputFormat
from tomwer.gui.qlefilesystem import QLFileSystem
from tomwer.io.utils import get_default_directory
from tomwer.core.utils.dictutils import concatenate_dict
from tomwer.core.process.icat.gallery import Binning

from .publish import PublishProcessedDataWidget


class _GalleryOutputDir(qt.QGroupBox):
    class OutputDirMode(_Enum):
        DATASET_GALLERY = "dataset gallery"
        PROPOSAL_GALLERY = "proposal GALLERY"
        CUSTOM = "custom"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(qt.QGridLayout())
        # dataset gallery option
        self._datasetGalleryQRB = qt.QRadioButton(
            self.OutputDirMode.DATASET_GALLERY.value, self
        )
        self.layout().addWidget(self._datasetGalleryQRB, 0, 0, 1, 4)
        # proposal gallery option
        self._proposalGalleryQRB = qt.QRadioButton(
            self.OutputDirMode.PROPOSAL_GALLERY.value, self
        )
        self.layout().addWidget(self._proposalGalleryQRB, 1, 0, 1, 4)

        # other option
        self._otherQRB = qt.QRadioButton(self.OutputDirMode.CUSTOM.value, self)
        self._otherQRB.setCheckable(True)
        self.layout().addWidget(self._otherQRB, 2, 0, 1, 4)

        self._otherQLE = QLFileSystem(
            "", self, filters=qt.QDir.NoDotAndDotDot | qt.QDir.Dirs
        )
        self.layout().addWidget(self._otherQLE, 3, 1, 1, 2)
        style = qt.QApplication.style()
        icon_opendir = style.standardIcon(qt.QStyle.SP_DirOpenIcon)
        self._selectOtherQLE = qt.QPushButton(icon_opendir, "", self)
        self._selectOtherQLE.setIcon(icon_opendir)
        self.layout().addWidget(self._selectOtherQLE, 3, 3, 1, 1)

        # button group
        self._buttonGroup = qt.QButtonGroup()
        self._buttonGroup.setExclusive(True)
        self._buttonGroup.addButton(self._datasetGalleryQRB)
        self._buttonGroup.addButton(self._proposalGalleryQRB)
        self._buttonGroup.addButton(self._otherQRB)

        # vertical spacer
        self._vSpacer = qt.QWidget(self)
        self._vSpacer.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Expanding)
        self.layout().addWidget(self._vSpacer, 99, 0, 1, 1)

        # set up GUI
        self._datasetGalleryQRB.setChecked(True)
        self._modeChanged()

        # connect signal / slot
        self._buttonGroup.buttonClicked.connect(self._modeChanged)
        self._selectOtherQLE.released.connect(self._selectOutput)

    def _selectOutput(self):  # pragma: no cover
        defaultDirectory = self._selectOtherQLE.text()
        if not os.path.isdir(defaultDirectory):
            defaultDirectory = get_default_directory()

        dialog = qt.QFileDialog(self, directory=defaultDirectory)
        dialog.setFileMode(qt.QFileDialog.DirectoryOnly)

        if not dialog.exec_():
            dialog.close()
            return

        self._selectOtherQLE.setText(dialog.selectedFiles()[0])

    def getOutputFolderMode(self):
        if self._datasetGalleryQRB.isChecked():
            return _GalleryOutputDir.OutputDirMode.DATASET_GALLERY
        elif self._proposalGalleryQRB.isChecked():
            return _GalleryOutputDir.OutputDirMode.PROPOSAL_GALLERY
        elif self._otherQRB.isChecked():
            return _GalleryOutputDir.OutputDirMode.CUSTOM
        else:
            raise NotImplementedError

    def setOutputFolderMode(self, mode):
        mode = _GalleryOutputDir.OutputDirMode.from_value(mode)
        if mode is _GalleryOutputDir.OutputDirMode.PROPOSAL_GALLERY:
            self._proposalGalleryQRB.setChecked(True)
        elif mode is _GalleryOutputDir.OutputDirMode.DATASET_GALLERY:
            self._datasetGalleryQRB.setChecked(True)
        elif mode is _GalleryOutputDir.OutputDirMode.CUSTOM:
            self._otherQRB.setChecked(True)
        else:
            raise NotImplementedError
        self._modeChanged()

    def getOtherOutputDir(self):
        return self._otherQLE.text()

    def setOtherOutputDir(self, path: str):
        self._otherQLE.setText(path)

    def _modeChanged(self, *args, **kwargs):
        custom_active = self._otherQRB.isChecked()
        self._otherQLE.setEnabled(custom_active)
        self._selectOtherQLE.setEnabled(custom_active)


class GalleryWidget(qt.QWidget):
    """Widget to let the user define the output location of the screenshots"""

    sigConfigChanged = qt.Signal()
    """emit when the configuration has changed"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(qt.QFormLayout())

        # screenshot precision
        self._precisonQCB = qt.QComboBox(self)
        self._precisonQCB.addItem("uint8")
        self.layout().addRow("precision", self._precisonQCB)
        # binning
        self._binningQCB = qt.QComboBox(self)
        self._binningQCB.addItems(Binning.values())
        self.layout().addRow("binning", self._binningQCB)
        self._binningQCB.setCurrentText(Binning.SIXTEEN_BY_SIXTEEN.value)
        self._binningQCB.setToolTip(
            "To speed up display of the gallery at the data portal side it is highly recommended to bin screenshots"
        )  # recommanded size: 5ko for the entire gallery
        # output format
        self._outputFormat = qt.QComboBox(self)
        self._outputFormat.addItems(OutputFormat.values())
        self.layout().addRow("outoutput_location_modeput format", self._outputFormat)
        # gallery output dir
        self._outputDirWidget = _GalleryOutputDir(self)
        self._outputLocationLabel = qt.QLabel("output location", self)
        self.layout().addRow(self._outputLocationLabel, self._outputDirWidget)
        self._outputDirWidget.hide()
        self._outputLocationLabel.hide()
        # overwrite
        self._overwriteCB = qt.QCheckBox("overwrite", self)
        self._overwriteCB.setChecked(True)
        self.layout().addRow(self._overwriteCB)
        # publishing setting
        self._publishConfig = PublishProcessedDataWidget(self)
        self._publisherGB = qt.QGroupBox("icat info")
        self._publisherGB.setLayout(qt.QVBoxLayout())
        self._publisherGB.layout().addWidget(self._publishConfig)
        self.layout().addRow(self._publisherGB)
        # connect signal / slot
        self._outputFormat.currentIndexChanged.connect(self._configChanged)
        self._overwriteCB.toggled.connect(self._configChanged)
        self._publishConfig.sigConfigChanged.connect(self.sigConfigChanged)
        self._binningQCB.currentIndexChanged.connect(self._configChanged)

    def getOutputFormat(self) -> OutputFormat:
        return OutputFormat.from_value(self._outputFormat.currentText())

    def setOutputFormat(self, format: OutputFormat):
        format = OutputFormat.from_value(format)
        self._outputFormat.setCurrentText(format.value)

    def getBinning(self) -> Binning:
        return Binning.from_value(self._binningQCB.currentText())

    def setBinning(self, binning: Binning):
        binning = Binning.from_value(binning)
        self._binningQCB.setCurrentText(binning.value)

    def getConfiguration(self):
        return concatenate_dict(
            self._publishConfig.getConfiguration(),
            {
                "output_format": self.getOutputFormat().value,
                "output_location_mode": self._outputDirWidget.getOutputFolderMode().value,
                "custom_output": self._outputDirWidget.getOtherOutputDir(),
                "overwrite": self._overwriteCB.isChecked(),
                "binning": self.getBinning().value,
            },
        )

    def setConfiguration(self, config: dict):
        self._publishConfig.setConfiguration(config)
        output_format = config.get("output_format", None)
        if output_format is not None:
            self.setOutputFormat(output_format)

        output_location_mode = config.get("output_location_mode", None)
        if output_location_mode is not None:
            self._outputDirWidget.setOutputFolderMode(output_location_mode)

        custom_output = config.get("custom_output", None)
        if custom_output is not None:
            self._outputDirWidget.setOtherOutputDir(custom_output)

        overwrite = config.get("overwrite", None)
        if overwrite is not None:
            overwrite = overwrite in (True, "True", 1)
            self._overwriteCB.setChecked(overwrite)

        binning = config.get("binning", None)
        if binning is not None:
            self.setBinning(binning=binning)

    def _configChanged(self, *args, **kwargs):
        self.sigConfigChanged.emit()
