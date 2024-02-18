# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2017 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/

__authors__ = ["C. Nemoz", "H. Payno"]
__license__ = "MIT"
__date__ = "23/03/2021"


from silx.gui import qt
from functools import partial

from tomwer.gui import icons as tomwer_icons
from tomwer.gui.control.tomoobjdisplaymode import DisplayMode


class NXTomomillParamsAction(qt.QAction):
    """
    Action to display a window with nxtomomill configuration
    """

    def __init__(self, parent):
        icon = tomwer_icons.getQIcon("parameters")

        qt.QAction.__init__(self, icon, "filter configuration", parent)
        self.setToolTip("Open dialog to configure nxtomomill parameters")
        self.setCheckable(False)


class CFGFileActiveLabel(qt.QLabel):
    """Label used to display if the .cfg file is active or not"""

    def __init__(self, parent):
        super().__init__(parent)
        icon = tomwer_icons.getQIcon("cfg_file_inactive")
        self.setToolTip("no valid cfg file provided")
        self.setPixmap(icon.pixmap(self.width(), self.height()))

    def setActive(self, active=True):
        if active is True:
            icon = tomwer_icons.getQIcon("cfg_file_active")
            tooltip = "will use the provided .cfg file"
        else:
            icon = tomwer_icons.getQIcon("cfg_file_inactive")
            tooltip = "will use default configuration"

        self.setPixmap(icon.pixmap(self.width(), self.height()))
        self.setToolTip(tooltip)

    def setInactive(self):
        self.setActive(active=False)


class TomoObjDisplayModeToolButton(qt.QToolButton):
    """
    Button to change the way tomo object are displayed.
    Either using the full url or only a 'short' description.
    """

    sigDisplayModeChanged = qt.Signal(str)

    _SHORT_DESC_TOOLTIP = "Use a short description of the tomo object. Two different scans can have the same short desciption"
    _URL_TOOLTIP = (
        "Use the full url to display the tomo object. Url is guaranted to be unique."
    )

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self._shortDescIcon = tomwer_icons.getQIcon("short_description")
        shortDescAction = qt.QAction(self._shortDescIcon, "short description", self)
        shortDescAction.setToolTip(self._SHORT_DESC_TOOLTIP)

        self._urlIcon = tomwer_icons.getQIcon("url")
        urlDescAction = qt.QAction(self._urlIcon, "url", self)
        urlDescAction.setToolTip(self._URL_TOOLTIP)

        menu = qt.QMenu(self)
        menu.addAction(shortDescAction)
        menu.addAction(urlDescAction)
        self.setMenu(menu)
        self.setPopupMode(qt.QToolButton.InstantPopup)

        # set up
        self.setDisplayMode(DisplayMode.SHORT)

        # connect signal / slot
        shortDescAction.triggered.connect(
            partial(self.setDisplayMode, DisplayMode.SHORT)
        )
        urlDescAction.triggered.connect(partial(self.setDisplayMode, DisplayMode.URL))

    def setDisplayMode(self, mode: DisplayMode):
        mode = DisplayMode.from_value(mode)
        if mode is DisplayMode.SHORT:
            self.setIcon(self._shortDescIcon)
            self.setToolTip(self._SHORT_DESC_TOOLTIP)
        elif mode is DisplayMode.URL:
            self.setIcon(self._urlIcon)
            self.setToolTip(self._URL_TOOLTIP)
        else:
            raise ValueError(f"display mode {mode} not handled")
        self.sigDisplayModeChanged.emit(mode.value)
