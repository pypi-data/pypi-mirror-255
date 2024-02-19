# -*- coding: utf-8 -*-

# Copyright (c) 2002 - 2024 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the project properties dialog.
"""

import contextlib
import os

import trove_classifiers

from PyQt6.QtCore import QDir, pyqtSlot
from PyQt6.QtWidgets import QDialog, QDialogButtonBox

from eric7 import Preferences
from eric7.EricGui import EricPixmapCache
from eric7.EricWidgets.EricApplication import ericApp
from eric7.EricWidgets.EricPathPicker import EricPathPickerModes
from eric7.QScintilla.DocstringGenerator import getSupportedDocstringTypes
from eric7.SystemUtilities import FileSystemUtilities, OSUtilities
from eric7.Testing.Interfaces import FrameworkNames

from .Ui_PropertiesDialog import Ui_PropertiesDialog


class PropertiesDialog(QDialog, Ui_PropertiesDialog):
    """
    Class implementing the project properties dialog.
    """

    def __init__(self, project, new=True, parent=None, name=None):
        """
        Constructor

        @param project reference to the project object
        @type Project
        @param new flag indicating the generation of a new project
            (defaults to True)
        @type bool (optional)
        @param parent parent widget of this dialog (defaults to None)
        @type QWidget (optional)
        @param name name of this dialog (defaults to None)
        @type str (optional)
        """
        super().__init__(parent)
        if name:
            self.setObjectName(name)
        self.setupUi(self)

        self.dirPicker.setMode(EricPathPickerModes.DIRECTORY_MODE)
        self.srcDirPicker.setMode(EricPathPickerModes.DIRECTORY_MODE)
        self.mainscriptPicker.setMode(EricPathPickerModes.OPEN_FILE_MODE)

        self.makeButton.setIcon(EricPixmapCache.getIcon("makefile"))

        self.docstringStyleComboBox.addItem(self.tr("None"), "")
        for docstringType, docstringStyle in sorted(getSupportedDocstringTypes()):
            self.docstringStyleComboBox.addItem(docstringStyle, docstringType)

        self.project = project
        self.newProject = new
        self.transPropertiesDlg = None
        self.spellPropertiesDlg = None
        self.makePropertiesDlg = None
        self.__fileTypesDict = {}

        patterns = []
        for pattern, filetype in self.project.getProjectData(
            dataKey="FILETYPES"
        ).items():
            if filetype == "SOURCES":
                patterns.append(pattern)
        filters = self.tr("Source Files ({0});;All Files (*)").format(
            " ".join(sorted(patterns))
        )
        self.mainscriptPicker.setFilters(filters)

        self.languageComboBox.addItems(project.getProgrammingLanguages())

        projectTypes = []
        for projectTypeItem in project.getProjectTypes().items():
            projectTypes.append((projectTypeItem[1], projectTypeItem[0]))
        self.projectTypeComboBox.clear()
        for projectType in sorted(projectTypes):
            self.projectTypeComboBox.addItem(projectType[0], projectType[1])

        ipath = Preferences.getMultiProject("Workspace") or OSUtilities.getHomeDir()
        self.__initPaths = [
            FileSystemUtilities.fromNativeSeparators(ipath),
            FileSystemUtilities.fromNativeSeparators(ipath) + "/",
        ]

        self.licenseComboBox.lineEdit().setClearButtonEnabled(True)
        self.__populateLicenseComboBox()

        if not new:
            name = os.path.splitext(self.project.pfile)[0]
            self.nameEdit.setText(os.path.basename(name))
            self.languageComboBox.setCurrentIndex(
                self.languageComboBox.findText(
                    self.project.getProjectData(dataKey="PROGLANGUAGE")
                )
            )
            self.mixedLanguageCheckBox.setChecked(
                self.project.getProjectData(dataKey="MIXEDLANGUAGE")
            )
            curIndex = self.projectTypeComboBox.findData(
                self.project.getProjectData(dataKey="PROJECTTYPE")
            )
            if curIndex == -1:
                curIndex = self.projectTypeComboBox.findData("PyQt6")
            self.projectTypeComboBox.setCurrentIndex(curIndex)
            self.dirPicker.setText(self.project.ppath)
            self.srcDirPicker.setText(self.project.getProjectData(dataKey="SOURCESDIR"))
            self.versionEdit.setText(self.project.getProjectData(dataKey="VERSION"))
            self.mainscriptPicker.setText(
                self.project.getProjectData(dataKey="MAINSCRIPT")
            )
            self.authorEdit.setText(self.project.getProjectData(dataKey="AUTHOR"))
            self.emailEdit.setText(self.project.getProjectData(dataKey="EMAIL"))
            self.descriptionEdit.setPlainText(
                self.project.getProjectData(dataKey="DESCRIPTION")
            )
            self.eolComboBox.setCurrentIndex(self.project.getProjectData(dataKey="EOL"))
            self.vcsLabel.show()
            if self.project.vcs is not None:
                vcsSystemsDict = (
                    ericApp()
                    .getObject("PluginManager")
                    .getPluginDisplayStrings("version_control")
                )
                try:
                    vcsSystemDisplay = vcsSystemsDict[
                        self.project.getProjectData(dataKey="VCS")
                    ]
                except KeyError:
                    vcsSystemDisplay = "None"
                self.vcsLabel.setText(
                    self.tr("The project is version controlled by <b>{0}</b>.").format(
                        vcsSystemDisplay
                    )
                )
                self.vcsInfoButton.show()
            else:
                self.vcsLabel.setText(self.tr("The project is not version controlled."))
                self.vcsInfoButton.hide()
            self.vcsCheckBox.hide()
            self.makeCheckBox.setChecked(
                self.project.getProjectData(dataKey="MAKEPARAMS")["MakeEnabled"]
            )
            cindex = self.docstringStyleComboBox.findData(
                self.project.getProjectData(dataKey="DOCSTRING")
            )
            self.docstringStyleComboBox.setCurrentIndex(cindex)
            with contextlib.suppress(KeyError):
                cindex = self.testingFrameworkComboBox.findData(
                    self.project.getProjectData(dataKey="TESTING_FRAMEWORK")
                )
                self.testingFrameworkComboBox.setCurrentIndex(cindex)
            with contextlib.suppress(KeyError):
                self.licenseComboBox.setCurrentText(
                    self.project.getProjectData(dataKey="LICENSE")
                )
            self.embeddedVenvCheckBox.setChecked(
                self.project.getProjectData(dataKey="EMBEDDED_VENV")
            )
        else:
            self.languageComboBox.setCurrentText("Python3")
            self.projectTypeComboBox.setCurrentIndex(
                self.projectTypeComboBox.findData("PyQt6")
            )
            self.dirPicker.setText(self.__initPaths[0])
            self.versionEdit.setText("0.1")
            self.vcsLabel.hide()
            self.vcsInfoButton.hide()
            if not self.project.vcsSoftwareAvailable():
                self.vcsCheckBox.hide()

        self.__origProgrammingLanguage = self.languageComboBox.currentText()
        self.__origMixedFlag = self.mixedLanguageCheckBox.isChecked()
        self.__origProjectType = self.getProjectType()

        self.languageComboBox.currentTextChanged.connect(self.__initFileTypesDict)
        self.mixedLanguageCheckBox.stateChanged.connect(self.__initFileTypesDict)
        self.projectTypeComboBox.currentIndexChanged.connect(self.__initFileTypesDict)

        self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(
            bool(self.dirPicker.text())
            and self.dirPicker.text() not in self.__initPaths
        )

    def __populateLicenseComboBox(self):
        """
        Private method to populate the license selector with the list of trove
        license types.
        """
        self.licenseComboBox.addItem("")
        self.licenseComboBox.addItems(
            sorted(
                classifier.split("::")[-1].strip()
                for classifier in trove_classifiers.classifiers
                if classifier.startswith("License ::")
            )
        )

    @pyqtSlot(str)
    def on_languageComboBox_currentTextChanged(self, language):
        """
        Private slot handling the selection of a programming language.

        @param language text of the current item
        @type str
        """
        curProjectType = self.getProjectType()

        self.projectTypeComboBox.clear()
        for projectType in sorted(
            self.project.getProjectTypes(language).items(), key=lambda k: k[1]
        ):
            self.projectTypeComboBox.addItem(projectType[1], projectType[0])

        index = self.projectTypeComboBox.findData(curProjectType)
        if index == -1:
            index = 0
        self.projectTypeComboBox.setCurrentIndex(index)

        curTestingFramework = self.testingFrameworkComboBox.currentText()
        self.testingFrameworkComboBox.clear()
        self.testingFrameworkComboBox.addItem(self.tr("None"), "")
        with contextlib.suppress(KeyError):
            for framework in sorted(FrameworkNames[language]):
                self.testingFrameworkComboBox.addItem(framework, framework)
        self.testingFrameworkComboBox.setCurrentText(curTestingFramework)

    @pyqtSlot(str)
    def on_dirPicker_textChanged(self, txt):
        """
        Private slot to handle a change of the project directory.

        @param txt name of the project directory
        @type str
        """
        self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(
            bool(txt)
            and FileSystemUtilities.fromNativeSeparators(txt) not in self.__initPaths
        )

    @pyqtSlot(str)
    def on_srcDirPicker_pathSelected(self, srcDir):
        """
        Private slot to check the selected sources sub-directory name.

        @param srcDir name of the sources directory name
        @type str
        """
        if srcDir:
            ppath = self.dirPicker.text()
            if ppath:
                ppath = QDir(ppath).absolutePath() + QDir.separator()
                srcDir = srcDir.replace(ppath, "")
            self.srcDirPicker.setText(srcDir)

    @pyqtSlot()
    def on_srcDirPicker_aboutToShowPathPickerDialog(self):
        """
        Private slot to perform actions before the sources sub-directory selection
        dialog is shown.
        """
        ppath = self.dirPicker.text()
        if not ppath:
            ppath = QDir.currentPath()
        self.srcDirPicker.setDefaultDirectory(ppath)

    @pyqtSlot()
    def on_spellPropertiesButton_clicked(self):
        """
        Private slot to display the spelling properties dialog.
        """
        from .SpellingPropertiesDialog import SpellingPropertiesDialog

        if self.spellPropertiesDlg is None:
            self.spellPropertiesDlg = SpellingPropertiesDialog(
                self.project, self.newProject, self
            )
        res = self.spellPropertiesDlg.exec()
        if res == QDialog.DialogCode.Rejected:
            self.spellPropertiesDlg.initDialog()  # reset the dialogs contents

    @pyqtSlot()
    def on_transPropertiesButton_clicked(self):
        """
        Private slot to display the translations properties dialog.
        """
        from .TranslationPropertiesDialog import TranslationPropertiesDialog

        if self.transPropertiesDlg is None:
            self.transPropertiesDlg = TranslationPropertiesDialog(
                self.project, self.newProject, self
            )
        else:
            self.transPropertiesDlg.initFilters()
        res = self.transPropertiesDlg.exec()
        if res == QDialog.DialogCode.Rejected:
            self.transPropertiesDlg.initDialog()  # reset the dialogs contents

    @pyqtSlot()
    def on_makeButton_clicked(self):
        """
        Private slot to display the make properties dialog.
        """
        from .MakePropertiesDialog import MakePropertiesDialog

        if self.makePropertiesDlg is None:
            self.makePropertiesDlg = MakePropertiesDialog(
                self.project, self.newProject, self
            )
        res = self.makePropertiesDlg.exec()
        if res == QDialog.DialogCode.Rejected:
            self.makePropertiesDlg.initDialog()

    @pyqtSlot(str)
    def on_mainscriptPicker_pathSelected(self, script):
        """
        Private slot to check the selected main script name.

        @param script name of the main script
        @type str
        """
        if script:
            ppath = self.dirPicker.text()
            if ppath:
                ppath = QDir(ppath).absolutePath() + QDir.separator()
                script = script.replace(ppath, "")
            self.mainscriptPicker.setText(script)

    @pyqtSlot()
    def on_mainscriptPicker_aboutToShowPathPickerDialog(self):
        """
        Private slot to perform actions before the main script selection dialog
        is shown.
        """
        ppath = self.dirPicker.text()
        if not ppath:
            ppath = QDir.currentPath()
        self.mainscriptPicker.setDefaultDirectory(ppath)

    @pyqtSlot()
    def on_vcsInfoButton_clicked(self):
        """
        Private slot to display a vcs information dialog.
        """
        from eric7.VCS.RepositoryInfoDialog import VcsRepositoryInfoDialog

        if self.project.vcs is None:
            return

        info = self.project.vcs.vcsRepositoryInfos(self.project.ppath)
        dlg = VcsRepositoryInfoDialog(self, info)
        dlg.exec()

    def getProjectType(self):
        """
        Public method to get the selected project type.

        @return selected UI type
        @rtype str
        """
        return self.projectTypeComboBox.itemData(
            self.projectTypeComboBox.currentIndex()
        )

    def getPPath(self):
        """
        Public method to get the project path.

        @return data of the project directory edit
        @rtype str
        """
        return os.path.abspath(self.dirPicker.text())

    @pyqtSlot()
    def __initFileTypesDict(self):
        """
        Private slot to (re-)initialize the filetype dictionary.
        """
        if (
            self.__origProgrammingLanguage != self.languageComboBox.currentText()
            or self.__origMixedFlag != self.mixedLanguageCheckBox.isChecked()
            or self.__origProjectType != self.getProjectType()
        ):
            # any of the defining data got changed
            self.__fileTypesDict = self.project.defaultFileTypes(
                self.languageComboBox.currentText(),
                self.mixedLanguageCheckBox.isChecked(),
                self.getProjectType(),
            )
        else:
            # all of the defining data was changed back to original
            self.__fileTypesDict = self.project.getProjectData(dataKey="FILETYPES")

    @pyqtSlot()
    def on_filetypesButton_clicked(self):
        """
        Private slot to open a dialog to edit the filetype associations.
        """
        from .FiletypeAssociationDialog import FiletypeAssociationDialog

        if not self.__fileTypesDict:
            self.__fileTypesDict = self.project.getProjectData(dataKey="FILETYPES")
            if (
                not self.__fileTypesDict
                or self.__origProgrammingLanguage != self.languageComboBox.currentText()
                or self.__origMixedFlag != self.mixedLanguageCheckBox.isChecked()
                or self.__origProjectType != self.getProjectType()
            ):
                # the associations were not defined yet or any of the defining data got
                # changed
                self.__fileTypesDict = self.project.defaultFileTypes(
                    self.languageComboBox.currentText(),
                    self.mixedLanguageCheckBox.isChecked(),
                    self.getProjectType(),
                )

        dlg = FiletypeAssociationDialog(self.project, self.__fileTypesDict)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.__fileTypesDict = dlg.getData()

    def storeData(self):
        """
        Public method to store the entered/modified data.
        """
        self.project.ppath = os.path.abspath(self.dirPicker.text())
        fn = self.nameEdit.text()
        if fn:
            self.project.name = fn
            fn = "{0}.epj".format(fn)
            self.project.pfile = os.path.join(self.project.ppath, fn)
        else:
            self.project.pfile = ""
        self.project.setProjectData(self.versionEdit.text(), dataKey="VERSION")
        srcDir = self.srcDirPicker.text()
        if srcDir:
            srcDir = self.project.getRelativePath(srcDir)
            self.project.setProjectData(srcDir, dataKey="SOURCESDIR")
        else:
            self.project.setProjectData("", dataKey="SOURCESDIR")
        fn = self.mainscriptPicker.text()
        if fn:
            fn = self.project.getRelativePath(fn)
            self.project.setProjectData(fn, dataKey="MAINSCRIPT")
            self.project.translationsRoot = os.path.splitext(fn)[0]
        else:
            self.project.setProjectData("", dataKey="MAINSCRIPT")
            self.project.translationsRoot = ""
        self.project.setProjectData(self.authorEdit.text(), dataKey="AUTHOR")
        self.project.setProjectData(self.emailEdit.text(), dataKey="EMAIL")
        self.project.setProjectData(
            self.descriptionEdit.toPlainText(), dataKey="DESCRIPTION"
        )
        self.project.setProjectData(
            self.languageComboBox.currentText(), dataKey="PROGLANGUAGE"
        )
        self.project.setProjectData(
            self.mixedLanguageCheckBox.isChecked(), dataKey="MIXEDLANGUAGE"
        )
        projectType = self.getProjectType()
        if projectType is not None:
            self.project.setProjectData(projectType, dataKey="PROJECTTYPE")
        self.project.setProjectData(self.eolComboBox.currentIndex(), dataKey="EOL")

        self.project.vcsRequested = self.vcsCheckBox.isChecked()

        if self.spellPropertiesDlg is not None:
            self.spellPropertiesDlg.storeData()

        if self.transPropertiesDlg is not None:
            self.transPropertiesDlg.storeData()

        makeParams = self.project.getProjectData(dataKey="MAKEPARAMS")
        makeParams["MakeEnabled"] = self.makeCheckBox.isChecked()
        self.project.setProjectData(makeParams, dataKey="MAKEPARAMS")
        if self.makePropertiesDlg is not None:
            self.makePropertiesDlg.storeData()

        self.project.setProjectData(
            self.docstringStyleComboBox.currentData(), dataKey="DOCSTRING"
        )

        self.project.setProjectData(
            self.testingFrameworkComboBox.currentData(), dataKey="TESTING_FRAMEWORK"
        )

        self.project.setProjectData(
            self.licenseComboBox.currentText(), dataKey="LICENSE"
        )

        self.project.setProjectData(
            self.embeddedVenvCheckBox.isChecked(), dataKey="EMBEDDED_VENV"
        )

        if self.__fileTypesDict:
            self.project.setProjectData(self.__fileTypesDict, dataKey="FILETYPES")
