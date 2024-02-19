# -*- coding: utf-8 -*-

# Copyright (c) 2010 - 2024 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing alternative functions for the QFileDialog static methods.
"""

import pathlib

from PyQt6.QtWidgets import QFileDialog

from eric7.SystemUtilities import OSUtilities

Option = QFileDialog.Option

ShowDirsOnly = QFileDialog.Option.ShowDirsOnly
DontResolveSymlinks = QFileDialog.Option.DontResolveSymlinks
DontConfirmOverwrite = QFileDialog.Option.DontConfirmOverwrite
DontUseNativeDialog = QFileDialog.Option.DontUseNativeDialog
ReadOnly = QFileDialog.Option.ReadOnly
HideNameFilterDetails = QFileDialog.Option.HideNameFilterDetails
DontUseCustomDirectoryIcons = QFileDialog.Option.DontUseCustomDirectoryIcons


def __reorderFilter(filterStr, initialFilter=""):
    """
    Private function to reorder the file filter to cope with a KDE issue
    introduced by distributor's usage of KDE file dialogs.

    @param filterStr Qt file filter
    @type str
    @param initialFilter initial filter
    @type str
    @return the rearranged Qt file filter
    @rtype str
    """
    if initialFilter and not OSUtilities.isMacPlatform():
        fileFilters = filterStr.split(";;")
        if len(fileFilters) < 10 and initialFilter in fileFilters:
            fileFilters.remove(initialFilter)
        fileFilters.insert(0, initialFilter)
        return ";;".join(fileFilters)
    else:
        return filterStr


###########################################################################
## String based interface
###########################################################################


def getOpenFileName(parent=None, caption="", directory="", filterStr="", options=None):
    """
    Module function to get the name of a file for opening it.

    @param parent parent widget of the dialog
    @type QWidget
    @param caption window title of the dialog
    @type str
    @param directory working directory of the dialog
    @type str
    @param filterStr filter string for the dialog
    @type str
    @param options various options for the dialog
    @type QFileDialog.Options
    @return name of file to be opened
    @rtype str
    """
    if options is None:
        options = QFileDialog.Option(0)
    return QFileDialog.getOpenFileName(
        parent, caption, directory, filterStr, "", options
    )[0]


def getOpenFileNameAndFilter(
    parent=None, caption="", directory="", filterStr="", initialFilter="", options=None
):
    """
    Module function to get the name of a file for opening it and the selected
    file name filter.

    @param parent parent widget of the dialog
    @type QWidget
    @param caption window title of the dialog
    @type str
    @param directory working directory of the dialog
    @type str
    @param filterStr filter string for the dialog
    @type str
    @param initialFilter initial filter for the dialog
    @type str
    @param options various options for the dialog
    @type QFileDialog.Options
    @return name of file to be opened and selected filter
    @rtype tuple of (str, str)
    """
    if options is None:
        options = QFileDialog.Option(0)
    newfilter = __reorderFilter(filterStr, initialFilter)
    return QFileDialog.getOpenFileName(
        parent, caption, directory, newfilter, initialFilter, options
    )


def getOpenFileNames(parent=None, caption="", directory="", filterStr="", options=None):
    """
    Module function to get a list of names of files for opening.

    @param parent parent widget of the dialog
    @type QWidget
    @param caption window title of the dialog
    @type str
    @param directory working directory of the dialog
    @type str
    @param filterStr filter string for the dialog
    @type str
    @param options various options for the dialog
    @type QFileDialog.Options
    @return list of file names to be opened
    @rtype list of str
    """
    if options is None:
        options = QFileDialog.Option(0)
    return QFileDialog.getOpenFileNames(
        parent, caption, directory, filterStr, "", options
    )[0]


def getOpenFileNamesAndFilter(
    parent=None, caption="", directory="", filterStr="", initialFilter="", options=None
):
    """
    Module function to get a list of names of files for opening and the
    selected file name filter.

    @param parent parent widget of the dialog
    @type QWidget
    @param caption window title of the dialog
    @type str
    @param directory working directory of the dialog
    @type str
    @param filterStr filter string for the dialog
    @type str
    @param initialFilter initial filter for the dialog
    @type str
    @param options various options for the dialog
    @type QFileDialog.Options
    @return list of file names to be opened and selected filter
    @rtype tuple of (list of str, str)
    """
    if options is None:
        options = QFileDialog.Option(0)
    newfilter = __reorderFilter(filterStr, initialFilter)
    return QFileDialog.getOpenFileNames(
        parent, caption, directory, newfilter, initialFilter, options
    )


def getOpenFileAndDirNames(
    parent=None, caption="", directory="", filterStr="", options=None
):
    """
    Module function to get the names of files and directories for opening.

    @param parent parent widget of the dialog
    @type QWidget
    @param caption window title of the dialog
    @type str
    @param directory working directory of the dialog
    @type str
    @param filterStr filter string for the dialog
    @type str
    @param options various options for the dialog
    @type QFileDialog.Options
    @return names of the selected files and folders
    @rtype list of str
    """
    from .EricDirFileDialog import EricDirFileDialog

    return EricDirFileDialog.getOpenFileAndDirNames(
        parent, caption, directory, filterStr, options
    )


def getSaveFileName(parent=None, caption="", directory="", filterStr="", options=None):
    """
    Module function to get the name of a file for saving.

    @param parent parent widget of the dialog
    @type QWidget
    @param caption window title of the dialog
    @type str
    @param directory working directory of the dialog
    @type str
    @param filterStr filter string for the dialog
    @type str
    @param options various options for the dialog
    @type QFileDialog.Options
    @return name of file to be saved
    @rtype str
    """
    if options is None:
        options = QFileDialog.Option(0)
    return QFileDialog.getSaveFileName(
        parent, caption, directory, filterStr, "", options
    )[0]


def getSaveFileNameAndFilter(
    parent=None, caption="", directory="", filterStr="", initialFilter="", options=None
):
    """
    Module function to get the name of a file for saving and the selected file name
    filter.

    @param parent parent widget of the dialog
    @type QWidget
    @param caption window title of the dialog
    @type str
    @param directory working directory of the dialog
    @type str
    @param filterStr filter string for the dialog
    @type str
    @param initialFilter initial filter for the dialog
    @type str
    @param options various options for the dialog
    @type QFileDialog.Options
    @return name of file to be saved and selected filte
    @rtype tuple of (str, str)
    """
    if options is None:
        options = QFileDialog.Option(0)
    newfilter = __reorderFilter(filterStr, initialFilter)
    return QFileDialog.getSaveFileName(
        parent, caption, directory, newfilter, initialFilter, options
    )


def getExistingDirectory(
    parent=None, caption="", directory="", options=QFileDialog.Option.ShowDirsOnly
):
    """
    Module function to get the name of a directory.

    @param parent parent widget of the dialog
    @type QWidget
    @param caption window title of the dialog
    @type str
    @param directory working directory of the dialog
    @type str
    @param options various options for the dialog
    @type QFileDialog.Options
    @return name of selected directory
    @rtype str
    """
    if options is None:
        options = QFileDialog.Option(0)
    return QFileDialog.getExistingDirectory(parent, caption, directory, options)


###########################################################################
## pathlib.Path based interface
###########################################################################


def getOpenFilePath(parent=None, caption="", directory="", filterStr="", options=None):
    """
    Module function to get the path of a file for opening it.

    @param parent parent widget of the dialog
    @type QWidget
    @param caption window title of the dialog
    @type str
    @param directory working directory of the dialog
    @type str or pathlib.Path
    @param filterStr filter string for the dialog
    @type str
    @param options various options for the dialog
    @type QFileDialog.Options
    @return path of file to be opened
    @rtype pathlib.Path
    """
    if options is None:
        options = QFileDialog.Option(0)
    filename = QFileDialog.getOpenFileName(
        parent, caption, str(directory), filterStr, "", options
    )[0]
    return pathlib.Path(filename)


def getOpenFilePathAndFilter(
    parent=None, caption="", directory="", filterStr="", initialFilter="", options=None
):
    """
    Module function to get the path of a file for opening it and the selected
    file name filter.

    @param parent parent widget of the dialog
    @type QWidget
    @param caption window title of the dialog
    @type str
    @param directory working directory of the dialog
    @type str or pathlib.Path
    @param filterStr filter string for the dialog
    @type str
    @param initialFilter initial filter for the dialog
    @type str
    @param options various options for the dialog
    @type QFileDialog.Options
    @return path of file to be opened and selected filter
    @rtype tuple of (pathlib.Path, str)
    """
    if options is None:
        options = QFileDialog.Option(0)
    newfilter = __reorderFilter(filterStr, initialFilter)
    filename, selectedFilter = QFileDialog.getOpenFileName(
        parent, caption, str(directory), newfilter, initialFilter, options
    )
    return pathlib.Path(filename), selectedFilter


def getOpenFilePaths(parent=None, caption="", directory="", filterStr="", options=None):
    """
    Module function to get a list of paths of files for opening.

    @param parent parent widget of the dialog
    @type QWidget
    @param caption window title of the dialog
    @type str
    @param directory working directory of the dialog
    @type str or pathlib.Path
    @param filterStr filter string for the dialog
    @type str
    @param options various options for the dialog
    @type QFileDialog.Options
    @return list of file paths to be opened
    @rtype list of pathlib.Path
    """
    if options is None:
        options = QFileDialog.Option(0)
    filenames = QFileDialog.getOpenFileNames(
        parent, caption, str(directory), filterStr, "", options
    )[0]
    return [pathlib.Path(f) for f in filenames]


def getOpenFilPathsAndFilter(
    parent=None, caption="", directory="", filterStr="", initialFilter="", options=None
):
    """
    Module function to get a list of paths of files for opening and the
    selected file name filter.

    @param parent parent widget of the dialog
    @type QWidget
    @param caption window title of the dialog
    @type str
    @param directory working directory of the dialog
    @type str or pathlib.Path
    @param filterStr filter string for the dialog
    @type str
    @param initialFilter initial filter for the dialog
    @type str
    @param options various options for the dialog
    @type QFileDialog.Options
    @return list of file paths to be opened and selected filter
    @rtype tuple of (list of pathlib.Path, str)
    """
    if options is None:
        options = QFileDialog.Option(0)
    newfilter = __reorderFilter(filterStr, initialFilter)
    filenames, selectedFilter = QFileDialog.getOpenFileNames(
        parent, caption, str(directory), newfilter, initialFilter, options
    )
    return [pathlib.Path(f) for f in filenames], selectedFilter


def getOpenFileAndDirPaths(
    parent=None, caption="", directory="", filterStr="", options=None
):
    """
    Module function to get the paths of files and directories for opening.

    @param parent parent widget of the dialog
    @type QWidget
    @param caption window title of the dialog
    @type str
    @param directory working directory of the dialog
    @type str or pathlib.Path
    @param filterStr filter string for the dialog
    @type str
    @param options various options for the dialog
    @type QFileDialog.Options
    @return paths of the selected files and folders
    @rtype list of pathlib.Path
    """
    from .EricDirFileDialog import EricDirFileDialog

    return EricDirFileDialog.getOpenFileAndDirPaths(
        parent, caption, directory, filterStr, options
    )


def getSaveFilePath(parent=None, caption="", directory="", filterStr="", options=None):
    """
    Module function to get the path of a file for saving.

    @param parent parent widget of the dialog
    @type QWidget
    @param caption window title of the dialog
    @type str
    @param directory working directory of the dialog
    @type str or pathlib.Path
    @param filterStr filter string for the dialog
    @type str
    @param options various options for the dialog
    @type QFileDialog.Options
    @return path of file to be saved
    @rtype pathlib.Path
    """
    if options is None:
        options = QFileDialog.Option(0)
    filename = QFileDialog.getSaveFileName(
        parent, caption, str(directory), filterStr, "", options
    )[0]
    return pathlib.Path(filename)


def getSaveFilePathAndFilter(
    parent=None, caption="", directory="", filterStr="", initialFilter="", options=None
):
    """
    Module function to get the path of a file for saving and the selected
    file name filter.

    @param parent parent widget of the dialog
    @type QWidget
    @param caption window title of the dialog
    @type str
    @param directory working directory of the dialog
    @type str or pathlib.Path
    @param filterStr filter string for the dialog
    @type str
    @param initialFilter initial filter for the dialog
    @type str
    @param options various options for the dialog
    @type QFileDialog.Options
    @return path of file to be saved and selected filte
    @rtype tuple of (pathlib.Path, str)
    """
    if options is None:
        options = QFileDialog.Option(0)
    newfilter = __reorderFilter(filterStr, initialFilter)
    filename, selectedFilter = QFileDialog.getSaveFileName(
        parent, caption, directory, newfilter, initialFilter, options
    )
    return pathlib.Path(filename), selectedFilter


def getExistingDirectoryPath(
    parent=None, caption="", directory="", options=QFileDialog.Option.ShowDirsOnly
):
    """
    Module function to get the path of a directory.

    @param parent parent widget of the dialog
    @type QWidget
    @param caption window title of the dialog
    @type str
    @param directory working directory of the dialog
    @type str or pathlib.Path
    @param options various options for the dialog
    @type QFileDialog.Options
    @return path of selected directory
    @rtype pathlib.Path
    """
    if options is None:
        options = QFileDialog.Option(0)
    dirname = QFileDialog.getExistingDirectory(parent, caption, str(directory), options)
    return pathlib.Path(dirname)


#
# eflag: noqa = U200
