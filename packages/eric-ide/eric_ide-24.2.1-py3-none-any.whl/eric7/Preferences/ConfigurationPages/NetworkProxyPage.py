# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2024 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Network configuration page.
"""

from PyQt6.QtCore import pyqtSlot

from eric7 import Preferences
from eric7.EricNetwork.EricFtp import EricFtpProxyType

from .ConfigurationPageBase import ConfigurationPageBase
from .Ui_NetworkProxyPage import Ui_NetworkProxyPage


class NetworkProxyPage(ConfigurationPageBase, Ui_NetworkProxyPage):
    """
    Class implementing the Network configuration page.
    """

    def __init__(self, configDialog):
        """
        Constructor

        @param configDialog reference to the configuration dialog
        @type ConfigurationDialog
        """
        super().__init__()
        self.setupUi(self)
        self.setObjectName("NetworkProxyPage")

        self.__configDlg = configDialog

        self.ftpProxyTypeCombo.addItem(
            self.tr("No FTP Proxy"), EricFtpProxyType.NO_PROXY.value
        )
        self.ftpProxyTypeCombo.addItem(
            self.tr("No Proxy Authentication required"),
            EricFtpProxyType.NON_AUTHORIZING.value,
        )
        self.ftpProxyTypeCombo.addItem(
            self.tr("User@Server"), EricFtpProxyType.USER_SERVER.value
        )
        self.ftpProxyTypeCombo.addItem(self.tr("SITE"), EricFtpProxyType.SITE.value)
        self.ftpProxyTypeCombo.addItem(self.tr("OPEN"), EricFtpProxyType.OPEN.value)
        self.ftpProxyTypeCombo.addItem(
            self.tr("User@Proxyuser@Server"),
            EricFtpProxyType.USER_PROXYUSER_SERVER.value,
        )
        self.ftpProxyTypeCombo.addItem(
            self.tr("Proxyuser@Server"), EricFtpProxyType.PROXYUSER_SERVER.value
        )
        self.ftpProxyTypeCombo.addItem(
            self.tr("AUTH and RESP"), EricFtpProxyType.AUTH_RESP.value
        )
        self.ftpProxyTypeCombo.addItem(
            self.tr("Bluecoat Proxy"), EricFtpProxyType.BLUECOAT.value
        )

        # set initial values

        # HTTP proxy
        self.httpProxyHostEdit.setText(Preferences.getUI("ProxyHost/Http"))
        self.httpProxyPortSpin.setValue(Preferences.getUI("ProxyPort/Http"))

        # HTTPS proxy
        self.httpsProxyHostEdit.setText(Preferences.getUI("ProxyHost/Https"))
        self.httpsProxyPortSpin.setValue(Preferences.getUI("ProxyPort/Https"))

        # FTP proxy
        self.ftpProxyHostEdit.setText(Preferences.getUI("ProxyHost/Ftp"))
        self.ftpProxyPortSpin.setValue(Preferences.getUI("ProxyPort/Ftp"))
        self.ftpProxyTypeCombo.setCurrentIndex(
            self.ftpProxyTypeCombo.findData(Preferences.getUI("ProxyType/Ftp").value)
        )
        self.ftpProxyUserEdit.setText(Preferences.getUI("ProxyUser/Ftp"))
        self.ftpProxyPasswordEdit.setText(Preferences.getUI("ProxyPassword/Ftp"))
        self.ftpProxyAccountEdit.setText(Preferences.getUI("ProxyAccount/Ftp"))

        self.httpProxyForAllCheckBox.setChecked(Preferences.getUI("UseHttpProxyForAll"))
        if not Preferences.getUI("UseProxy"):
            self.noProxyButton.setChecked(True)
        elif Preferences.getUI("UseSystemProxy"):
            self.systemProxyButton.setChecked(True)
        else:
            self.manualProxyButton.setChecked(True)

        self.exceptionsEdit.setText(
            ", ".join(Preferences.getUI("ProxyExceptions").split(","))
        )

    def save(self):
        """
        Public slot to save the Networj configuration.
        """
        Preferences.setUI("UseProxy", not self.noProxyButton.isChecked())
        Preferences.setUI("UseSystemProxy", self.systemProxyButton.isChecked())
        Preferences.setUI(
            "UseHttpProxyForAll", self.httpProxyForAllCheckBox.isChecked()
        )

        Preferences.setUI(
            "ProxyExceptions",
            ",".join([h.strip() for h in self.exceptionsEdit.text().split(",")]),
        )

        # HTTP proxy
        Preferences.setUI("ProxyHost/Http", self.httpProxyHostEdit.text())
        Preferences.setUI("ProxyPort/Http", self.httpProxyPortSpin.value())

        # HTTPS proxy
        Preferences.setUI("ProxyHost/Https", self.httpsProxyHostEdit.text())
        Preferences.setUI("ProxyPort/Https", self.httpsProxyPortSpin.value())

        # FTP proxy
        Preferences.setUI("ProxyHost/Ftp", self.ftpProxyHostEdit.text())
        Preferences.setUI("ProxyPort/Ftp", self.ftpProxyPortSpin.value())
        Preferences.setUI(
            "ProxyType/Ftp", EricFtpProxyType(self.ftpProxyTypeCombo.currentData())
        )
        Preferences.setUI("ProxyUser/Ftp", self.ftpProxyUserEdit.text())
        Preferences.setUI("ProxyPassword/Ftp", self.ftpProxyPasswordEdit.text())
        Preferences.setUI("ProxyAccount/Ftp", self.ftpProxyAccountEdit.text())

    @pyqtSlot()
    def on_clearProxyPasswordsButton_clicked(self):
        """
        Private slot to clear the saved HTTP(S) proxy passwords.
        """
        Preferences.setUI("ProxyPassword/Http", "")
        Preferences.setUI("ProxyPassword/Https", "")

    @pyqtSlot(int)
    def on_ftpProxyTypeCombo_currentIndexChanged(self, index):
        """
        Private slot handling the selection of a proxy type.

        @param index index of the selected item
        @type int
        """
        proxyType = EricFtpProxyType(self.ftpProxyTypeCombo.itemData(index))
        self.ftpProxyHostEdit.setEnabled(proxyType != EricFtpProxyType.NO_PROXY)
        self.ftpProxyPortSpin.setEnabled(proxyType != EricFtpProxyType.NO_PROXY)
        self.ftpProxyUserEdit.setEnabled(
            proxyType
            not in [EricFtpProxyType.NO_PROXY, EricFtpProxyType.NON_AUTHORIZING]
        )
        self.ftpProxyPasswordEdit.setEnabled(
            proxyType
            not in [EricFtpProxyType.NO_PROXY, EricFtpProxyType.NON_AUTHORIZING]
        )
        self.ftpProxyAccountEdit.setEnabled(
            proxyType
            not in [EricFtpProxyType.NO_PROXY, EricFtpProxyType.NON_AUTHORIZING]
        )


def create(dlg):
    """
    Module function to create the configuration page.

    @param dlg reference to the configuration dialog
    @type ConfigurationDialog
    @return reference to the instantiated page
    @rtype ConfigurationPageBase
    """
    page = NetworkProxyPage(dlg)
    return page
