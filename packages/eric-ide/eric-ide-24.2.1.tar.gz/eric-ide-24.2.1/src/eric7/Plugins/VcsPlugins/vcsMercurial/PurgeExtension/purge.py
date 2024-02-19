# -*- coding: utf-8 -*-

# Copyright (c) 2011 - 2024 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the purge extension interface.
"""

from PyQt6.QtWidgets import QDialog

from eric7.UI.DeleteFilesConfirmationDialog import DeleteFilesConfirmationDialog

from ..HgDialog import HgDialog
from ..HgExtension import HgExtension


class Purge(HgExtension):
    """
    Class implementing the purge extension interface.
    """

    def __init__(self, vcs):
        """
        Constructor

        @param vcs reference to the Mercurial vcs object
        @type Hg
        """
        super().__init__(vcs)

        self.purgeListDialog = None

    def shutdown(self):
        """
        Public method used to shutdown the purge interface.
        """
        if self.purgeListDialog is not None:
            self.purgeListDialog.close()

    def __getEntries(self, deleteAll):
        """
        Private method to get a list of files/directories being purged.

        @param deleteAll flag indicating to delete all files including ignored
            ones
        @type bool
        @return name of the current patch
        @rtype str
        """
        purgeEntries = []

        args = self.vcs.initCommand("purge")
        args.append("--print")
        if deleteAll:
            args.append("--all")

        client = self.vcs.getClient()
        out, err = client.runcommand(args)
        if out:
            purgeEntries = out.strip().split()

        return purgeEntries

    def hgPurge(self, deleteAll=False):
        """
        Public method to purge files and directories not tracked by Mercurial.

        @param deleteAll flag indicating to delete all files including ignored
            ones
        @type bool
        """
        if deleteAll:
            title = self.tr("Purge All Files")
            message = self.tr(
                """Do really want to delete all files not tracked by"""
                """ Mercurial (including ignored ones)?"""
            )
        else:
            title = self.tr("Purge Files")
            message = self.tr(
                """Do really want to delete files not tracked by Mercurial?"""
            )
        entries = self.__getEntries(deleteAll)
        dlg = DeleteFilesConfirmationDialog(None, title, message, entries)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            args = self.vcs.initCommand("purge")
            if deleteAll:
                args.append("--all")
            args.append("-v")

            dia = HgDialog(title, self.vcs)
            res = dia.startProcess(args)
            if res:
                dia.exec()

    def hgPurgeList(self, deleteAll=False):
        """
        Public method to list files and directories not tracked by Mercurial.

        @param deleteAll flag indicating to list all files including ignored
            ones
        @type bool
        """
        from .HgPurgeListDialog import HgPurgeListDialog

        entries = self.__getEntries(deleteAll)
        self.purgeListDialog = HgPurgeListDialog(entries)
        self.purgeListDialog.show()
