# coding=utf-8
"""
This module contains the BaseModuleLoader class
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
import os
from docstring_checker.doc_node import DocNode
from ..base_loader import BaseLoader, Protected


# ==================================================================================================
# INITIALISATIONS
# ==================================================================================================

# ==================================================================================================
# CLASSES
# ==================================================================================================

# =================================
class BaseModuleLoader(BaseLoader):
    """
    This class is the base class for module loaders

    Instance attributes:
    :type __write_error_function: (str) -> NoneType
    :ivar __write_error_function: function to write a docstring error

    :type __is_handled_exception_function: (str) -> bool
    :ivar __is_handled_exception_function: function to check if an error is handled and thus has to be ignored

    :type __update_problematic_types_function: (str, str, str, str) -> NoneType
    :ivar __update_problematic_types_function: function to update the detected problematic types

    :type __get_doc_format_function: () -> docstring_checker.code_inspection.doc_format.DocFormat
    :ivar __get_doc_format_function: function to get the DocFormat instance

    :type __module_node: NoneType | DocNode
    :ivar __module_node: the node containing the data of the module
    """

    # ==========
    @classmethod
    def get_loader_id(cls):
        """
        This method is designed to get the ID of the loader

        :rtype: str
        :return: the ID of the loader
        """
        return "BASE MODULE"

    # ===================================================================================================================
    def __init__(self, root_node, write_error_function, is_handled_exception_function, update_problematic_types_function,
                 get_doc_format_function):
        """
        Initialization of a BaseModuleLoader instance

        :type root_node: DocNode
        :param root_node: the root node of the project

        :type write_error_function: (str) -> NoneType
        :param write_error_function: function to write a docstring error

        :type is_handled_exception_function: (str) -> bool
        :param is_handled_exception_function: function to check if an error is handled and thus has to be ignored

        :type update_problematic_types_function: (str, str, str, str) -> NoneType
        :param update_problematic_types_function: function to update the detected problematic types

        :type get_doc_format_function: () -> docstring_checker.code_inspection.doc_format.DocFormat
        :param get_doc_format_function: function to get the DocFormat instance
        """
        # TODO : deporter l'utilisation de modules_to_avoid au dessus
        super().__init__(root_node)
        self.__write_error_function = write_error_function
        self.__is_handled_exception_function = is_handled_exception_function
        self.__update_problematic_types_function = update_problematic_types_function
        self.__get_doc_format_function = get_doc_format_function

        self.__module_node = None

    # ========================
    def get_module_name(self):
        """
        This method is designed to get the name of the module

        :rtype: str
        :return: the name of the module
        """
        raise NotImplementedError("The method '' is not overloaded for class %s !" % str(self.__class__))

    # ========
    @Protected
    def __get_module_node(self):
        """
        This method is designed to get the node containing the data of the module

        :rtype: NoneType | DocNode
        :return: the node containing the data of the module
        """
        return self.__module_node

    # ========
    @Protected
    def __set_module_node(self, value):
        """
        This method is designed to update the node containing the data of the module

        :type value: NoneType | DocNode
        :param value: the node containing the data of the module
        """
        self.__module_node = value

    # ========
    @Protected
    def __add_to_known_in_module(self, name, test_item):
        """
        This method is designed to add an item of the module as known by this module within the node of the module

        :type name: str
        :param name: the name of the item as known in the module

        :type test_item: any
        :param test_item: the item with the given name in the module
        """
        source_module_import_path = ""
        item_name = ""
        try:
            source_module_import_path = test_item.__module__
        except Exception:
            if test_item.__class__.__name__ == "module":
                source_module_import_path = test_item.__name__
                if source_module_import_path == test_item.__package__:
                    item_name = "__init__"
        else:
            try:
                item_name = test_item.__name__
            except Exception:
                if source_module_import_path == "typing":
                    item_name = name
                else:
                    source_module_import_path = ""

        if source_module_import_path != "":
            known_in_module = self.__module_node.get_data("KnownInModule")
            known_in_module[name] = (source_module_import_path, item_name)

    # ========
    @Protected
    def __write_error(self, data):
        """
        This method is designed to write an error

        :type data: str
        :param data: the data to write in the error file
        """
        self.__write_error_function(data)

    # ========
    @Protected
    def __is_handled_exception(self, exception_header):
        """
        This method is designed to check if an error is handled and thus has to be ignored

        :type exception_header: str
        :param exception_header: header of an error in the error file

        :rtype: bool
        :return: True if the error is handled, False otherwise.
        """
        return self.__is_handled_exception_function(exception_header)

    # ========
    @Protected
    def __update_problematic_types(self, cur_class, class_name, item_name, test_item):
        """
        This method is designed to update the detected problematic types

        :type cur_class: type
        :param cur_class: the class causing problem

        :type class_name: str
        :param class_name: name of the class

        :type item_name: str
        :param item_name: the name of the item in the class

        :type test_item: any
        :param test_item: the item of the class causing problem
        """
        bases = [base_name.__name__ for base_name in cur_class.__bases__]
        if item_name not in ['__dict__', '__weakref__'] and 'type' not in bases:
            pb_type = type(test_item).__name__
            if pb_type not in ('str', 'dict', 'list'):
                self.__update_problematic_types_function(pb_type, self.get_module_name(), class_name, item_name)

    # ========
    @Protected
    def __get_doc_format_function(self):
        """
        This method is designed to get the DocFormat instance

        :rtype: docstring_checker.code_inspection.doc_format.DocFormat
        :return: the DocFormat instance
        """
        return self.__get_doc_format_function()


# ==================================================================================================
# FONCTIONS
# ==================================================================================================
