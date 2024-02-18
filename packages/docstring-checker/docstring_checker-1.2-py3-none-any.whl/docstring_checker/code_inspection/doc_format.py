# coding=utf-8
"""
This module contains the DocFormat class
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
from typing import Type
from .doc_format_enum import DocFormatEnum
from .docstring_tag_enum import DocstringTagEnum


# ==================================================================================================
# INITIALISATIONS
# ==================================================================================================

# ==================================================================================================
# CLASSES
# ==================================================================================================

# ======================
class DocFormat(object):
    """
    Instances of this class handle the different docstring formats and the matching tags

    Class attributes:
    :type FORMAT_ENUM: Type[DocFormatEnum]
    :cvar FORMAT_ENUM: the enum for the docsring formats

    :type TAG_ENUM: Type[DocstringTagEnum]
    :cvar TAG_ENUM: the enum for the docstring tags

    :type __formats_data: dict[DocFormatEnum, dict[DocstringTagEnum, str]]
    :cvar __formats_data: dictionnary linking a docstring format to a dictionnary linking a docstring tag to the matching str


    Instance attributes
    :type __doc_format: DocFormatEnum
    :ivar __doc_format: the current docstring format

    :type __tags_dict: dict[DocstringTagEnum, str]
    :ivar __tags_dict: dictionnary linking a docstring tag to the matching str for the current docstring format
    """
    FORMAT_ENUM = DocFormatEnum
    TAG_ENUM = DocstringTagEnum
    __formats_data = {DocFormatEnum.SPINX: {DocstringTagEnum.TYPE: ":type ",
                                            DocstringTagEnum.PARAM: ":param ",
                                            DocstringTagEnum.RTYPE: ":rtype:",
                                            DocstringTagEnum.RETURN: ":return:",
                                            DocstringTagEnum.IVAR: ":ivar ",
                                            DocstringTagEnum.CVAR: ":cvar "},
                      DocFormatEnum.EPYDOC: {DocstringTagEnum.TYPE: "@type ",
                                             DocstringTagEnum.PARAM: "@param ",
                                             DocstringTagEnum.RTYPE: "@rtype:",
                                             DocstringTagEnum.RETURN: "@return:",
                                             DocstringTagEnum.IVAR: "@ivar ",
                                             DocstringTagEnum.CVAR: "@cvar "}}

    # =============================
    def __init__(self, doc_format):
        """
        Initialization of a DocFormat instance

        :type doc_format: str | DocFormatEnum
        :param doc_format: the current docstring format
        """
        if isinstance(doc_format, str):
            try:
                doc_format = DocFormatEnum(doc_format)
            except ValueError:
                raise Exception("'%s' is not a valid doc format !" % doc_format)

        self.__doc_format = doc_format
        self.__tags_dict = self.__formats_data[doc_format]

    # =======================
    def get_doc_format(self):
        """
        This method is designed to get the current docstring format

        :rtype: DocFormatEnum
        :return: the current docstring format
        """
        return self.__doc_format

    # =====================
    def get_tag(self, tag):
        """
        This method is designed to get the str matching a docstring tag

        :type tag: str | DocstringTagEnum
        :param tag: the desired tag

        :rtype: str
        :return: the str matching the docstring tag
        """
        if isinstance(tag, str):
            try:
                tag = DocstringTagEnum(tag)
            except ValueError:
                raise Exception("'%s' is not a valid docstring tag !" % tag)

        return self.__tags_dict[tag]

    # =====================
    def get_type_tag(self):
        """
        This method is designed to get the str matching the 'type' docstring tag

        :rtype: str
        :return: the str matching the 'type' docstring tag
        """
        return self.get_tag(DocstringTagEnum.TYPE)

    # ======================
    def get_param_tag(self):
        """
        This method is designed to get the str matching the 'param' docstring tag

        :rtype: str
        :return: the str matching the 'param' docstring tag
        """
        return self.get_tag(DocstringTagEnum.PARAM)

    # ======================
    def get_rtype_tag(self):
        """
        This method is designed to get the str matching the 'rtype' docstring tag

        :rtype: str
        :return: the str matching the 'rtype' docstring tag
        """
        return self.get_tag(DocstringTagEnum.RTYPE)

    # =======================
    def get_return_tag(self):
        """
        This method is designed to get the str matching the 'return' docstring tag

        :rtype: str
        :return: the str matching the 'return' docstring tag
        """
        return self.get_tag(DocstringTagEnum.RETURN)

    # =====================
    def get_ivar_tag(self):
        """
        This method is designed to get the str matching the 'ivar' docstring tag

        :rtype: str
        :return: the str matching the 'ivar' docstring tag
        """
        return self.get_tag(DocstringTagEnum.IVAR)

    # =====================
    def get_cvar_tag(self):
        """
        This method is designed to get the str matching the 'cvar' docstring tag

        :rtype: str
        :return: the str matching the 'cvar' docstring tag
        """
        return self.get_tag(DocstringTagEnum.CVAR)


# ==================================================================================================
# FONCTIONS
# ==================================================================================================
