# from orangewidget import gui
# from orangewidget.settings import Setting

# from silx.gui import qt
# import weakref
# from ewoksorange.bindings.owwidgets import OWEwoksWidgetOneThreadPerRun

# import tomwer.core.process.icat.createscreenshots
# from tomwer.gui.icat.createscreenshots import CreateRawDataScreenshotsWidget
# from processview.core.superviseprocess import SuperviseProcess


# class RawDataScreenshotCreatorOW(
#     OWEwoksWidgetOneThreadPerRun,
#     SuperviseProcess,
#     ewokstaskclass=tomwer.core.process.icat.createscreenshots.CreateRawDataScreenshotsTask,
# ):
#     """
#     This widget can receive 'data' (scan) and but some screenshot to be pushed on GALLERY.
#     """

#     name = "Create raw data screenshots"
#     id = "orangecontrib.widgets.tomwer.icat.RawDataScreenshotCreatorOW.RawDataScreenshotCreatorOW"
#     description = "Create screenshot of the raw data from user wishes. \n"
#     icon = "icons/raw_screenshots.svg"
#     priority = 63
#     keywords = [
#         "tomography",
#         "tomwer",
#         "tomo_obj",
#         "screenshot",
#         "raw data",
#     ]

#     want_main_area = True
#     want_control_area = False
#     resizing_enabled = True

#     _ewoks_default_inputs = Setting(
#         {
#             "raw_projections_required": True,
#             "raw_projections_each": 90,
#             "raw_darks_required": True,
#             "raw_flats_required": True,
#         }
#     )

#     _ewoks_inputs_to_hide_from_orange = (
#         "__process__",
#         "raw_projections_required",
#         "raw_projections_each",
#         "raw_darks_required",
#         "raw_flats_required",
#     )

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         SuperviseProcess.__init__(self)
#         self._widget = CreateRawDataScreenshotsWidget(parent=self)

#         self._box = gui.vBox(self.mainArea, self.name)
#         layout = self._box.layout()
#         layout.addWidget(self._widget)

#         # load settings
#         self._widget.setConfiguration(self._ewoks_default_inputs)

#         # connect signal / slot
#         self._widget.sigConfigChanged.connect(self._updateSettings)

#     def _updateSettings(self):
#         self._ewoks_default_inputs = self._widget.getConfiguration()

#     def handleNewSignals(self) -> None:
#         """Invoked by the workflow signal propagation manager after all
#         signals handlers have been called.
#         """
#         # for now we want to avoid propagation any processing.
#         # task will be executed only when the user validates the dialog
#         if self.get_task_input_value("data", None) is None:
#             return
#         else:
#             super().handleNewSignals()

#     def get_task_inputs(self):
#         task_inputs = super().get_task_inputs()
#         configuration = self._widget.getConfiguration()
#         task_inputs["raw_projections_required"] = configuration[
#             "raw_projections_required"
#         ]
#         task_inputs["raw_projections_each"] = configuration["raw_projections_each"]
#         task_inputs["raw_darks_required"] = configuration["raw_darks_required"]
#         task_inputs["raw_flats_required"] = configuration["raw_flats_required"]
#         task_inputs["__process__"] = weakref.ref(self)
#         return task_inputs

#     def sizeHint(self):
#         return qt.QSize(500, 200)
