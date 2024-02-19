# -*- coding: utf-8 -*-

# Copyright (c) 2007 - 2024 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog showing UML like diagrams.
"""

import enum
import json
import pathlib

from PyQt6.QtCore import QCoreApplication, Qt, pyqtSlot
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QGraphicsScene, QToolBar

from eric7.EricGui import EricPixmapCache
from eric7.EricWidgets import EricFileDialog, EricMessageBox
from eric7.EricWidgets.EricMainWindow import EricMainWindow

from .ApplicationDiagramBuilder import ApplicationDiagramBuilder
from .ImportsDiagramBuilder import ImportsDiagramBuilder
from .PackageDiagramBuilder import PackageDiagramBuilder
from .UMLClassDiagramBuilder import UMLClassDiagramBuilder
from .UMLGraphicsView import UMLGraphicsView


class UMLDialogType(enum.Enum):
    """
    Class defining the UML dialog types.
    """

    CLASS_DIAGRAM = 0
    PACKAGE_DIAGRAM = 1
    IMPORTS_DIAGRAM = 2
    APPLICATION_DIAGRAM = 3
    NO_DIAGRAM = 255


class UMLDialog(EricMainWindow):
    """
    Class implementing a dialog showing UML like diagrams.
    """

    FileVersions = ("1.0",)
    JsonFileVersions = ("1.0",)

    UMLDialogType2String = {
        UMLDialogType.CLASS_DIAGRAM: QCoreApplication.translate(
            "UMLDialog", "Class Diagram"
        ),
        UMLDialogType.PACKAGE_DIAGRAM: QCoreApplication.translate(
            "UMLDialog", "Package Diagram"
        ),
        UMLDialogType.IMPORTS_DIAGRAM: QCoreApplication.translate(
            "UMLDialog", "Imports Diagram"
        ),
        UMLDialogType.APPLICATION_DIAGRAM: QCoreApplication.translate(
            "UMLDialog", "Application Diagram"
        ),
    }

    def __init__(
        self, diagramType, project, path="", parent=None, initBuilder=True, **kwargs
    ):
        """
        Constructor

        @param diagramType type of the diagram
        @type UMLDialogType
        @param project reference to the project object
        @type Project
        @param path file or directory path to build the diagram from
        @type str
        @param parent parent widget of the dialog
        @type QWidget
        @param initBuilder flag indicating to initialize the diagram
            builder
        @type bool
        @keyparam kwargs diagram specific data
        @type dict
        """
        super().__init__(parent)
        self.setObjectName("UMLDialog")

        self.__project = project
        self.__diagramType = diagramType

        self.scene = QGraphicsScene(0.0, 0.0, 800.0, 600.0)
        self.umlView = UMLGraphicsView(self.scene, parent=self)
        self.builder = self.__diagramBuilder(self.__diagramType, path, **kwargs)
        if self.builder and initBuilder:
            self.builder.initialize()

        self.__fileName = ""

        self.__initActions()
        self.__initToolBars()

        self.setCentralWidget(self.umlView)

        self.umlView.relayout.connect(self.__relayout)

        self.setWindowTitle(self.__getDiagramTitel(self.__diagramType))

    def __getDiagramTitel(self, diagramType):
        """
        Private method to get a textual description for the diagram type.

        @param diagramType diagram type string
        @type str
        @return titel of the diagram
        @rtype str
        """
        return UMLDialog.UMLDialogType2String.get(
            diagramType, self.tr("Illegal Diagram Type")
        )

    def __initActions(self):
        """
        Private slot to initialize the actions.
        """
        self.closeAct = QAction(
            EricPixmapCache.getIcon("close"), self.tr("Close"), self
        )
        self.closeAct.triggered.connect(self.close)

        self.openAct = QAction(EricPixmapCache.getIcon("open"), self.tr("Load"), self)
        self.openAct.triggered.connect(self.load)

        self.saveAct = QAction(
            EricPixmapCache.getIcon("fileSave"), self.tr("Save"), self
        )
        self.saveAct.triggered.connect(self.__save)

        self.saveAsAct = QAction(
            EricPixmapCache.getIcon("fileSaveAs"), self.tr("Save As..."), self
        )
        self.saveAsAct.triggered.connect(self.__saveAs)

        self.saveImageAct = QAction(
            EricPixmapCache.getIcon("fileSavePixmap"), self.tr("Save as Image"), self
        )
        self.saveImageAct.triggered.connect(self.umlView.saveImage)

        self.printAct = QAction(
            EricPixmapCache.getIcon("print"), self.tr("Print"), self
        )
        self.printAct.triggered.connect(self.umlView.printDiagram)

        self.printPreviewAct = QAction(
            EricPixmapCache.getIcon("printPreview"), self.tr("Print Preview"), self
        )
        self.printPreviewAct.triggered.connect(self.umlView.printPreviewDiagram)

    def __initToolBars(self):
        """
        Private slot to initialize the toolbars.
        """
        self.windowToolBar = QToolBar(self.tr("Window"), self)
        self.windowToolBar.addAction(self.closeAct)

        self.fileToolBar = QToolBar(self.tr("File"), self)
        self.fileToolBar.addAction(self.openAct)
        self.fileToolBar.addSeparator()
        self.fileToolBar.addAction(self.saveAct)
        self.fileToolBar.addAction(self.saveAsAct)
        self.fileToolBar.addAction(self.saveImageAct)
        self.fileToolBar.addSeparator()
        self.fileToolBar.addAction(self.printPreviewAct)
        self.fileToolBar.addAction(self.printAct)

        self.umlToolBar = self.umlView.initToolBar()

        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.fileToolBar)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.windowToolBar)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.umlToolBar)

    def show(self, fromFile=False):
        """
        Public method to show the dialog.

        @param fromFile flag indicating, that the diagram was loaded
            from file
        @type bool
        """
        if not fromFile and self.builder:
            self.builder.buildDiagram()
        super().show()

    def __relayout(self):
        """
        Private method to re-layout the diagram.
        """
        if self.builder:
            self.builder.buildDiagram()

    def __diagramBuilder(self, diagramType, path, **kwargs):
        """
        Private method to instantiate a diagram builder object.

        @param diagramType type of the diagram
        @type UMLDialogType
        @param path file or directory path to build the diagram from
        @type str
        @keyparam kwargs diagram specific data
        @type dict
        @return reference to the instantiated diagram builder
        @rtype UMLDiagramBuilder
        """
        if diagramType == UMLDialogType.CLASS_DIAGRAM:
            return UMLClassDiagramBuilder(
                self, self.umlView, self.__project, path, **kwargs
            )
        elif diagramType == UMLDialogType.PACKAGE_DIAGRAM:
            return PackageDiagramBuilder(
                self, self.umlView, self.__project, path, **kwargs
            )
        elif diagramType == UMLDialogType.IMPORTS_DIAGRAM:
            return ImportsDiagramBuilder(
                self, self.umlView, self.__project, path, **kwargs
            )
        elif diagramType == UMLDialogType.APPLICATION_DIAGRAM:
            return ApplicationDiagramBuilder(
                self, self.umlView, self.__project, **kwargs
            )
        else:
            return None

    def __save(self):
        """
        Private slot to save the diagram with the current name.
        """
        self.__saveAs(self.__fileName)

    @pyqtSlot()
    def __saveAs(self, filename=""):
        """
        Private slot to save the diagram.

        @param filename name of the file to write to
        @type str
        """
        if not filename:
            fname, selectedFilter = EricFileDialog.getSaveFileNameAndFilter(
                self,
                self.tr("Save Diagram"),
                "",
                self.tr(
                    "Eric Graphics File (*.egj);;"
                    "Eric Text Graphics File (*.e5g);;"
                    "All Files (*)"
                ),
                "",
                EricFileDialog.DontConfirmOverwrite,
            )
            if not fname:
                return

            fpath = pathlib.Path(fname)
            if not fpath.suffix:
                ex = selectedFilter.split("(*")[1].split(")")[0]
                if ex:
                    fpath = fpath.with_suffix(ex)
            if fpath.exists():
                res = EricMessageBox.yesNo(
                    self,
                    self.tr("Save Diagram"),
                    self.tr(
                        "<p>The file <b>{0}</b> already exists. Overwrite it?</p>"
                    ).format(fpath),
                    icon=EricMessageBox.Warning,
                )
                if not res:
                    return
            filename = str(fpath)

        res = self.__writeJsonGraphicsFile(filename)

        if res:
            # save the file name only in case of success
            self.__fileName = filename

    # Note: remove loading of eric6 line based diagram format after 22.6
    def load(self, filename=""):
        """
        Public method to load a diagram from a file.

        @param filename name of the file to be loaded
        @type str
        @return flag indicating success
        @rtype bool
        """
        if not filename:
            filename = EricFileDialog.getOpenFileName(
                self,
                self.tr("Load Diagram"),
                "",
                self.tr(
                    "Eric Graphics File (*.egj);;"
                    "Eric Text Graphics File (*.e5g);;"
                    "All Files (*)"
                ),
            )
            if not filename:
                # Canceled by user
                return False

        return (
            self.__readLineBasedGraphicsFile(filename)
            if filename.endswith(".e5g")
            else
            # JSON format is the default
            self.__readJsonGraphicsFile(filename)
        )

    #######################################################################
    ## Methods to read and write eric graphics files of the old line
    ## based file format.
    #######################################################################

    def __readLineBasedGraphicsFile(self, filename):
        """
        Private method to read an eric graphics file using the old line
        based file format.

        @param filename name of the file to be read
        @type str
        @return flag indicating success
        @rtype bool
        """
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = f.read()
        except OSError as err:
            EricMessageBox.critical(
                self,
                self.tr("Load Diagram"),
                self.tr(
                    """<p>The file <b>{0}</b> could not be read.</p>"""
                    """<p>Reason: {1}</p>"""
                ).format(filename, str(err)),
            )
            return False

        lines = data.splitlines()
        if len(lines) < 3:
            self.__showInvalidDataMessage(filename)
            return False

        try:
            # step 1: check version
            linenum = 0
            key, value = lines[linenum].split(": ", 1)
            if key.strip() != "version" or value.strip() not in UMLDialog.FileVersions:
                self.__showInvalidDataMessage(filename, linenum)
                return False
            else:
                version = value

            # step 2: extract diagram type
            linenum += 1
            key, value = lines[linenum].split(": ", 1)
            if key.strip() != "diagram_type":
                self.__showInvalidDataMessage(filename, linenum)
                return False
            try:
                diagramType = value.strip().split(None, 1)[0]
                self.__diagramType = UMLDialogType(int(diagramType))
            except ValueError:
                self.__showInvalidDataMessage(filename, linenum)
                return False
            self.scene.clear()
            self.builder = self.__diagramBuilder(self.__diagramType, "")

            # step 3: extract scene size
            linenum += 1
            key, value = lines[linenum].split(": ", 1)
            if key.strip() != "scene_size":
                self.__showInvalidDataMessage(filename, linenum)
                return False
            try:
                width, height = [float(v.strip()) for v in value.split(";")]
            except ValueError:
                self.__showInvalidDataMessage(filename, linenum)
                return False
            self.umlView.setSceneSize(width, height)

            # step 4: extract builder data if available
            linenum += 1
            key, value = lines[linenum].split(": ", 1)
            if key.strip() == "builder_data":
                ok = self.builder.parsePersistenceData(version, value)
                if not ok:
                    self.__showInvalidDataMessage(filename, linenum)
                    return False
                linenum += 1

            # step 5: extract the graphics items
            ok, vlinenum = self.umlView.parsePersistenceData(version, lines[linenum:])
            if not ok:
                self.__showInvalidDataMessage(filename, linenum + vlinenum)
                return False

        except IndexError:
            self.__showInvalidDataMessage(filename)
            return False

        # everything worked fine, so remember the file name and set the
        # window title
        self.setWindowTitle(self.__getDiagramTitel(self.__diagramType))
        self.__fileName = filename

        return True

    def __showInvalidDataMessage(self, filename, linenum=-1):
        """
        Private slot to show a message dialog indicating an invalid data file.

        @param filename name of the file containing the invalid data
        @type str
        @param linenum number of the invalid line
        @type int
        """
        msg = (
            self.tr(
                """<p>The file <b>{0}</b> does not contain valid data.</p>"""
            ).format(filename)
            if linenum < 0
            else self.tr(
                """<p>The file <b>{0}</b> does not contain"""
                """ valid data.</p><p>Invalid line: {1}</p>"""
            ).format(filename, linenum + 1)
        )
        EricMessageBox.critical(self, self.tr("Load Diagram"), msg)

    #######################################################################
    ## Methods to read and write eric graphics files of the JSON based
    ## file format.
    #######################################################################

    def __writeJsonGraphicsFile(self, filename):
        """
        Private method to write an eric graphics file using the JSON based
        file format.

        @param filename name of the file to write to
        @type str
        @return flag indicating a successful write
        @rtype bool
        """
        data = {
            "version": "1.0",
            "type": self.__diagramType.value,
            "title": self.__getDiagramTitel(self.__diagramType),
            "width": self.scene.width(),
            "height": self.scene.height(),
            "builder": self.builder.toDict(),
            "view": self.umlView.toDict(),
        }

        try:
            jsonString = json.dumps(data, indent=2)
            with open(filename, "w") as f:
                f.write(jsonString)
            return True
        except (OSError, TypeError) as err:
            EricMessageBox.critical(
                self,
                self.tr("Save Diagram"),
                self.tr(
                    """<p>The file <b>{0}</b> could not be saved.</p>"""
                    """<p>Reason: {1}</p>"""
                ).format(filename, str(err)),
            )
            return False

    def __readJsonGraphicsFile(self, filename):
        """
        Private method to read an eric graphics file using the JSON based
        file format.

        @param filename name of the file to be read
        @type str
        @return flag indicating a successful read
        @rtype bool
        """
        try:
            with open(filename, "r") as f:
                jsonString = f.read()
            data = json.loads(jsonString)
        except (OSError, json.JSONDecodeError) as err:
            EricMessageBox.critical(
                None,
                self.tr("Load Diagram"),
                self.tr(
                    """<p>The file <b>{0}</b> could not be read.</p>"""
                    """<p>Reason: {1}</p>"""
                ).format(filename, str(err)),
            )
            return False

        try:
            # step 1: check version
            if data["version"] in UMLDialog.JsonFileVersions:
                version = data["version"]
            else:
                self.__showInvalidDataMessage(filename)
                return False

            # step 2: set diagram type
            try:
                self.__diagramType = UMLDialogType(data["type"])
            except ValueError:
                self.__showInvalidDataMessage(filename)
                return False
            self.scene.clear()
            self.builder = self.__diagramBuilder(self.__diagramType, "")

            # step 3: set scene size
            self.umlView.setSceneSize(data["width"], data["height"])

            # step 4: extract builder data if available
            ok, msg = self.builder.fromDict(version, data["builder"])
            if not ok:
                if msg:
                    res = EricMessageBox.warning(
                        self,
                        self.tr("Load Diagram"),
                        msg,
                        EricMessageBox.Abort | EricMessageBox.Ignore,
                        EricMessageBox.Abort,
                    )
                    if res == EricMessageBox.Abort:
                        return False
                    else:
                        self.umlView.setLayoutActionsEnabled(False)
                else:
                    self.__showInvalidDataMessage(filename)
                    return False

            # step 5: extract the graphics items
            ok = self.umlView.fromDict(version, data["view"])
            if not ok:
                self.__showInvalidDataMessage(filename)
                return False
        except KeyError:
            self.__showInvalidDataMessage(filename)
            return False

        # everything worked fine, so remember the file name and set the
        # window title
        self.setWindowTitle(self.__getDiagramTitel(self.__diagramType))
        self.__fileName = filename

        return True
