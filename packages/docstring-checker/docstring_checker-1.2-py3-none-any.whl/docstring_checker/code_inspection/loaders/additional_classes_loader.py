# coding=utf-8
"""
This module contains the AdditionalClassesLoader class
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
from typing import Iterable
from docstring_checker.doc_node import DocNode
from .base_module_loader import BaseModuleLoader


# ==================================================================================================
# INITIALISATIONS
# ==================================================================================================

# ==================================================================================================
# CLASSES
# ==================================================================================================


# ==============================================
class AdditionalClassesLoader(BaseModuleLoader):
    """
    This class is dedicated to load doc data from a module

    Instance attributes:
    :type __additional_classes: Iterable[type]
    :ivar __additional_classes: list of additional classes
    """

    # ==========
    @classmethod
    def get_loader_id(cls):
        """
        This method is designed to get the ID of the loader

        :rtype: str
        :return: the ID of the loader
        """
        return "MODULE"

    # ====================================================================================================
    def __init__(self, root_node, additional_classes, write_error_function, is_handled_exception_function,
                 update_problematic_types_function, get_doc_format_function):
        """
        Initialization of a ModuleLoader instance

        :type root_node: DocNode
        :param root_node: the root node of the project

        :type additional_classes: Iterable[type]
        :param additional_classes: list of additional classes

        :type write_error_function: (str) -> NoneType
        :param write_error_function: function to write a docstring error

        :type is_handled_exception_function: (str) -> bool
        :param is_handled_exception_function: function to check if an error is handled and thus has to be ignored

        :type update_problematic_types_function: (str, str, str, str) -> NoneType
        :param update_problematic_types_function: function to update the detected problematic types

        :type get_doc_format_function: () -> docstring_checker.code_inspection.doc_format.DocFormat
        :param get_doc_format_function: function to get the DocFormat instance
        """
        super().__init__(root_node, write_error_function, is_handled_exception_function, update_problematic_types_function,
                         get_doc_format_function)

        self.__additional_classes = additional_classes

    # ========================
    def get_module_name(self):
        """
        This method is designed to get the name of the module

        :rtype: str
        :return: the name of the module
        """
        return "additional_classes"

    # =============
    def load(self):
        """
        This method is designed to perform data loading
        """
        self.__initialize_module_node()
        self.__update_module_node()

    # =================================
    def __initialize_module_node(self):
        """
        This method is designed to initialize the node of the module
        """
        known_in_module = {}
        module_name = self.get_module_name()
        module_node = DocNode("MODULES", module_name, self.__get_parent_node())
        module_node.set_doc_name(module_name)

        module_node.set_data("ModulePath", module_name)
        module_node.set_data("ModuleImportPath", module_name)
        module_node.set_data("KnownInModule", known_in_module)

        self.__set_module_node(module_node)

    # =============================
    def __update_module_node(self):
        """
        This method is designed to update the node of the module with the content of the module
        """
        factory = self.get_factory()
        module_node = self.__get_module_node()
        for additional_class in sorted(self.__additional_classes, key=lambda x: x.__name__):
            name = additional_class.__name__
            self.__add_to_known_in_module(name, additional_class)
            sub_loader = factory.get_instance_from_id("CLASS", self, module_node, additional_class, name)
            sub_loader.load()

    # ==================================================
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
            known_in_module = self.__get_module_node().get_data("KnownInModule")
            known_in_module[name] = (source_module_import_path, item_name)



# ==================================================================================================
# FONCTIONS
# ==================================================================================================
