# -*- coding: utf-8 -*-

# Copyright (c) 2005 - 2024 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog for entering project specific debugger settings.
"""

import os

from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QComboBox, QDialog

from eric7 import Preferences
from eric7.EricGui import EricPixmapCache
from eric7.EricWidgets.EricApplication import ericApp
from eric7.EricWidgets.EricCompleters import EricDirCompleter
from eric7.EricWidgets.EricPathPicker import EricPathPickerModes
from eric7.Globals import getConfig

from .Ui_DebuggerPropertiesDialog import Ui_DebuggerPropertiesDialog


class DebuggerPropertiesDialog(QDialog, Ui_DebuggerPropertiesDialog):
    """
    Class implementing a dialog for entering project specific debugger
    settings.
    """

    def __init__(self, project, parent=None, name=None):
        """
        Constructor

        @param project reference to the project object
        @type Project
        @param parent parent widget of this dialog
        @type QWidget
        @param name name of this dialog
        @type str
        """
        super().__init__(parent)
        if name:
            self.setObjectName(name)
        self.setupUi(self)

        self.project = project

        debugClientsHistory = Preferences.getProject("DebugClientsHistory")
        self.debugClientPicker.setMode(EricPathPickerModes.OPEN_FILE_MODE)
        self.debugClientPicker.setInsertPolicy(QComboBox.InsertPolicy.InsertAtTop)
        self.debugClientPicker.setSizeAdjustPolicy(
            QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon
        )
        self.debugClientPicker.setPathsList(debugClientsHistory)
        self.debugClientClearHistoryButton.setIcon(
            EricPixmapCache.getIcon("editDelete")
        )

        self.translationLocalCompleter = EricDirCompleter(self.translationLocalEdit)

        venvManager = ericApp().getObject("VirtualEnvManager")

        self.venvGroupBox.setVisible(
            not self.project.getProjectData(dataKey="EMBEDDED_VENV")
        )
        self.venvComboBox.addItem("")
        if self.project.getProjectData(dataKey="EMBEDDED_VENV"):
            venvIndex = 0
        else:
            self.venvComboBox.addItems(sorted(venvManager.getVirtualenvNames()))

            if self.project.debugProperties["VIRTUALENV"]:
                venvIndex = max(
                    0,
                    self.venvComboBox.findText(
                        self.project.debugProperties["VIRTUALENV"]
                    ),
                )
            else:
                if self.project.getProjectData(dataKey="PROGLANGUAGE") == "Python3":
                    venvName = Preferences.getDebugger("Python3VirtualEnv")
                else:
                    venvName = ""
                if not venvName:
                    venvName, _ = venvManager.getDefaultEnvironment()
                if venvName:
                    venvIndex = max(0, self.venvComboBox.findText(venvName))
                else:
                    venvIndex = 0
        self.venvComboBox.setCurrentIndex(venvIndex)
        if self.project.debugProperties["DEBUGCLIENT"]:
            self.debugClientPicker.setText(
                self.project.debugProperties["DEBUGCLIENT"], toNative=False
            )
        else:
            if self.project.getProjectData(dataKey="PROGLANGUAGE") == "Python3":
                debugClient = os.path.join(
                    getConfig("ericDir"), "DebugClients", "Python", "DebugClient.py"
                )
            else:
                debugClient = ""
            self.debugClientPicker.setText(debugClient, toNative=False)
        self.debugEnvironmentOverrideCheckBox.setChecked(
            self.project.debugProperties["ENVIRONMENTOVERRIDE"]
        )
        self.debugEnvironmentEdit.setText(
            self.project.debugProperties["ENVIRONMENTSTRING"]
        )
        self.remoteDebuggerGroup.setChecked(
            self.project.debugProperties["REMOTEDEBUGGER"]
        )
        self.remoteHostEdit.setText(self.project.debugProperties["REMOTEHOST"])
        self.remoteCommandEdit.setText(self.project.debugProperties["REMOTECOMMAND"])
        self.remoteDebugClientEdit.setText(
            self.project.debugProperties["REMOTEDEBUGCLIENT"]
        )
        self.pathTranslationGroup.setChecked(
            self.project.debugProperties["PATHTRANSLATION"]
        )
        self.translationRemoteEdit.setText(self.project.debugProperties["REMOTEPATH"])
        self.translationLocalEdit.setText(self.project.debugProperties["LOCALPATH"])
        self.consoleDebuggerGroup.setChecked(
            self.project.debugProperties["CONSOLEDEBUGGER"]
        )
        self.consoleCommandEdit.setText(self.project.debugProperties["CONSOLECOMMAND"])
        self.redirectCheckBox.setChecked(self.project.debugProperties["REDIRECT"])
        self.noEncodingCheckBox.setChecked(self.project.debugProperties["NOENCODING"])

        msh = self.minimumSizeHint()
        self.resize(max(self.width(), msh.width()), msh.height())

    @pyqtSlot()
    def on_debugClientPicker_aboutToShowPathPickerDialog(self):
        """
        Private slot to perform actions before the debug client selection
        dialog is shown.
        """
        filters = self.project.getDebuggerFilters(
            self.project.getProjectData(dataKey="PROGLANGUAGE")
        )
        filters += self.tr("All Files (*)")
        self.debugClientPicker.setFilters(filters)

    def storeData(self):
        """
        Public method to store the entered/modified data.
        """
        self.project.debugProperties["VIRTUALENV"] = self.venvComboBox.currentText()

        self.project.debugProperties["DEBUGCLIENT"] = self.debugClientPicker.text(
            toNative=False
        )
        if not self.project.debugProperties["DEBUGCLIENT"]:
            if self.project.getProjectData(dataKey="PROGLANGUAGE") == "Python3":
                debugClient = os.path.join(
                    getConfig("ericDir"), "DebugClients", "Python", "DebugClient.py"
                )
            else:
                debugClient = ""
            self.project.debugProperties["DEBUGCLIENT"] = debugClient

        self.project.debugProperties[
            "ENVIRONMENTOVERRIDE"
        ] = self.debugEnvironmentOverrideCheckBox.isChecked()
        self.project.debugProperties[
            "ENVIRONMENTSTRING"
        ] = self.debugEnvironmentEdit.text()
        self.project.debugProperties[
            "REMOTEDEBUGGER"
        ] = self.remoteDebuggerGroup.isChecked()
        self.project.debugProperties["REMOTEHOST"] = self.remoteHostEdit.text()
        self.project.debugProperties["REMOTECOMMAND"] = self.remoteCommandEdit.text()
        self.project.debugProperties[
            "REMOTEDEBUGCLIENT"
        ] = self.remoteDebugClientEdit.text()
        self.project.debugProperties[
            "PATHTRANSLATION"
        ] = self.pathTranslationGroup.isChecked()
        self.project.debugProperties["REMOTEPATH"] = self.translationRemoteEdit.text()
        self.project.debugProperties["LOCALPATH"] = self.translationLocalEdit.text()
        self.project.debugProperties[
            "CONSOLEDEBUGGER"
        ] = self.consoleDebuggerGroup.isChecked()
        self.project.debugProperties["CONSOLECOMMAND"] = self.consoleCommandEdit.text()
        self.project.debugProperties["REDIRECT"] = self.redirectCheckBox.isChecked()
        self.project.debugProperties["NOENCODING"] = self.noEncodingCheckBox.isChecked()
        self.project.debugPropertiesLoaded = True
        self.project.debugPropertiesChanged = True

        self.__saveHistories()

    def __saveHistories(self):
        """
        Private method to save the path picker histories.
        """
        debugClient = self.debugClientPicker.text(toNative=False)
        debugClientsHistory = self.debugClientPicker.getPathItems()
        if debugClient not in debugClientsHistory:
            debugClientsHistory.insert(0, debugClient)
        Preferences.setProject("DebugClientsHistory", debugClientsHistory)

    @pyqtSlot()
    def on_debugClientClearHistoryButton_clicked(self):
        """
        Private slot to clear the debug clients history.
        """
        self.__clearHistory(self.debugClientPicker)

    def __clearHistory(self, picker):
        """
        Private method to clear a path picker history.

        @param picker reference to the path picker
        @type EricComboPathPicker
        """
        currentText = picker.text()
        picker.clear()
        picker.setText(currentText)

        self.__saveHistories()
