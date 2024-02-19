# -*- coding: utf-8 -*-

# Copyright (c) 2010 - 2024 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a class for reading an XML multi project file.
"""

import os

from PyQt6.QtCore import QUuid

from eric7.MultiProject.MultiProjectProjectMeta import MultiProjectProjectMeta
from eric7.SystemUtilities import FileSystemUtilities

from .Config import multiProjectFileFormatVersion
from .XMLStreamReaderBase import XMLStreamReaderBase


class MultiProjectReader(XMLStreamReaderBase):
    """
    Class for reading an XML multi project file.
    """

    supportedVersions = ["4.2", "5.0", "5.1"]

    def __init__(self, device, multiProject):
        """
        Constructor

        @param device reference to the I/O device to read from
        @type QIODevice
        @param multiProject Reference to the multi project object to store the
            information into.
        @type MultiProject
        """
        XMLStreamReaderBase.__init__(self, device)

        self.multiProject = multiProject
        self.path = os.path.dirname(device.fileName())

        self.version = ""

    def readXML(self):
        """
        Public method to read and parse the XML document.
        """
        while not self.atEnd():
            self.readNext()
            if self.isStartElement():
                if self.name() == "MultiProject":
                    self.version = self.attribute(
                        "version", multiProjectFileFormatVersion
                    )
                    if self.version not in self.supportedVersions:
                        self.raiseUnsupportedFormatVersion(self.version)
                elif self.name() == "Description":
                    self.multiProject.description = self.readElementText()
                elif self.name() == "Projects":
                    self.__readProjects()
                else:
                    self.raiseUnexpectedStartTag(self.name())

        self.showErrorMessage()

    def __readProjects(self):
        """
        Private method to read the project infos.
        """
        while not self.atEnd():
            self.readNext()
            if self.isEndElement() and self.name() == "Projects":
                break

            if self.isStartElement():
                if self.name() == "Project":
                    self.__readProject()
                else:
                    self.raiseUnexpectedStartTag(self.name())

    def __readProject(self):
        """
        Private method to read the project info.
        """
        uid = self.attribute("uid", "")

        project = MultiProjectProjectMeta(
            name="",
            file="",
            uid=uid if uid else QUuid.createUuid().toString(),
            main=self.toBool(self.attribute("isMaster", "False")),
        )

        while not self.atEnd():
            self.readNext()
            if self.isEndElement() and self.name() == "Project":
                self.multiProject.addProject(project)
                break

            if self.isStartElement():
                if self.name() == "ProjectName":
                    project.name = self.readElementText()
                elif self.name() == "ProjectFile":
                    project.file = FileSystemUtilities.absoluteUniversalPath(
                        self.readElementText(), self.path
                    )
                elif self.name() == "ProjectDescription":
                    project.description = self.readElementText()
                elif self.name() == "ProjectCategory":
                    project.category = self.readElementText()
                else:
                    self.raiseUnexpectedStartTag(self.name())
