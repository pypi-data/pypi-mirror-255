# -*- coding: utf-8 -*-

# Copyright (c) 2010 - 2024 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a class for reading an XML project file.
"""

from eric7.SystemUtilities import FileSystemUtilities

from .Config import projectFileFormatVersion
from .XMLStreamReaderBase import XMLStreamReaderBase


class ProjectReader(XMLStreamReaderBase):
    """
    Class for reading an XML project file.
    """

    supportedVersions = ["4.6", "5.0", "5.1", "6.0", "6.1", "6.2", "6.3", "6.4", "6.5"]

    def __init__(self, device, project):
        """
        Constructor

        @param device reference to the I/O device to read from
        @type QIODevice
        @param project Reference to the project object to store the
            information into.
        @type Project
        """
        XMLStreamReaderBase.__init__(self, device)

        self.project = project

        self.version = ""

    def readXML(self):
        """
        Public method to read and parse the XML document.
        """
        fileCategoryTags = [
            s.capitalize() for s in self.project.getFileCategories()
        ] + ["Interfaces", "Protocols"]
        # The XML project files always included these.

        while not self.atEnd():
            self.readNext()
            if self.isStartElement():
                if self.name() == "Project":
                    self.version = self.attribute("version", projectFileFormatVersion)
                    if self.version not in self.supportedVersions:
                        self.raiseUnsupportedFormatVersion(self.version)
                elif self.name() == "Language":
                    self.project.setProjectData(
                        self.readElementText(), dataKey="SPELLLANGUAGE", setDirty=False
                    )
                elif self.name() == "ProjectWordList":
                    self.project.setProjectData(
                        FileSystemUtilities.toNativeSeparators(self.readElementText()),
                        dataKey="SPELLWORDS",
                        setDirty=False,
                    )
                elif self.name() == "ProjectExcludeList":
                    self.project.setProjectData(
                        FileSystemUtilities.toNativeSeparators(self.readElementText()),
                        dataKey="SPELLEXCLUDES",
                        setDirty=False,
                    )
                elif self.name() == "Hash":
                    self.project.setProjectData(
                        self.readElementText(), dataKey="HASH", setDirty=False
                    )
                elif self.name() == "ProgLanguage":
                    self.project.setProjectData(
                        int(self.attribute("mixed", "0")),
                        dataKey="MIXEDLANGUAGE",
                        setDirty=False,
                    )
                    self.project.setProjectData(
                        self.readElementText(), dataKey="PROGLANGUAGE", setDirty=False
                    )
                    if self.project.getProjectData(dataKey="PROGLANGUAGE") == "Python":
                        # convert Python to the more specific Python3
                        self.project.setProjectData(
                            "Python3", dataKey="PROGLANGUAGE", setDirty=False
                        )
                elif self.name() == "ProjectType":
                    self.project.setProjectData(
                        self.readElementText(), dataKey="PROJECTTYPE", setDirty=False
                    )
                elif self.name() == "Description":
                    self.project.setProjectData(
                        self.readElementText(), dataKey="DESCRIPTION", setDirty=False
                    )
                elif self.name() == "Version":
                    self.project.setProjectData(
                        self.readElementText(), dataKey="VERSION", setDirty=False
                    )
                elif self.name() == "Author":
                    self.project.setProjectData(
                        self.readElementText(), dataKey="AUTHOR", setDirty=False
                    )
                elif self.name() == "Email":
                    self.project.setProjectData(
                        self.readElementText(), dataKey="EMAIL", setDirty=False
                    )
                elif self.name() == "TranslationPattern":
                    self.project.setProjectData(
                        FileSystemUtilities.toNativeSeparators(self.readElementText()),
                        dataKey="TRANSLATIONPATTERN",
                        setDirty=False,
                    )
                elif self.name() == "TranslationsBinPath":
                    self.project.setProjectData(
                        FileSystemUtilities.toNativeSeparators(self.readElementText()),
                        dataKey="TRANSLATIONSBINPATH",
                        setDirty=False,
                    )
                elif self.name() == "Eol":
                    self.project.setProjectData(
                        int(self.attribute("index", "0")), dataKey="EOL", setDirty=False
                    )
                elif self.name() in fileCategoryTags:
                    self.__readFiles(self.name(), self.name()[:-1], self.name().upper())
                elif self.name() == "TranslationExceptions":
                    self.__readFiles(
                        "TranslationExceptions",
                        "TranslationException",
                        "TRANSLATIONEXCEPTIONS",
                    )
                elif self.name() == "MainScript":
                    self.project.setProjectData(
                        FileSystemUtilities.toNativeSeparators(self.readElementText()),
                        dataKey="MAINSCRIPT",
                        setDirty=False,
                    )
                elif self.name() == "Vcs":
                    self.__readVcs()
                elif self.name() == "FiletypeAssociations":
                    self.__readFiletypeAssociations()
                elif self.name() == "LexerAssociations":
                    self.__readLexerAssociations()
                elif self.name() == "Make":
                    self.__readBasicDataField("Make", "MakeParameters", "MAKEPARAMS")
                elif self.name() == "IdlCompiler":
                    self.__readBasicDataField(
                        "IdlCompiler", "IdlCompilerParameters", "IDLPARAMS"
                    )
                elif self.name() == "UicCompiler":
                    self.__readBasicDataField(
                        "UicCompiler", "UicCompilerParameters", "UICPARAMS"
                    )
                elif self.name() == "RccCompiler":
                    self.__readBasicDataField(
                        "RccCompiler", "RccCompilerParameters", "RCCPARAMS"
                    )
                elif self.name() == "DocstringStyle":
                    self.project.setProjectData(
                        self.readElementText(), dataKey="DOCSTRING", setDirty=False
                    )
                elif self.name() == "ProjectTypeSpecific":
                    self.__readBasicDataField(
                        "ProjectTypeSpecific",
                        "ProjectTypeSpecificData",
                        "PROJECTTYPESPECIFICDATA",
                    )
                elif self.name() == "Documentation":
                    self.__readBasicDataField(
                        "Documentation", "DocumentationParams", "DOCUMENTATIONPARMS"
                    )
                elif self.name() == "Packagers":
                    self.__readBasicDataField(
                        "Packagers", "PackagersParams", "PACKAGERSPARMS"
                    )
                elif self.name() == "Checkers":
                    self.__readBasicDataField(
                        "Checkers", "CheckersParams", "CHECKERSPARMS"
                    )
                elif self.name() == "OtherTools":
                    self.__readBasicDataField(
                        "OtherTools", "OtherToolsParams", "OTHERTOOLSPARMS"
                    )
                else:
                    self.raiseUnexpectedStartTag(self.name())

        self.showErrorMessage()

    def __readFiles(self, tag, listTag, dataKey):
        """
        Private method to read a list of files.

        @param tag name of the list tag
        @type str
        @param listTag name of the list element tag
        @type str
        @param dataKey key of the project data element
        @type str
        """
        while not self.atEnd():
            self.readNext()
            if self.isEndElement() and self.name() == tag:
                break

            if self.isStartElement():
                if self.name() == listTag:
                    fileList = self.project.getProjectData(dataKey=dataKey)
                    fileList.append(
                        FileSystemUtilities.toNativeSeparators(self.readElementText())
                    )
                    self.project.setProjectData(
                        fileList, dataKey=dataKey, setDirty=False
                    )
                else:
                    self.raiseUnexpectedStartTag(self.name())

    def __readBasicDataField(self, tag, dataTag, dataKey):
        """
        Private method to read a list of files.

        @param tag name of the list tag
        @type str
        @param dataTag name of the data tag
        @type str
        @param dataKey key of the project data element
        @type str
        """
        while not self.atEnd():
            self.readNext()
            if self.isEndElement() and self.name() == tag:
                break

            if self.isStartElement():
                if self.name() == dataTag:
                    self.project.setProjectData(
                        self._readBasics(), dataKey=dataKey, setDirty=False
                    )
                else:
                    self.raiseUnexpectedStartTag(self.name())

    def __readVcs(self):
        """
        Private method to read the VCS info.
        """
        while not self.atEnd():
            self.readNext()
            if self.isEndElement() and self.name() == "Vcs":
                break

            if self.isStartElement():
                if self.name() == "VcsType":
                    self.project.setProjectData(
                        self.readElementText(), dataKey="VCS", setDirty=False
                    )
                elif self.name() == "VcsOptions":
                    self.project.setProjectData(
                        self._readBasics(), dataKey="VCSOPTIONS", setDirty=False
                    )
                elif self.name() == "VcsOtherData":
                    self.project.setProjectData(
                        self._readBasics(), dataKey="VCSOTHERDATA", setDirty=False
                    )
                else:
                    self.raiseUnexpectedStartTag(self.name())

    def __readFiletypeAssociations(self):
        """
        Private method to read the file type associations.
        """
        while not self.atEnd():
            self.readNext()
            if self.isEndElement() and self.name() == "FiletypeAssociations":
                break

            if self.isStartElement():
                if self.name() == "FiletypeAssociation":
                    pattern = self.attribute("pattern", "")
                    filetype = self.attribute("type", "OTHERS")
                    if pattern:
                        fileTypes = self.project.getProjectData(dataKey="FILETYPES")
                        fileTypes[pattern] = filetype
                        self.project.setProjectData(
                            fileTypes, dataKey="FILETYPES", setDirty=False
                        )
                else:
                    self.raiseUnexpectedStartTag(self.name())

    def __readLexerAssociations(self):
        """
        Private method to read the lexer associations.
        """
        while not self.atEnd():
            self.readNext()
            if self.isEndElement() and self.name() == "LexerAssociations":
                break

            if self.isStartElement():
                if self.name() == "LexerAssociation":
                    pattern = self.attribute("pattern", "")
                    lexer = self.attribute("lexer")
                    if pattern:
                        assocs = self.project.getProjectData(dataKey="LEXERASSOCS")
                        assocs[pattern] = lexer
                        self.project.setProjectData(
                            assocs, dataKey="LEXERASSOCS", setDirty=False
                        )
                else:
                    self.raiseUnexpectedStartTag(self.name())
