# -*- coding: utf-8 -*-

# Copyright (c) 2019 - 2024 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing some helpers for Google mail.
"""

import os

from eric7 import Globals
from eric7.EricWidgets.EricApplication import ericApp
from eric7.SystemUtilities import PythonUtilities

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
CLIENT_SECRET_FILE = "eric_client_secret.json"  # secok
TOKEN_FILE = "eric_python_email_send_token.json"  # secok
APPLICATION_NAME = "Eric Python Send Email"

RequiredPackages = (
    "google-api-python-client",
    "google-auth-httplib2",
    "google-auth-oauthlib",
)


def isClientSecretFileAvailable():
    """
    Module function to check, if the client secret file has been installed.

    @return flag indicating, that the credentials file is there
    @rtype bool
    """
    return os.path.exists(os.path.join(Globals.getConfigDir(), CLIENT_SECRET_FILE))


def installGoogleAPIPackages():
    """
    Module function to install the required packages to support Google mail.
    """
    pip = ericApp().getObject("Pip")
    pip.installPackages(
        RequiredPackages, interpreter=PythonUtilities.getPythonExecutable()
    )


#
# eflag: noqa = U200
