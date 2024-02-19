# -*- coding: utf-8 -*-

# Copyright (c) 2006 - 2024 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the browser model.
"""

import contextlib
import os
import re

from PyQt6.QtCore import QDir, QFileSystemWatcher, QModelIndex, Qt, pyqtSignal
from PyQt6.QtGui import QColor

from eric7 import Preferences
from eric7.SystemUtilities import FileSystemUtilities
from eric7.UI.BrowserModel import (
    BrowserDirectoryItem,
    BrowserFileItem,
    BrowserItem,
    BrowserItemType,
    BrowserModel,
    BrowserSimpleDirectoryItem,
)
from eric7.Utilities import ModuleParser
from eric7.VCS.VersionControl import VersionControlState


class ProjectBrowserItemMixin:
    """
    Class implementing common methods of project browser items.

    It is meant to be used as a mixin class.
    """

    def __init__(self, type_, bold=False):
        """
        Constructor

        @param type_ type of file/directory in the project
        @type str
        @param bold flag indicating a highlighted font
        @type bool
        """
        self._projectTypes = [type_]
        self.bold = bold
        self.vcsState = " "

    def getTextColor(self):
        """
        Public method to get the items text color.

        @return text color
        @rtype QColor
        """
        if self.bold:
            return Preferences.getProjectBrowserColour("Highlighted")
        else:
            return None

    def setVcsState(self, state):
        """
        Public method to set the items VCS state.

        @param state VCS state (one of A, C, M, U or " ")
        @type str
        """
        self.vcsState = state

    def addVcsStatus(self, vcsStatus):
        """
        Public method to add the VCS status.

        @param vcsStatus VCS status text
        @type str
        """
        self.itemData.append(vcsStatus)

    def setVcsStatus(self, vcsStatus):
        """
        Public method to set the VCS status.

        @param vcsStatus VCS status text
        @type str
        """
        self.itemData[1] = vcsStatus

    def getProjectTypes(self):
        """
        Public method to get the project type.

        @return project type
        @rtype str
        """
        return self._projectTypes[:]

    def addProjectType(self, type_):
        """
        Public method to add a type to the list.

        @param type_ type to add to the list
        @type str
        """
        self._projectTypes.append(type_)


class ProjectBrowserSimpleDirectoryItem(
    BrowserSimpleDirectoryItem, ProjectBrowserItemMixin
):
    """
    Class implementing the data structure for project browser simple directory
    items.
    """

    def __init__(self, parent, projectType, text, path=""):
        """
        Constructor

        @param parent parent item
        @type BrowserItem
        @param projectType type of file/directory in the project
        @type str
        @param text text to be displayed
        @type str
        @param path path of the directory
        @type str
        """
        BrowserSimpleDirectoryItem.__init__(self, parent, text, path=path)
        ProjectBrowserItemMixin.__init__(self, projectType)

        self.type_ = BrowserItemType.PbSimpleDirectory


class ProjectBrowserDirectoryItem(BrowserDirectoryItem, ProjectBrowserItemMixin):
    """
    Class implementing the data structure for project browser directory items.
    """

    def __init__(self, parent, dinfo, projectType, full=True, bold=False):
        """
        Constructor

        @param parent parent item
        @type BrowserItem
        @param dinfo dinfo is the string for the directory
        @type str
        @param projectType type of file/directory in the project
        @type str
        @param full flag indicating full pathname should be displayed
        @type bool
        @param bold flag indicating a highlighted font
        @type bool
        """
        BrowserDirectoryItem.__init__(self, parent, dinfo, full)
        ProjectBrowserItemMixin.__init__(self, projectType, bold)

        self.type_ = BrowserItemType.PbDirectory


class ProjectBrowserFileItem(BrowserFileItem, ProjectBrowserItemMixin):
    """
    Class implementing the data structure for project browser file items.
    """

    def __init__(
        self, parent, finfo, projectType, full=True, bold=False, sourceLanguage=""
    ):
        """
        Constructor

        @param parent parent item
        @type BrowserItem
        @param finfo the string for the file
        @type str
        @param projectType type of file/directory in the project
        @type str
        @param full flag indicating full pathname should be displayed
        @type bool
        @param bold flag indicating a highlighted font
        @type bool
        @param sourceLanguage source code language of the project
        @type str
        """
        BrowserFileItem.__init__(self, parent, finfo, full, sourceLanguage)
        ProjectBrowserItemMixin.__init__(self, projectType, bold)

        self.type_ = BrowserItemType.PbFile


class ProjectBrowserModel(BrowserModel):
    """
    Class implementing the project browser model.

    @signal vcsStateChanged(str) emitted after the VCS state has changed
    """

    vcsStateChanged = pyqtSignal(str)

    def __init__(self, parent):
        """
        Constructor

        @param parent reference to parent object
        @type Project.Project
        """
        super().__init__(parent, nopopulate=True)

        rootData = self.tr("Name")
        self.rootItem = BrowserItem(None, rootData)
        self.rootItem.itemData.append(self.tr("VCS Status"))

        self.progDir = None
        self.project = parent
        self.__projectBrowser = None

        self.watchedItems = {}
        self.__watcherActive = True
        self.watcher = QFileSystemWatcher(self)
        self.watcher.directoryChanged.connect(self.directoryChanged)

        self.inRefresh = False

        self.colorNames = {
            "A": "VcsAdded",
            "M": "VcsModified",
            "O": "VcsRemoved",
            "R": "VcsReplaced",
            "U": "VcsUpdate",
            "Z": "VcsConflict",
        }
        self.itemBackgroundColors = {
            " ": QColor(),
            "A": Preferences.getProjectBrowserColour(self.colorNames["A"]),
            "M": Preferences.getProjectBrowserColour(self.colorNames["M"]),
            "O": Preferences.getProjectBrowserColour(self.colorNames["O"]),
            "R": Preferences.getProjectBrowserColour(self.colorNames["R"]),
            "U": Preferences.getProjectBrowserColour(self.colorNames["U"]),
            "Z": Preferences.getProjectBrowserColour(self.colorNames["Z"]),
        }

        self.highLightColor = Preferences.getProjectBrowserColour("Highlighted")
        # needed by preferencesChanged()

        self.vcsStatusReport = {}

    def setProjectBrowserReference(self, projectBrowser):
        """
        Public method to set a reference to the project browser instance.

        @param projectBrowser reference to the project browser instance
        @type ProjectBrowser
        """
        self.__projectBrowser = projectBrowser

    def data(self, index, role):
        """
        Public method to get data of an item.

        @param index index of the data to retrieve
        @type QModelIndex
        @param role role of data
        @type Qt.ItemDataRole
        @return requested data
        @rtype Any
        """
        if not index.isValid():
            return None

        if role == Qt.ItemDataRole.ForegroundRole:
            if index.column() == 0:
                try:
                    return index.internalPointer().getTextColor()
                except AttributeError:
                    return None
        elif role == Qt.ItemDataRole.BackgroundRole:
            try:
                col = self.itemBackgroundColors[index.internalPointer().vcsState]
                if col.isValid():
                    return col
                else:
                    return None
            except AttributeError:
                return None
            except KeyError:
                return None

        return BrowserModel.data(self, index, role)

    def populateItem(self, parentItem, repopulate=False):
        """
        Public method to populate an item's subtree.

        @param parentItem reference to the item to be populated
        @type BrowserItem
        @param repopulate flag indicating a repopulation
        @type bool
        """
        if parentItem.type() == BrowserItemType.PbSimpleDirectory:
            return  # nothing to do
        elif parentItem.type() == BrowserItemType.PbDirectory:
            self.populateProjectDirectoryItem(parentItem, repopulate)
        elif parentItem.type() == BrowserItemType.PbFile:
            self.populateFileItem(parentItem, repopulate)
        else:
            BrowserModel.populateItem(self, parentItem, repopulate)

    def populateProjectDirectoryItem(self, parentItem, repopulate=False):
        """
        Public method to populate a directory item's subtree.

        @param parentItem reference to the directory item to be populated
        @type BrowserItem
        @param repopulate flag indicating a repopulation
        @type bool
        """
        self._addWatchedItem(parentItem)

        qdir = QDir(parentItem.dirName())

        fileFilter = (
            (QDir.Filter.AllEntries | QDir.Filter.Hidden | QDir.Filter.NoDotAndDotDot)
            if Preferences.getProject("BrowsersListHiddenFiles")
            else QDir.Filter.AllEntries | QDir.Filter.NoDotAndDotDot
        )
        entryInfoList = qdir.entryInfoList(fileFilter)

        if len(entryInfoList) > 0:
            if repopulate:
                self.beginInsertRows(
                    self.createIndex(parentItem.row(), 0, parentItem),
                    0,
                    len(entryInfoList) - 1,
                )
            states = {}
            if self.project.vcs is not None:
                for f in entryInfoList:
                    fname = f.absoluteFilePath()
                    states[os.path.normcase(fname)] = 0
                dname = parentItem.dirName()
                self.project.vcs.clearStatusCache()
                states = self.project.vcs.vcsAllRegisteredStates(states, dname)

            for f in entryInfoList:
                node = (
                    ProjectBrowserDirectoryItem(
                        parentItem,
                        FileSystemUtilities.toNativeSeparators(f.absoluteFilePath()),
                        parentItem.getProjectTypes()[0],
                        False,
                    )
                    if f.isDir()
                    else ProjectBrowserFileItem(
                        parentItem,
                        FileSystemUtilities.toNativeSeparators(f.absoluteFilePath()),
                        parentItem.getProjectTypes()[0],
                    )
                )
                if self.project.vcs is not None:
                    fname = f.absoluteFilePath()
                    if (
                        states[os.path.normcase(fname)]
                        == VersionControlState.Controlled
                    ):
                        node.addVcsStatus(self.project.vcs.vcsName())
                        self.project.clearStatusMonitorCachedState(f.absoluteFilePath())
                    else:
                        node.addVcsStatus(self.tr("local"))
                else:
                    node.addVcsStatus("")
                self._addItem(node, parentItem)
            if repopulate:
                self.endInsertRows()

    def projectClosed(self):
        """
        Public method called after a project has been closed.
        """
        self.__vcsStatus = {}

        self.watchedItems = {}
        watchedDirs = self.watcher.directories()
        if watchedDirs:
            self.watcher.removePaths(watchedDirs)

        self.rootItem.removeChildren()
        self.beginResetModel()
        self.endResetModel()

        # reset the module parser cache
        ModuleParser.resetParsedModules()

    def projectOpened(self):
        """
        Public method used to populate the model after a project has been
        opened.
        """
        self.__vcsStatus = {}
        states = {}
        fileCategories = self.project.getFileCategories()

        if self.project.vcs is not None:
            for fileCategory in fileCategories:
                for fn in self.project.getProjectData(dataKey=fileCategory):
                    states[os.path.normcase(os.path.join(self.project.ppath, fn))] = 0

            self.project.vcs.clearStatusCache()
            states = self.project.vcs.vcsAllRegisteredStates(states, self.project.ppath)

        self.inRefresh = True
        for fileCategory in fileCategories:
            # Show the entry in bold in the others browser to make it more
            # distinguishable
            bold = fileCategory == "OTHERS"
            sourceLanguage = (
                self.project.getProjectLanguage() if fileCategory == "SOURCES" else ""
            )

            for fn in self.project.getProjectData(dataKey=fileCategory):
                fname = os.path.join(self.project.ppath, fn)
                parentItem, dt = self.findParentItemByName(
                    self.__projectBrowser.getProjectBrowserFilter(fileCategory), fn
                )
                itm = (
                    ProjectBrowserDirectoryItem(
                        parentItem,
                        fname,
                        self.__projectBrowser.getProjectBrowserFilter(fileCategory),
                        False,
                        bold,
                    )
                    if os.path.isdir(fname)
                    else ProjectBrowserFileItem(
                        parentItem,
                        fname,
                        self.__projectBrowser.getProjectBrowserFilter(fileCategory),
                        False,
                        bold,
                        sourceLanguage=sourceLanguage,
                    )
                )
                self._addItem(itm, parentItem)
                if self.project.vcs is not None:
                    if (
                        states[os.path.normcase(fname)]
                        == VersionControlState.Controlled
                    ):
                        itm.addVcsStatus(self.project.vcs.vcsName())
                    else:
                        itm.addVcsStatus(self.tr("local"))
                else:
                    itm.addVcsStatus("")
        self.inRefresh = False
        self.beginResetModel()
        self.endResetModel()

    def findParentItemByName(self, type_, name, dontSplit=False):
        """
        Public method to find an item given its name.

        <b>Note</b>: This method creates all necessary parent items, if they
        don't exist.

        @param type_ type of the item
        @type str
        @param name name of the item
        @type str
        @param dontSplit flag indicating the name should not be split
        @type bool
        @return reference to the item found and the new display name
        @rtype str
        """
        if dontSplit:
            pathlist = []
            pathlist.append(name)
            pathlist.append("ignore_me")
        else:
            pathlist = re.split(r"/|\\", name)

        if len(pathlist) > 1:
            olditem = self.rootItem
            path = self.project.ppath
            for p in pathlist[:-1]:
                itm = self.findChildItem(p, 0, olditem)
                path = os.path.join(path, p)
                if itm is None:
                    itm = ProjectBrowserSimpleDirectoryItem(olditem, type_, p, path)
                    self.__addVCSStatus(itm, path)
                    if self.inRefresh:
                        self._addItem(itm, olditem)
                    else:
                        if olditem == self.rootItem:
                            oldindex = QModelIndex()
                        else:
                            oldindex = self.createIndex(olditem.row(), 0, olditem)
                        self.addItem(itm, oldindex)
                else:
                    if type_ and type_ not in itm.getProjectTypes():
                        itm.addProjectType(type_)
                olditem = itm
            return (itm, pathlist[-1])
        else:
            return (self.rootItem, name)

    def findChildItem(self, text, column, parentItem=None):
        """
        Public method to find a child item given some text.

        @param text text to search for
        @type str
        @param column column to search in
        @type int
        @param parentItem reference to parent item
        @type BrowserItem
        @return reference to the item found
        @rtype BrowserItem
        """
        if parentItem is None:
            parentItem = self.rootItem

        for itm in parentItem.children():
            if itm.data(column) == text:
                return itm

        return None

    def addNewItem(self, typeString, name, additionalTypeStrings=None):
        """
        Public method to add a new item to the model.

        @param typeString string denoting the type of the new item
        @type str
        @param name name of the new item
        @type str
        @param additionalTypeStrings names of additional types
        @type list of str
        """
        # Show the entry in bold in the others browser to make it more
        # distinguishable
        bold = typeString == "OTHERS"

        fname = os.path.join(self.project.ppath, name)
        parentItem, dt = self.findParentItemByName(
            self.__projectBrowser.getProjectBrowserFilter(typeString), name
        )
        parentIndex = (
            QModelIndex()
            if parentItem == self.rootItem
            else self.createIndex(parentItem.row(), 0, parentItem)
        )
        if os.path.isdir(fname):
            itm = ProjectBrowserDirectoryItem(
                parentItem,
                fname,
                self.__projectBrowser.getProjectBrowserFilter(typeString),
                False,
                bold,
            )
        else:
            if typeString == "SOURCES":
                sourceLanguage = self.project.getProjectLanguage()
            else:
                sourceLanguage = ""
            itm = ProjectBrowserFileItem(
                parentItem,
                fname,
                self.__projectBrowser.getProjectBrowserFilter(typeString),
                False,
                bold,
                sourceLanguage=sourceLanguage,
            )
        self.__addVCSStatus(itm, fname)
        if additionalTypeStrings:
            for additionalTypeString in additionalTypeStrings:
                browserType = self.__projectBrowser.getProjectBrowserFilter(
                    additionalTypeString
                )
                itm.addProjectType(browserType)
        self.addItem(itm, parentIndex)

    def renameItem(self, name, newFilename):
        """
        Public method to rename an item.

        @param name the old display name
        @type str
        @param newFilename new filename of the item
        @type str
        """
        itm = self.findItem(name)
        if itm is None:
            return

        index = self.createIndex(itm.row(), 0, itm)
        itm.setName(newFilename, full=False)
        self.dataChanged.emit(index, index)
        self.repopulateItem(newFilename)

    def findItem(self, name):
        """
        Public method to find an item given its name.

        @param name name of the item
        @type str
        @return reference to the item found
        @rtype BrowserItem
        """
        if QDir.isAbsolutePath(name):
            name = self.project.getRelativePath(name)
        pathlist = re.split(r"/|\\", name)
        if len(pathlist) > 0:
            olditem = self.rootItem
            for p in pathlist:
                itm = self.findChildItem(p, 0, olditem)
                if itm is None:
                    return None
                olditem = itm
            return itm
        else:
            return None

    def itemIndexByName(self, name):
        """
        Public method to find an item's index given its name.

        @param name name of the item
        @type str
        @return index of the item found
        @rtype QModelIndex
        """
        itm = self.findItem(name)
        index = self.createIndex(itm.row(), 0, itm) if itm else QModelIndex()
        return index

    def itemIndexByNameAndLine(self, name, lineno):
        """
        Public method to find an item's index given its name.

        @param name name of the item
        @type str
        @param lineno one based line number of the item
        @type int
        @return index of the item found
        @rtype QModelIndex
        """
        index = QModelIndex()
        itm = self.findItem(name)
        if itm is not None and isinstance(itm, ProjectBrowserFileItem):
            olditem = itm
            autoPopulate = Preferences.getProject("AutoPopulateItems")
            while itm is not None:
                if not itm.isPopulated():
                    if itm.isLazyPopulated() and autoPopulate:
                        self.populateItem(itm)
                    else:
                        break
                for child in itm.children():
                    with contextlib.suppress(AttributeError):
                        start, end = child.boundaries()
                        if end == -1:
                            end = 1000000  # assume end of file
                        if start <= lineno <= end:
                            itm = child
                            break
                else:
                    itm = None
                if itm:
                    olditem = itm
            index = self.createIndex(olditem.row(), 0, olditem)

        return index

    def startFileSystemMonitoring(self):
        """
        Public method to (re)start monitoring the project file system.
        """
        self.__watcherActive = True

    def stopFileSystemMonitoring(self):
        """
        Public method to stop monitoring the project file system.
        """
        self.__watcherActive = False

    def directoryChanged(self, path):
        """
        Public slot to handle the directoryChanged signal of the watcher.

        @param path path of the directory
        @type str
        """
        if not self.__watcherActive:
            return

        if path not in self.watchedItems:
            # just ignore the situation we don't have a reference to the item
            return

        fileFilter = (
            (QDir.Filter.AllEntries | QDir.Filter.Hidden | QDir.Filter.NoDotAndDotDot)
            if Preferences.getProject("BrowsersListHiddenFiles")
            else QDir.Filter.AllEntries | QDir.Filter.NoDotAndDotDot
        )

        for itm in self.watchedItems[path]:
            oldCnt = itm.childCount()

            qdir = QDir(itm.dirName())

            entryInfoList = qdir.entryInfoList(fileFilter)

            # step 1: check for new entries
            children = itm.children()
            for f in entryInfoList:
                fpath = FileSystemUtilities.toNativeSeparators(f.absoluteFilePath())
                childFound = False
                for child in children[:]:
                    if child.name() == fpath:
                        childFound = True
                        children.remove(child)
                        break
                if childFound:
                    continue

                cnt = itm.childCount()
                self.beginInsertRows(self.createIndex(itm.row(), 0, itm), cnt, cnt)
                node = (
                    ProjectBrowserDirectoryItem(
                        itm,
                        FileSystemUtilities.toNativeSeparators(f.absoluteFilePath()),
                        itm.getProjectTypes()[0],
                        False,
                    )
                    if f.isDir()
                    else ProjectBrowserFileItem(
                        itm,
                        FileSystemUtilities.toNativeSeparators(f.absoluteFilePath()),
                        itm.getProjectTypes()[0],
                    )
                )
                self._addItem(node, itm)
                if self.project.vcs is not None:
                    self.project.vcs.clearStatusCache()
                    state = self.project.vcs.vcsRegisteredState(node.name())
                    if state == VersionControlState.Controlled:
                        node.addVcsStatus(self.project.vcs.vcsName())
                    else:
                        node.addVcsStatus(self.tr("local"))
                self.endInsertRows()

            # step 2: check for removed entries
            if len(entryInfoList) != itm.childCount():
                for row in range(oldCnt - 1, -1, -1):
                    child = itm.child(row)
                    childname = FileSystemUtilities.fromNativeSeparators(child.name())
                    entryFound = False
                    for f in entryInfoList[:]:
                        if f.absoluteFilePath() == childname:
                            entryFound = True
                            entryInfoList.remove(f)
                            break
                    if entryFound:
                        continue

                    self._removeWatchedItem(child)
                    self.beginRemoveRows(self.createIndex(itm.row(), 0, itm), row, row)
                    itm.removeChild(child)
                    self.endRemoveRows()

    def __addVCSStatus(self, item, name):
        """
        Private method used to set the vcs status of a node.

        @param item item to work on
        @type BrowserItem
        @param name filename belonging to this item
        @type str
        """
        vcs = self.project.vcs
        if vcs is not None:
            state = vcs.vcsRegisteredState(name)
            if state == VersionControlState.Controlled:
                item.addVcsStatus(vcs.vcsName())
            else:
                item.addVcsStatus(self.tr("local"))
        else:
            item.addVcsStatus("")

    def __updateVCSStatus(self, item, name, recursive=True):
        """
        Private method used to update the vcs status of a node.

        @param item item to work on
        @type BrowserItem
        @param name filename belonging to this item
        @type str
        @param recursive flag indicating a recursive update
        @type bool
        """
        vcs = self.project.vcs
        if vcs is not None:
            vcs.clearStatusCache()
            state = vcs.vcsRegisteredState(name)
            if state == VersionControlState.Controlled:
                item.setVcsStatus(vcs.vcsName())
            else:
                item.setVcsStatus(self.tr("local"))
            if recursive:
                name = os.path.dirname(name)
                parentItem = item.parent()
                if name and parentItem is not self.rootItem:
                    self.__updateVCSStatus(parentItem, name, recursive)
        else:
            item.setVcsStatus("")

        index = self.createIndex(item.row(), 0, item)
        self.dataChanged.emit(index, index)

    def updateVCSStatus(self, name, recursive=True):
        """
        Public method used to update the vcs status of a node.

        @param name filename belonging to this item
        @type str
        @param recursive flag indicating a recursive update
        @type bool
        """
        item = self.findItem(name)
        if item:
            self.__updateVCSStatus(item, name, recursive)

    def removeItem(self, name):
        """
        Public method to remove a named item.

        @param name file or directory name of the item
        @type str
        """
        fname = os.path.basename(name)
        parentItem = self.findParentItemByName(0, name)[0]
        parentIndex = (
            QModelIndex()
            if parentItem == self.rootItem
            else self.createIndex(parentItem.row(), 0, parentItem)
        )
        childItem = self.findChildItem(fname, 0, parentItem)
        if childItem is not None:
            self.beginRemoveRows(parentIndex, childItem.row(), childItem.row())
            parentItem.removeChild(childItem)
            self.endRemoveRows()

    def repopulateItem(self, name):
        """
        Public method to repopulate an item.

        @param name name of the file relative to the project root
        @type str
        """
        itm = self.findItem(name)
        if itm is None:
            return

        if itm.isLazyPopulated():
            if not itm.isPopulated():
                # item is not populated yet, nothing to do
                return

            if itm.childCount():
                index = self.createIndex(itm.row(), 0, itm)
                self.beginRemoveRows(index, 0, itm.childCount() - 1)
                itm.removeChildren()
                self.endRemoveRows()
            ModuleParser.resetParsedModule(os.path.join(self.project.ppath, name))

            self.populateItem(itm, True)

    def projectPropertiesChanged(self):
        """
        Public method to react on a change of the project properties.
        """
        # nothing to do for now
        return

    def changeVCSStates(self, statesList):
        """
        Public slot to record the (non normal) VCS states.

        @param statesList list of VCS state entries giving the states in the
            first column and the path relative to the project directory starting
            with the third column. The allowed status flags are:
            <ul>
                <li>"A" path was added but not yet comitted</li>
                <li>"M" path has local changes</li>
                <li>"O" path was removed</li>
                <li>"R" path was deleted and then re-added</li>
                <li>"U" path needs an update</li>
                <li>"Z" path contains a conflict</li>
                <li>" " path is back at normal</li>
            </ul>
        @type list of str
        """
        statesList.sort()
        lastHead = ""
        itemCache = {}
        if len(statesList) == 1 and statesList[0] == "--RESET--":
            statesList = []
            for name in self.__vcsStatus:
                statesList.append(" {0}".format(name))

        for name in statesList:
            state = name[0]
            if state in "AMORUZ ":
                name = name[1:].strip()
                if state == " ":
                    if name in self.__vcsStatus:
                        del self.__vcsStatus[name]
                else:
                    self.__vcsStatus[name] = state

                try:
                    itm = itemCache[name]
                except KeyError:
                    itm = self.findItem(name)
                    if itm:
                        itemCache[name] = itm
                if itm:
                    itm.setVcsState(state)
                    itm.setVcsStatus(self.project.vcs.vcsName())
                    index1 = self.createIndex(itm.row(), 0, itm)
                    index2 = self.createIndex(
                        itm.row(), self.rootItem.columnCount() - 1, itm
                    )
                    self.dataChanged.emit(index1, index2)

                head, tail = os.path.split(name)
                if head != lastHead:
                    if lastHead:
                        self.__changeParentsVCSState(lastHead, itemCache)
                    lastHead = head
        if lastHead:
            self.__changeParentsVCSState(lastHead, itemCache)
        try:
            globalVcsStatus = sorted(self.__vcsStatus.values())[-1]
        except IndexError:
            globalVcsStatus = " "
        self.vcsStateChanged.emit(globalVcsStatus)

    def __changeParentsVCSState(self, path, itemCache):
        """
        Private method to recursively change the parents VCS state.

        @param path pathname of parent item
        @type str
        @param itemCache reference to the item cache used to store
            references to named items
        @type dict
        """
        while path:
            try:
                itm = itemCache[path]
            except KeyError:
                itm = self.findItem(path)
                if itm:
                    itemCache[path] = itm
            if itm:
                state = " "
                for id_ in itm.children():
                    if state < id_.vcsState:
                        state = id_.vcsState
                if state != itm.vcsState:
                    itm.setVcsState(state)
                    index1 = self.createIndex(itm.row(), 0, itm)
                    index2 = self.createIndex(
                        itm.row(), self.rootItem.columnCount() - 1, itm
                    )
                    self.dataChanged.emit(index1, index2)
            path, tail = os.path.split(path)

    def preferencesChanged(self):
        """
        Public method used to handle a change in preferences.
        """
        for code in self.colorNames:
            color = Preferences.getProjectBrowserColour(self.colorNames[code])
            if color.name() == self.itemBackgroundColors[code].name():
                continue

            self.itemBackgroundColors[code] = color

        color = Preferences.getProjectBrowserColour("Highlighted")
        if self.highLightColor.name() != color.name():
            self.highLightColor = color
