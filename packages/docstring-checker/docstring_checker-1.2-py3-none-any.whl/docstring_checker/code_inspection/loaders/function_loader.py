# coding=utf-8
"""
This module contains the FunctionLoader class
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
from typing import Callable
import inspect
from docstring_checker.doc_node import DocNode
from ..base_loader import BaseLoader


# ==================================================================================================
# INITIALISATIONS
# ==================================================================================================

# ==================================================================================================
# CLASSES
# ==================================================================================================


# =============================
class FunctionLoader(BaseLoader):
    """
    This class is dedicated to load doc data from a function

    Instance attributes:
    :type __function_name: str
    :ivar __function_name: the name of the function

    :type __function: Callable
    :ivar __function: the inspected function

    :type __function_node: NoneType | DocNode
    :ivar __function_node: the node containing the data of the function
    """
    # ==========
    @classmethod
    def get_loader_id(cls):
        """
        This method is designed to get the ID of the loader

        :rtype: str
        :return: the ID of the loader
        """
        return "FUNCTION"

    # ======================================================================
    def __init__(self, module_loader, module_node, function_name, function):
        """
        Initialization of a FunctionLoader instance

        :type module_loader: docstring_checker.code_inspection.loaders.module_loader.ModuleLoader
        :param module_loader: the parent loader

        :type module_node: DocNode
        :param module_node: the hierarchical node where data will be added

        :type function_name: str
        :param function_name: the name of the function

        :type function: Callable
        :param function: the function
        """
        super().__init__(module_node, parent_loader=module_loader)

        self.__function_name = function_name
        self.__function = function

        self.__function_node = None

    # =============
    def load(self):
        """
        This method is designed to perform data loading
        """
        try:
            cur_signature = inspect.signature(self.__function)
        except ValueError:
            pass
        else:
            self.__initialize_function_node(cur_signature)
            signature, source_code = self.__inspect_function()
            error_lines = self.__check_method_docstring(self.__function_node.get_docstring(), signature, source_code)
            self.__handle_errors(error_lines)

    # =====================================
    def __handle_errors(self, error_lines):
        """
        This method is designed to handle docstring errors

        :type error_lines: list[str]
        :param error_lines: the error lines
        """
        if len(error_lines) != 0:
            test_line = self.__function_node.get_doc_header_line()
            if not self.__is_handled_exception(test_line):
                self.__write_error(test_line + "\n")
                self.__write_error("\n")
                for line in error_lines:
                    self.__write_error(line)
                    self.__write_error("\n")
                self.__write_error("\n")

                error_node = DocNode("ERRORS", self.__function_name, self.__function_node)
                error_node.set_data(self.__function_node.get_doc_name(), self.__function_name)

                str_to_add = '<div><p><span style="color:red;font-weight: bold">' + "\n<br>".join(error_lines) + "</span></p></div>"
                function_doc = self.__function_node.get_docstring() + str_to_add
                self.__function_node.set_docstring(function_doc)

    # ==================================================
    def __initialize_function_node(self, cur_signature):
        """
        This method is designed to initialize the node of the function

        :type cur_signature: inspect.Signature
        :param cur_signature: the signature of the function
        """
        str_signature = str(cur_signature)
        if str_signature.endswith("typing.Type"):
            str_signature = "->".join(str_signature.split("->")[0:-1]).rstrip()

        function_node = DocNode("FUNCTIONS", self.__function_name, self.__get_parent_node())
        function_node.set_doc_name(self.__function_name)

        function_doc = self.__reformat_docstring(self.__function.__doc__)
        function_node.set_docstring(function_doc)

        function_node.set_signature(str_signature)

        self.__function_node = function_node

    # ===========================
    def __inspect_function(self):
        """
        This method is designed to get the signature and source code of the function

        :rtype: (inspect.Signature, str)
        :return: the signature and the source code of the function
        """
        try:
            source = self.__function.__meta_wrapped__
        except Exception:
            source = self.__function

        source_code = inspect.getsource(source)
        signature = inspect.signature(source)

        return signature, source_code


# ==================================================================================================
# FONCTIONS
# ==================================================================================================
