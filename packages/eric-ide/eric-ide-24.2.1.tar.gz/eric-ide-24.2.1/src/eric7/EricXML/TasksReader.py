# -*- coding: utf-8 -*-

# Copyright (c) 2010 - 2024 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a class for reading an XML tasks file.
"""

import contextlib
import time

from PyQt6.QtCore import QUuid

from eric7.EricWidgets.EricApplication import ericApp
from eric7.SystemUtilities import FileSystemUtilities
from eric7.Tasks.Task import TaskPriority, TaskType

from .Config import tasksFileFormatVersion
from .XMLStreamReaderBase import XMLStreamReaderBase


class TasksReader(XMLStreamReaderBase):
    """
    Class for reading an XML tasks file.
    """

    supportedVersions = ["4.2", "5.0", "5.1", "6.0"]

    def __init__(self, device, forProject=False, viewer=None):
        """
        Constructor

        @param device reference to the I/O device to read from
        @type QIODevice
        @param forProject flag indicating project related mode
        @type bool
        @param viewer reference to the task viewer
        @type TaskViewer
        """
        XMLStreamReaderBase.__init__(self, device)

        self.viewer = viewer

        self.forProject = forProject
        if viewer:
            self.viewer = viewer
        else:
            self.viewer = ericApp().getObject("TaskViewer")

        self.version = ""
        self.tasks = []

    def readXML(self):
        """
        Public method to read and parse the XML document.
        """
        while not self.atEnd():
            self.readNext()
            if self.isEndElement() and self.name() == "Tasks":
                for task, expanded in self.tasks:
                    task.setExpanded(expanded)
                break

            if self.isStartElement():
                if self.name() == "Tasks":
                    self.version = self.attribute("version", tasksFileFormatVersion)
                    if self.version not in self.supportedVersions:
                        self.raiseUnsupportedFormatVersion(self.version)
                elif self.name() == "Task":
                    self.__readTask()
                elif self.name() == "ProjectScanFilter":
                    scanFilter = self.readElementText()
                    if self.forProject:
                        self.viewer.setTasksScanFilter(scanFilter)
                else:
                    self.raiseUnexpectedStartTag(self.name())

        self.showErrorMessage()

    def __readTask(self):
        """
        Private method to read the task info.
        """
        task = {
            "summary": "",
            "created": 0,
            "filename": "",
            "linenumber": 0,
            "type": TaskType.TODO,
            "description": "",
            "uid": "",
            "priority": TaskPriority(
                int(self.attribute("priority", str(TaskPriority.NORMAL.value)))
            ),
            "completed": self.toBool(self.attribute("completed", "False")),
        }
        if self.version in ["4.2", "5.0"]:
            isBugfix = self.toBool(self.attribute("bugfix", "False"))
            if isBugfix:
                task["type"] = TaskType.FIXME
        else:
            task["type"] = TaskType(
                int(self.attribute("type", str(TaskType.TODO.value)))
            )
        uid = self.attribute("uid", "")
        if uid:
            task["uid"] = uid
        else:
            # upgrade from pre 6.0 format
            task["uid"] = QUuid.createUuid().toString()
        parentUid = self.attribute("parent_uid", "")
        expanded = self.toBool(self.attribute("expanded", "True"))

        while not self.atEnd():
            self.readNext()
            if self.isEndElement() and self.name() == "Task":
                parentTask = self.viewer.findParentTask(parentUid)
                addedTask = self.viewer.addTask(
                    task["summary"],
                    priority=task["priority"],
                    filename=task["filename"],
                    lineno=task["linenumber"],
                    completed=task["completed"],
                    _time=task["created"],
                    isProjectTask=self.forProject,
                    taskType=task["type"],
                    description=task["description"],
                    uid=task["uid"],
                    parentTask=parentTask,
                )
                if addedTask:
                    self.tasks.append((addedTask, expanded))
                break

            if self.isStartElement():
                if self.name() == "Summary":
                    task["summary"] = self.readElementText()
                elif self.name() == "Description":
                    task["description"] = self.readElementText()
                elif self.name() == "Created":
                    task["created"] = time.mktime(
                        time.strptime(self.readElementText(), "%Y-%m-%d, %H:%M:%S")
                    )
                elif self.name() == "Resource":
                    continue  # handle but ignore this tag
                elif self.name() == "Filename":
                    task["filename"] = FileSystemUtilities.toNativeSeparators(
                        self.readElementText()
                    )
                elif self.name() == "Linenumber":
                    with contextlib.suppress(ValueError):
                        task["linenumber"] = int(self.readElementText())
                else:
                    self.raiseUnexpectedStartTag(self.name())
