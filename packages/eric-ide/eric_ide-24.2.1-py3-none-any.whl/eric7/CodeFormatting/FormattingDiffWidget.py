# -*- coding: utf-8 -*-

# Copyright (c) 2022 - 2024 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a window to show a unified diff..
"""

from PyQt6.QtWidgets import QWidget

from eric7 import Preferences
from eric7.UI.DiffHighlighter import DiffHighlighter

from .Ui_FormattingDiffWidget import Ui_FormattingDiffWidget


class FormattingDiffWidget(QWidget, Ui_FormattingDiffWidget):
    """
    Class implementing a window to show a unified diff..
    """

    def __init__(self, parent=None):
        """
        Constructor

        @param parent reference to the parent widget (defaults to None)
        @type QWidget (optional)
        """
        super().__init__(parent)
        self.setupUi(self)

        font = Preferences.getEditorOtherFonts("MonospacedFont")
        self.diffEdit.document().setDefaultFont(font)

        self.__highlighter = DiffHighlighter(self.diffEdit.document())
        self.__savedGeometry = None

    def showDiff(self, diff):
        """
        Public method to show the given diff.

        @param diff text containing the unified diff
        @type str
        """
        self.diffEdit.clear()
        self.__highlighter.regenerateRules()

        if diff:
            self.diffEdit.setPlainText(diff)
        else:
            self.diffEdit.setPlainText(self.tr("There is no difference."))

        if self.__savedGeometry is not None:
            self.restoreGeometry(self.__savedGeometry)

        if not self.isVisible():
            self.show()
        self.activateWindow()
        self.raise_()

    def closeEvent(self, evt):  # noqa: U100
        """
        Protected slot implementing a close event handler.

        @param evt reference to the close event
        @type QCloseEvent
        """
        self.__savedGeometry = self.saveGeometry()
