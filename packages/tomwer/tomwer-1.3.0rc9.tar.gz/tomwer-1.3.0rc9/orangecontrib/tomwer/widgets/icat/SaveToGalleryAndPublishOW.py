# from typing import Optional
# from orangewidget import gui
# from orangewidget.settings import Setting

# from silx.gui import qt
# import weakref
# from ewoksorange.bindings.owwidgets import OWEwoksWidgetOneThreadPerRun

# from tomwer.core.scan.scanbase import TomwerScanBase
# import tomwer.core.process.icat.gallery
# from tomwer.gui.icat.gallery import GalleryWidget, _GalleryOutputDir
# from processview.core.superviseprocess import SuperviseProcess


# class SaveToGalleryAndPublishOW(
#     OWEwoksWidgetOneThreadPerRun,
#     SuperviseProcess,
#     ewokstaskclass=tomwer.core.process.icat.gallery.SaveToGalleryAndPublishTask,
# ):
#     """
#     This widget can receive 'screenshots' signal (expected as a tuple (source, screenshots_dict)
#     source is the tomo obj associated (so we can automate deduction of the output dir)
#     screenshots_dict is a dict of str: DataUrl
#     """

#     name = "Save to gallery and publish"
#     id = "orangecontrib.widgets.tomwer.icat.MoveToGalleryOW.SaveToGalleryAndPublishOW"
#     description = "This widget will save screenshot of reconstruction to a specific location (acquisition gallery as the default end point) \n"
#     icon = "icons/add_gallery.svg"
#     priority = 63
#     keywords = [
#         "tomography",
#         "tomwer",
#         "tomo_obj",
#         "screenshot",
#         "acquisition",
#         "gallery",
#     ]

#     want_main_area = True
#     want_control_area = False
#     resizing_enabled = True

#     _ewoks_default_inputs = Setting(
#         {
#             "format": "png",
#             "output_location_mode": "default",
#             "custom_output": None,
#             "screenshots": None,
#             "overwrite": False,
#         }
#     )

#     _ewoks_inputs_to_hide_from_orange = (
#         "proposal",
#         "dataset",
#         "beamline",
#         "dry_run",
#         "__process__",
#     )

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         SuperviseProcess.__init__(self)
#         self._scan = None
#         self._widget = GalleryWidget(parent=self)

#         self._box = gui.vBox(self.mainArea, self.name)
#         layout = self._box.layout()
#         layout.addWidget(self._widget)

#         # load settings
#         self._widget.setConfiguration(self._ewoks_default_inputs)

#         # connect signal / slot
#         self._widget.sigConfigChanged.connect(self._updateSettings)

#     def _updateSettings(self):
#         self._ewoks_default_inputs = self._widget.getConfiguration()

#     def setScan(self, scan: TomwerScanBase):
#         self._scan = weakref.ref(scan)
#         self._widget._publishConfig.setScan(scan=scan)

#     def getScan(self) -> Optional[TomwerScanBase]:
#         if self._scan is None:
#             return None
#         else:
#             return self._scan()

#     def handleNewSignals(self) -> None:
#         """Invoked by the workflow signal propagation manager after all
#         signals handlers have been called.
#         """
#         # update the widget when receive the scan (proposal, dataset...)
#         screenshots = self.get_task_input_value("screenshots", None)
#         if screenshots is None:
#             return
#         else:
#             scan = screenshots.scan
#             if scan != self.getScan():
#                 self.setScan(scan)

#         if self.get_task_input_value("screenshots", None) is None:
#             return
#         else:
#             super().handleNewSignals()

#     def get_task_inputs(self):
#         task_inputs = super().get_task_inputs()
#         configuration = self._widget.getConfiguration()

#         use_custom_output_dir = _GalleryOutputDir.OutputDirMode.from_value(
#             configuration.get("output_location_mode", "default")
#         )
#         # if user requested to overwrite the output directory
#         if use_custom_output_dir is _GalleryOutputDir.OutputDirMode.PROPOSAL_GALLERY:
#             task_inputs["screenshots"]["output_dir"] = configuration["custom_output"]

#         task_inputs["overwrite"] = configuration["overwrite"]
#         task_inputs["format"] = configuration["output_format"]
#         task_inputs["beamline"] = configuration["beamline"]
#         task_inputs["dataset"] = configuration["dataset"]
#         task_inputs["proposal"] = configuration["proposal"]
#         task_inputs["__process__"] = weakref.ref(self)
#         return task_inputs

#     def sizeHint(self):
#         return qt.QSize(500, 200)
