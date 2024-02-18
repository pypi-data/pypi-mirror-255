# coding=utf-8
"""
This module contains the DocstringCheckerBaseException class
"""

# =============================================================================================== #
#  _____                 _        _                _____ _               _
# |  __ \               | |      (_)              / ____| |             | |
# | |  | | ___   ___ ___| |_ _ __ _ _ __   __ _  | |    | |__   ___  ___| | _____ _ __
# | |  | |/ _ \ / __/ __| __| '__| | '_ \ / _` | | |    | '_ \ / _ \/ __| |/ / _ \ '__|
# | |__| | (_) | (__\__ \ |_| |  | | | | | (_| | | |____| | | |  __/ (__|   <  __/ |
# |_____/ \___/ \___|___/\__|_|  |_|_| |_|\__, |  \_____|_| |_|\___|\___|_|\_\___|_|
#                                          __/ |
#                                         |___/
# =============================================================================================== #
from . import __author__, __email__, __version__, __maintainer__, __date__


# ==================================================================================================
# IMPORTS
# ==================================================================================================
import sys
import traceback


# ==================================================================================================
# INITIALISATIONS
# ==================================================================================================

# ==================================================================================================
# CLASSES
# ==================================================================================================

# =============================================
class DocstringCheckerBaseException(Exception):
    """
    This class defines the base exception for docstring_checker
    It is designed to format error message by adding a description of the error before its content

    Instance attributes:
    :type __descr: str
    :ivar __descr: description of the error
    """

    # ==========
    @classmethod
    def format_error_msg(cls):
        """
        This function is designed to format an exception that occured

        :rtype: str
        :return: The exception that occured into text
        """
        tb = sys.exc_info()
        tbinfo = traceback.format_tb(tb[2])
        msg = ''
        for elem in tbinfo:
            msg += str(elem)
        msg += str(tb[1])
        return msg

    # ================================
    def __init__(self, descr, msg=""):
        """
        Initialization of a DocstringCheckerBaseException instance

        :type descr: str
        :param descr: description of the error

        :type msg: str
        :param msg: Contextual error message. If not given, traceback is used
        """
        if msg == "":
            msg = self.format_error_msg()

        Exception.__init__(self, msg)
        self.__descr = descr

    # =================
    def __str__(self):
        """
        Overloaded __str__ method

        :rtype: str
        :return: The error message
        """
        res = "%s\n\t%s" % (self.__descr, self.args[0].replace("\n", "\n\t"))

        return res


# ==================================================================================================
# FONCTIONS
# ==================================================================================================


