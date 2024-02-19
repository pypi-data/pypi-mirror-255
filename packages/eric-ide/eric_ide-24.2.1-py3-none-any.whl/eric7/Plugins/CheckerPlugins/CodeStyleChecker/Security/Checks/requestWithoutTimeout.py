# -*- coding: utf-8 -*-

# Copyright (c) 2022 - 2024 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing checks for using requests without timeout.
"""

#
# This is a modified version of the one found in the bandit package.
#
# SPDX-License-Identifier: Apache-2.0
#


def getChecks():
    """
    Public method to get a dictionary with checks handled by this module.

    @return dictionary containing checker lists containing checker function and
        list of codes
    @rtype dict
    """
    return {
        "Call": [
            (checkRequestWithouTimeout, ("S114",)),
        ],
    }


def checkRequestWithouTimeout(reportError, context, config):  # noqa: U100
    """
    Function to check for use of requests without timeout.

    @param reportError function to be used to report errors
    @type func
    @param context security context object
    @type SecurityContext
    @param config dictionary with configuration data
    @type dict
    """
    httpVerbs = ("get", "options", "head", "post", "put", "patch", "delete")
    qualName = context.callFunctionNameQual.split(".")[0]
    if qualName == "requests" and context.callFunctionName in httpVerbs:
        # check for missing timeout
        if context.checkCallArgValue("timeout") is None:
            reportError(
                context.node.lineno - 1,
                context.node.col_offset,
                "S114.1",
                "M",
                "L",
            )

        # check for timeout=None
        if context.checkCallArgValue("timeout", "None"):
            reportError(
                context.node.lineno - 1,
                context.node.col_offset,
                "S114.2",
                "M",
                "L",
            )
