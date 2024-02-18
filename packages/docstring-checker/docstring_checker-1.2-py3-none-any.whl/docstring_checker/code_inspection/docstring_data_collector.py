# coding=utf-8
"""
This module contains the DocstringDataCollector class
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
from typing import Iterable, TextIO
import os
from glob import iglob
from .loaders.module_loader import ModuleLoader
from .loaders.additional_classes_loader import AdditionalClassesLoader
from docstring_checker.doc_node import DocNode


# ==================================================================================================
# INITIALISATIONS
# ==================================================================================================

# ==================================================================================================
# CLASSES
# ==================================================================================================

# ===================================
class DocstringDataCollector(object):
    """
    This class is designed to collect the docstring data of a project within a DocNode instance

    Instance attributes
    :type __root_node: DocNode
    :ivar __root_node: the root node of the project containing the gathered data

    :type __source_directories: Iterable[str]
    :ivar __source_directories: list of directories of the libraries to check

    :type __modules_to_avoid: list[str]
    :ivar __modules_to_avoid: list of modules not to analyze

    :type __additional_classes: list[type]
    :ivar __additional_classes: list of additional classes to analyses (usually built with metaclass)

    :type __doc_format: docstring_checker.code_inspection.doc_format.DocFormat
    :ivar __doc_format: the DocFormat instance

    :type __error_file: NoneType | TextIO
    :ivar __error_file: the error file to write

    :type __is_handled_exception: (str) -> bool
    :ivar __is_handled_exception: function to check if an error is handled from its header in error file

    :type __problematic_types: dict[str, list[(str, str, str)]]
    :ivar __problematic_types: dictionnary linking the name of a problematic type to :
                                 - the name of the module
                                 - the name of the class
                                 - the name of the member of the class
                               causing the problem
    """
    # ===================================================================================================================================
    def __init__(self, project_name, source_directories, modules_to_avoid, additional_classes, doc_format, is_handled_exception,
                 errors_filepath=""):
        """
        Initialization of a DocstringDataCollector instance

        :type project_name: str
        :param project_name: the name of the project

        :type source_directories: Iterable[str]
        :param source_directories: list of directories of the libraries to check

        :type modules_to_avoid: list[str]
        :param modules_to_avoid: list of modules not to analyze

        :type additional_classes: list[type]
        :param additional_classes: list of additional classes to analyses (usually built with metaclass)

        :type doc_format: docstring_checker.code_inspection.doc_format.DocFormat
        :param doc_format: the DocFormat instance

        :type errors_filepath: str
        :param errors_filepath: the path to the error file ("" if no error file to write)

        :type is_handled_exception: (str) -> bool
        :param is_handled_exception: function to check if an error is handled from its header in error file
        """
        if os.path.isdir(os.path.dirname(errors_filepath)):
            error_file = open(errors_filepath, mode="w", encoding="utf-8")
        else:
            error_file = None

        self.__root_node = DocNode("root_node", project_name)
        self.__root_node.set_doc_name(project_name)
        self.__source_directories = source_directories
        self.__modules_to_avoid = modules_to_avoid
        self.__additional_classes = additional_classes
        self.__doc_format = doc_format
        self.__error_file = error_file
        self.__problematic_types = {}

        self.__is_handled_exception = is_handled_exception
        self.__initialize_root_node()

    # ======================
    def get_root_node(self):
        """
        This method is designed to get the root node of the project containing the gathered data

        :rtype: DocNode
        :return: the root node of the project containing the gathered data
        """
        return self.__root_node

    # =======================
    def get_doc_format(self):
        """
        This method is designed to get the DocFormat instance

        :rtype: docstring_checker.code_inspection.doc_format.DocFormat
        :return: the DocFormat instance
        """
        return self.__doc_format

    # =====================
    def collect_data(self):
        """
        This method is designed to collect the data of the project

        :rtype: DocNode
        :return: the data of the project
        """
        self.__load_modules()
        self.__load_additionnal_classes()

        if self.__error_file is not None:
            self.__error_file.flush()
            self.__error_file.close()

        return self.__root_node

    # =======================
    def __load_modules(self):
        """
        This method is designed to load the data of the modules
        """
        for source_dir in self.__source_directories:
            for module_path in iglob(source_dir + os.sep + "**" + os.sep + "*.py", recursive=True):
                dir_path0 = os.path.dirname(source_dir)
                module_loader = ModuleLoader(self.__root_node, module_path, dir_path0, self.__modules_to_avoid, self.__write_error,
                                             self.__is_handled_exception, self.__update_problematic_types, self.get_doc_format)
                module_loader.load()

    # ===================================
    def __load_additionnal_classes(self):
        """
        This method is designed to load the data of the additional classes
        """
        module_loader = AdditionalClassesLoader(self.__root_node, self.__additional_classes, self.__write_error,
                                                self.__is_handled_exception, self.__update_problematic_types, self.get_doc_format)
        module_loader.load()

    # ===============================
    def __initialize_root_node(self):
        """
        This method is designed to initialize the root node of the project
        """
        root_names = []
        for source_dir in self.__source_directories:
            root_names.append(os.path.basename(source_dir))

        self.__root_node.set_data("RootNames", root_names)

    # ============================
    def __write_error(self, data):
        """
        This method is designed to write an error if possible

        :type data: str
        :param data: the data to write in the error file
        """
        if self.__error_file is not None:
            self.__error_file.write(data)

    # ================================================================================
    def __update_problematic_types(self, pb_type, module_name, class_name, item_name):
        """
        This method is designed to update the problematic types

        :type pb_type: str
        :param pb_type: the name of the problematic type

        :type module_name: str
        :param module_name: the name of the module where the problem in encountred

        :type class_name: str
        :param class_name:the name of the class where the problem in encountred

        :type item_name: str
        :param item_name: the name of the member of the class causing the problem
        """
        data_list = self.__problematic_types.setdefault(pb_type, [])
        data_list.append((module_name, class_name, item_name))


# ==================================================================================================
# FONCTIONS
# ==================================================================================================
