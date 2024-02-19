# -*- coding: utf-8 -*-

# Copyright (c) 2006 - 2024 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module defining common data to be used by all modules.
"""

#
# Note: Do not import any eric stuff in here!!!!!!!
#

import os

import semver

from PyQt6.QtCore import QByteArray, QCoreApplication, QProcess, qVersion

from eric7.SystemUtilities import PythonUtilities

try:
    from eric7.eric7config import getConfig
except ImportError:
    from eric7config import getConfig

# names of the various settings objects
settingsNameOrganization = "Eric7"
settingsNameGlobal = "eric7"
settingsNameRecent = "eric7recent"

# key names of the various recent entries
recentNameBreakpointConditions = "BreakPointConditions"
recentNameBreakpointFiles = "BreakPointFiles"
recentNameFiles = "Files"
recentNameHexFiles = "HexFiles"
recentNameHosts = "Hosts"
recentNameMultiProject = "MultiProjects"
recentNamePdfFiles = "PdfFiles"
recentNameProject = "Projects"
recentNameTestDiscoverHistory = "UTDiscoverHistory"
recentNameTestFileHistory = "UTFileHistory"
recentNameTestNameHistory = "UTTestnameHistory"
recentNameTestFramework = "UTTestFramework"
recentNameTestEnvironment = "UTEnvironmentName"

configDir = None


def getConfigDir():
    """
    Module function to get the name of the directory storing the config data.

    @return directory name of the config dir
    @rtype str
    """
    if configDir is not None and os.path.exists(configDir):
        hp = configDir
    else:
        cdn = ".eric7"
        hp = os.path.join(os.path.expanduser("~"), cdn)
        if not os.path.exists(hp):
            os.mkdir(hp)
    return hp


def getInstallInfoFilePath():
    """
    Public method to get the path name of the install info file.

    @return file path of the install info file
    @rtype str
    """
    filename = "eric7install.{0}.json".format(
        getConfig("ericDir")
        .replace(":", "_")
        .replace("\\", "_")
        .replace("/", "_")
        .replace(" ", "_")
        .strip("_")
    )
    return os.path.join(getConfigDir(), filename)


def setConfigDir(d):
    """
    Module function to set the name of the directory storing the config data.

    @param d name of an existing directory
    @type str
    """
    global configDir
    configDir = os.path.expanduser(d)


###############################################################################
## functions for version handling
###############################################################################


def versionIsValid(version):
    """
    Function to check, if the given version string is valid.

    @param version version string
    @type str
    @return flag indicating validity
    @rtype bool
    """
    try:
        return semver.VersionInfo.is_valid(version)
    except AttributeError:
        return semver.VersionInfo.isvalid(version)


def versionToTuple(version):
    """
    Module function to convert a version string into a tuple.

    Note: A version string consists of non-negative decimals separated by "."
    optionally followed by a suffix. Suffix is everything after the last
    decimal.

    @param version version string
    @type str
    @return version named tuple containing the version parts
    @rtype semver.VersionInfo
    """
    while version and not version[0].isdecimal():
        # sanitize version string (get rid of leading non-decimal characters)
        version = version[1:]

    while len(version.split(".")) < 3:
        # ensure the version string contains at least three parts
        version += ".0"

    if versionIsValid(version):
        return semver.VersionInfo.parse(version)
    else:
        return semver.VersionInfo(0, 0, 0)


###############################################################################
## functions for extended string handling
###############################################################################


def strGroup(txt, sep, groupLen=4):
    """
    Module function to group a string into sub-strings separated by a
    separator.

    @param txt text to be grouped
    @type str
    @param sep separator string
    @type str
    @param groupLen length of each group
    @type int
    @return result string
    @rtype str
    """
    groups = []

    while len(txt) // groupLen != 0:
        groups.insert(0, txt[-groupLen:])
        txt = txt[:-groupLen]
    if len(txt) > 0:
        groups.insert(0, txt)
    return sep.join(groups)


def strToQByteArray(txt):
    """
    Module function to convert a Python string into a QByteArray.

    @param txt Python string to be converted
    @type str, bytes, bytearray
    @return converted QByteArray
    @rtype QByteArray
    """
    if isinstance(txt, str):
        txt = txt.encode("utf-8")

    return QByteArray(txt)


def dataString(size, loc=None):
    """
    Module function to generate a formatted size string.

    @param size size to be formatted
    @type int
    @param loc locale to be used for localized size strings (defaults to None)
    @type QLocale (optional)
    @return formatted data string
    @rtype str
    """
    if loc is None:
        if size < 1024:
            return QCoreApplication.translate("Globals", "{0:4.2f} Bytes").format(size)
        elif size < 1024 * 1024:
            size /= 1024
            return QCoreApplication.translate("Globals", "{0:4.2f} KiB").format(size)
        elif size < 1024 * 1024 * 1024:
            size /= 1024 * 1024
            return QCoreApplication.translate("Globals", "{0:4.2f} MiB").format(size)
        elif size < 1024 * 1024 * 1024 * 1024:
            size /= 1024 * 1024 * 1024
            return QCoreApplication.translate("Globals", "{0:4.2f} GiB").format(size)
        else:
            size /= 1024 * 1024 * 1024 * 1024
            return QCoreApplication.translate("Globals", "{0:4.2f} TiB").format(size)
    else:
        if size < 1024:
            return QCoreApplication.translate("Globals", "{0} Bytes").format(
                loc.toString(size, "f", 2)
            )
        elif size < 1024 * 1024:
            size /= 1024
            return QCoreApplication.translate("Globals", "{0} KiB").format(
                loc.toString(size, "f", 2)
            )
        elif size < 1024 * 1024 * 1024:
            size /= 1024 * 1024
            return QCoreApplication.translate("Globals", "{0} MiB").format(
                loc.toString(size, "f", 2)
            )
        elif size < 1024 * 1024 * 1024 * 1024:
            size /= 1024 * 1024 * 1024
            return QCoreApplication.translate("Globals", "{0} GiB").format(
                loc.toString(size, "f", 2)
            )
        else:
            size /= 1024 * 1024 * 1024 * 1024
            return QCoreApplication.translate("Globals", "{0} TiB").format(
                loc.toString(size, "f", 2)
            )


###############################################################################
## functions for converting QSetting return types to valid types
###############################################################################


def toBool(value):
    """
    Module function to convert a value to bool.

    @param value value to be converted
    @type str
    @return converted data
    @rtype bool
    """
    if value in ["True", "true", "1", "Yes", "yes"]:
        return True
    elif value in ["False", "false", "0", "No", "no"]:
        return False
    else:
        return bool(value)


def toList(value):
    """
    Module function to convert a value to a list.

    @param value value to be converted
    @type None, list or Any
    @return converted data
    @rtype list
    """
    if value is None:
        return []
    elif not isinstance(value, list):
        return [value]
    else:
        return value


def toByteArray(value):
    """
    Module function to convert a value to a byte array.

    @param value value to be converted
    @type QByteArray or None
    @return converted data
    @rtype QByteArray
    """
    if value is None:
        return QByteArray()
    else:
        return value


def toDict(value):
    """
    Module function to convert a value to a dictionary.

    @param value value to be converted
    @type dict or None
    @return converted data
    @rtype dict
    """
    if value is None:
        return {}
    else:
        return value


###############################################################################
## functions for web browser variant detection
###############################################################################


def getWebBrowserSupport():
    """
    Module function to determine the supported web browser variant.

    @return string indicating the supported web browser variant ("QtWebEngine",
        or "None")
    @rtype str
    """
    try:
        from eric7.eric7config import getConfig  # __IGNORE_WARNING_I101__
    except ImportError:
        from eric7config import getConfig  # __IGNORE_WARNING_I10__

    scriptPath = os.path.join(getConfig("ericDir"), "Tools", "webBrowserSupport.py")
    proc = QProcess()
    proc.start(PythonUtilities.getPythonExecutable(), [scriptPath, qVersion()])
    variant = (
        str(proc.readAllStandardOutput(), "utf-8", "replace").strip()
        if proc.waitForFinished(10000)
        else "None"
    )
    return variant


#
# eflag: noqa = M801, U200
