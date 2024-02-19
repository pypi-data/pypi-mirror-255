# -*- coding: utf-8 -*-

# Copyright (c) 2023 - 2024 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a proxy style to allow item selection by single/double click or
platform default.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QProxyStyle, QStyle

from eric7 import Preferences


class EricProxyStyle(QProxyStyle):
    """
    Class implementing a proxy style to allow item selection by single/double click or
    platform default.
    """

    def styleHint(self, hint, option=None, widget=None, returnData=None):
        """
        Public method returning a style hint for the given widget described by the
        provided style option.

        @param hint style hint to be determined
        @type QStyle.StyleHint
        @param option style option (defaults to None)
        @type QStyleOption (optional)
        @param widget reference to the widget (defaults to None)
        @type QWidget (optional)
        @param returnData data structure to return more data (defaults to None)
        @type QStyleHintReturn (optional)
        @return integer representing the style hint
        @rtype int
        """
        if hint == QStyle.StyleHint.SH_ItemView_ActivateItemOnSingleClick:
            # Activate item with a single click?
            activate = Preferences.getUI("ActivateItemOnSingleClick")
            if QApplication.keyboardModifiers() == Qt.KeyboardModifier.NoModifier:
                if activate == "singleclick":
                    return 1
                elif activate == "doubleclick":
                    return 0

        # return the default style hint
        return super().styleHint(
            hint, option=option, widget=widget, returnData=returnData
        )
