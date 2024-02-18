# coding=utf-8
"""
This module contains the MethodLoader class
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
class MethodLoader(BaseLoader):
    """
    This class is dedicated to load doc data from a method

    Instance attributes:
    :type __method_name: str
    :ivar __method_name: the name of the method

    :type __method: Callable
    :ivar __method: the inspected method

    :type __method_category: str
    :ivar __method_category: he tag indiating the type of docstring (ex : STATIC_METHODS, METHODS...)

    :type __method_node: NoneType | DocNode
    :ivar __method_node: the node containing the data of the method
    """
    # ==========
    @classmethod
    def get_loader_id(cls):
        """
        This method is designed to get the ID of the loader

        :rtype: str
        :return: the ID of the loader
        """
        return "METHOD"

    # =================================================================================
    def __init__(self, class_loader, class_node, method_name, method, method_category):
        """
        Initialization of a MethodLoader instance

        :type class_loader: docstring_checker.code_inspection.loaders.class_loader.ClassLoader
        :param class_loader: the parent loader

        :type class_node: DocNode
        :param class_node: the hierarchical node where data will be added

        :type method_name: str
        :param method_name: the name of the method in the class

        :type method: Callable
        :param method: the method

        :type method_category: str
        :param method_category: the tag indiating the type of docstring (ex : STATIC_METHODS, METHODS...)
        """
        super().__init__(class_node, parent_loader=class_loader)
        self.__method_name = method_name
        self.__method = method
        self.__method_category = method_category

        self.__method_node = None

    # =============
    def load(self):
        """
        This method is designed to perform data loading
        """
        try:
            cur_signature = inspect.signature(self.__method)
        except ValueError:
            pass
        else:
            self.__initialize_method_node(cur_signature)
            signature, source_code = self.__inspect_method()
            error_lines = self.__check_method_docstring(self.__method_node.get_docstring(), signature, source_code)
            self.__handle_errors(error_lines)

    # =====================================
    def __handle_errors(self, error_lines):
        """
        This method is designed to handle docstring errors

        :type error_lines: list[str]
        :param error_lines: the error lines
        """
        class_name = self.__get_class_name()

        if len(error_lines) != 0:
            test_line = self.__method_node.get_doc_header_line()
            if not self.__is_handled_exception(test_line):
                self.__write_error(test_line + "\n")
                self.__write_error("\n")
                for line in error_lines:
                    self.__write_error(line)
                    self.__write_error("\n")
                self.__write_error("\n")

                error_node = DocNode("ERRORS", self.__method_name, self.__method_node)
                error_node.set_data(self.__method_node.get_parent().get_doc_name(), class_name)
                error_node.set_data('MethodName', self.__method_name)

                str_to_add = '<div><p><span style="color:red;font-weight: bold">' + "\n<br>".join(error_lines) + "</span></p></div>"
                method_doc = self.__method_node.get_docstring() + str_to_add
                self.__method_node.set_docstring(method_doc)

    # ================================================
    def __initialize_method_node(self, cur_signature):
        """
        This method is designed to initialize the node of the method

        :type cur_signature: inspect.Signature
        :param cur_signature: the signature of the method
        """
        str_signature = str(cur_signature)
        if str_signature.endswith("typing.Type"):
            str_signature = "->".join(str_signature.split("->")[0:-1]).rstrip()

        method_node = DocNode(self.__method_category, self.__method_name, self.__get_parent_node())
        method_node.set_doc_name(self.__method_name)

        method_doc = self.__reformat_docstring(self.__method.__doc__)
        method_node.set_docstring(method_doc)

        method_node.set_signature(str_signature)

        self.__method_node = method_node

    # =========================
    def __inspect_method(self):
        """
        This method is designed to get the signature and source code of the method

        :rtype: (inspect.Signature, str)
        :return: the signature and the source code of the method
        """
        try:
            source = self.__method.__meta_wrapped__
        except Exception:
            source = self.__method

        source_code = inspect.getsource(source)
        signature = inspect.signature(source)

        return signature, source_code

    # =========================
    def __get_class_name(self):
        """
        This method is designed to get the name of the class possessing the method

        :rtype: str
        :return: the name of the class possessing the method
        """
        parent = self.__get_parent_loader()

        return parent.get_class_name()


# ==================================================================================================
# FONCTIONS
# ==================================================================================================
