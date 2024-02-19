# -*- coding: utf-8 -*-

# Copyright (c) 2018 - 2024 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to enter the data of a virtual environment.
"""

import os

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import QDialog, QDialogButtonBox

from eric7.EricWidgets.EricPathPicker import EricPathPickerModes
from eric7.SystemUtilities import OSUtilities, PythonUtilities

from .Ui_VirtualenvAddEditDialog import Ui_VirtualenvAddEditDialog
from .VirtualenvMeta import VirtualenvMetaData


class VirtualenvAddEditDialog(QDialog, Ui_VirtualenvAddEditDialog):
    """
    Class implementing a dialog to enter the data of a virtual environment.
    """

    def __init__(
        self,
        manager,
        metadata=None,
        baseDir="",
        parent=None,
    ):
        """
        Constructor

        @param manager reference to the virtual environment manager
        @type VirtualenvManager
        @param metadata object containing the metadata of the virtual environment
            (defaults to None)
        @type VirtualenvMetaData (optional)
        @param baseDir base directory for the virtual environments (defaults to "")
        @type str (optional)
        @param parent reference to the parent widget (defaults to None)
        @type QWidget (optional)
        """
        super().__init__(parent)
        self.setupUi(self)

        self.__venvName = "" if metadata is None else metadata.name
        self.__manager = manager
        self.__editMode = bool(self.__venvName)

        if self.__editMode:
            self.setWindowTitle(self.tr("Edit Virtual Environment"))
        else:
            self.setWindowTitle(self.tr("Add Virtual Environment"))

        self.__envBaseDir = baseDir
        if not self.__envBaseDir:
            self.__envBaseDir = OSUtilities.getHomeDir()

        self.targetDirectoryPicker.setMode(EricPathPickerModes.DIRECTORY_MODE)
        self.targetDirectoryPicker.setWindowTitle(
            self.tr("Virtualenv Target Directory")
        )
        self.targetDirectoryPicker.setDefaultDirectory(self.__envBaseDir)

        self.pythonExecPicker.setMode(EricPathPickerModes.OPEN_FILE_MODE)
        self.pythonExecPicker.setWindowTitle(self.tr("Python Interpreter"))
        self.pythonExecPicker.setDefaultDirectory(PythonUtilities.getPythonExecutable())

        self.execPathEdit.setToolTip(
            self.tr(
                "Enter the executable search path to be prepended to the PATH"
                " environment variable. Use '{0}' as the separator."
            ).format(os.pathsep)
        )

        self.nameEdit.setText(self.__venvName)
        if metadata:
            if metadata.path:
                self.targetDirectoryPicker.setText(
                    metadata.path, toNative=not metadata.is_remote
                )
            else:
                self.targetDirectoryPicker.setText(
                    self.__envBaseDir, toNative=not metadata.is_remote
                )
            if not metadata.interpreter and metadata.path and not metadata.is_remote:
                py = self.__detectPythonInterpreter(metadata.path)
                self.pythonExecPicker.setText(py)
            else:
                self.pythonExecPicker.setText(
                    metadata.interpreter, toNative=not metadata.is_remote
                )
        else:
            self.targetDirectoryPicker.setText(self.__envBaseDir, toNative=True)

        self.globalCheckBox.setChecked(metadata.is_global if metadata else False)
        self.anacondaCheckBox.setChecked(metadata.is_conda if metadata else False)
        self.remoteCheckBox.setChecked(metadata.is_remote if metadata else False)
        self.execPathEdit.setText(metadata.exec_path if metadata else "")
        self.descriptionEdit.setPlainText(metadata.description if metadata else "")

        self.__updateOk()

        self.nameEdit.setFocus(Qt.FocusReason.OtherFocusReason)

    def __updateOk(self):
        """
        Private slot to update the state of the OK button.
        """
        enable = (
            (
                bool(self.nameEdit.text())
                and (
                    self.nameEdit.text() == self.__venvName
                    or self.__manager.isUnique(self.nameEdit.text())
                )
            )
            if self.__editMode
            else (
                bool(self.nameEdit.text())
                and self.__manager.isUnique(self.nameEdit.text())
            )
        )

        if not self.globalCheckBox.isChecked():
            enable &= self.remoteCheckBox.isChecked() or (
                bool(self.targetDirectoryPicker.text())
                and self.targetDirectoryPicker.text() != self.__envBaseDir
                and os.path.exists(self.targetDirectoryPicker.text())
            )

        enable = (
            enable
            and bool(self.pythonExecPicker.text())
            and (
                self.remoteCheckBox.isChecked()
                or os.access(self.pythonExecPicker.text(), os.X_OK)
            )
        )

        self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(enable)

    def __detectPythonInterpreter(self, venvDirectory):
        """
        Private method to search for a suitable Python interpreter inside an
        environment.

        @param venvDirectory directory for the virtual environment
        @type str
        @return detected Python interpreter or empty string
        @rtype str
        """
        if venvDirectory:
            # try to determine a Python interpreter name
            if OSUtilities.isWindowsPlatform():
                candidates = (
                    os.path.join(venvDirectory, "Scripts", "python.exe"),
                    os.path.join(venvDirectory, "python.exe"),
                )
            else:
                candidates = (os.path.join(venvDirectory, "bin", "python3"),)
            for py in candidates:
                if os.path.exists(py):
                    return py

        return ""

    @pyqtSlot(str)
    def on_nameEdit_textChanged(self, txt):
        """
        Private slot to handle changes of the logical name.

        @param txt current logical name
        @type str
        """
        self.__updateOk()

    @pyqtSlot(str)
    def on_targetDirectoryPicker_textChanged(self, txt):
        """
        Private slot to handle changes of the virtual environment directory.

        @param txt virtual environment directory
        @type str
        """
        self.__updateOk()

        if txt:
            self.pythonExecPicker.setDefaultDirectory(txt)
        else:
            self.pythonExecPicker.setDefaultDirectory(
                PythonUtilities.getPythonExecutable()
            )
        py = self.__detectPythonInterpreter(txt)
        if py:
            self.pythonExecPicker.setText(py)

    @pyqtSlot(str)
    def on_pythonExecPicker_textChanged(self, txt):
        """
        Private slot to handle changes of the virtual environment interpreter.

        @param txt virtual environment interpreter
        @type str
        """
        self.__updateOk()

    @pyqtSlot(bool)
    def on_globalCheckBox_toggled(self, checked):
        """
        Private slot handling a change of the global check box state.

        @param checked state of the check box
        @type bool
        """
        self.__updateOk()

    @pyqtSlot(bool)
    def on_remoteCheckBox_toggled(self, checked):
        """
        Private slot handling a change of the remote check box state.

        @param checked state of the check box
        @type bool
        """
        self.__updateOk()

    @pyqtSlot(bool)
    def on_anacondaCheckBox_clicked(self, checked):
        """
        Private slot handling a user click on this check box.

        @param checked state of the check box
        @type bool
        """
        if checked and not bool(self.execPathEdit.text()):
            # prepopulate the execPathEdit widget
            if OSUtilities.isWindowsPlatform():
                self.execPathEdit.setText(
                    os.pathsep.join(
                        [
                            self.targetDirectoryPicker.text(),
                            os.path.join(self.targetDirectoryPicker.text(), "Scripts"),
                            os.path.join(
                                self.targetDirectoryPicker.text(), "Library", "bin"
                            ),
                        ]
                    )
                )
            else:
                self.execPathEdit.setText(
                    os.path.join(self.targetDirectoryPicker.text(), "bin"),
                )

    def getMetaData(self):
        """
        Public method to retrieve the entered metadata.

        @return metadata for the virtual environment
        @rtype VirtualenvMetaData
        """
        nativePaths = not self.remoteCheckBox.isChecked()
        return VirtualenvMetaData(
            name=self.nameEdit.text(),
            path=self.targetDirectoryPicker.text(toNative=nativePaths),
            interpreter=self.pythonExecPicker.text(toNative=nativePaths),
            is_global=self.globalCheckBox.isChecked(),
            is_conda=self.anacondaCheckBox.isChecked(),
            is_remote=self.remoteCheckBox.isChecked(),
            exec_path=self.execPathEdit.text(),
            description=self.descriptionEdit.toPlainText(),
        )
