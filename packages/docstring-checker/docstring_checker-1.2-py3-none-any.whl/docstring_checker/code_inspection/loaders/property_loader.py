# coding=utf-8
"""
This module contains the PropertyLoader class
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
from ..base_loader import BaseLoader
from docstring_checker.doc_node import DocNode


# ==================================================================================================
# INITIALISATIONS
# ==================================================================================================

# ==================================================================================================
# CLASSES
# ==================================================================================================

# ===============================
class PropertyLoader(BaseLoader):
    """
    This class is dedicated to load doc data from a property

    Instance attributes:
    :type __property_name: str
    :ivar __property_name: the name of the property in the class

    :type __get_method: NoneType | Callable
    :ivar __get_method: the get method of the property

    :type __set_method: NoneType | Callable
    :ivar __set_method: the set method of the property
    """

    # ==========
    @classmethod
    def get_loader_id(cls):
        """
        This method is designed to get the ID of the loader

        :rtype: str
        :return: the ID of the loader
        """
        return "PROPERTY"

    # =======================================================================
    def __init__(self, class_loader, class_node, property_name, the_property):
        """
        Initialization of a PropertyLoader instance

        :type class_loader: docstring_checker.code_inspection.loaders.class_loader.ClassLoader
        :param class_loader: the parent loader

        :type class_node: DocNode
        :param class_node: the hierarchical node where data will be added

        :type property_name: str
        :param property_name: the name of the property in the class

        :type the_property: property
        :param the_property: the property
        """
        super().__init__(class_node, parent_loader=class_loader)
        self.__property_name = property_name
        self.__get_method = the_property.fget
        self.__set_method = the_property.fset

    # =============
    def load(self):
        """
        This method is designed to perform data loading
        """
        if self.__get_method is not None:
            self.__load_get()

        if self.__set_method is not None:
            self.__load_set()

    # ===================
    def __load_get(self):
        """
        This method is designed to perform data loading for the getter of the property
        """
        factory = self.get_factory()
        prefix = DocNode.get_property_getter_prefix()
        sub_loader = factory.get_instance_from_id("METHOD", self, self.__get_parent_node(), prefix + self.__property_name,
                                                  self.__get_method, "METHODS")
        sub_loader.load()

    # ===================
    def __load_set(self):
        """
        This method is designed to perform data loading for the setter of the property
        """
        factory = self.get_factory()
        prefix = DocNode.get_property_setter_prefix()
        sub_loader = factory.get_instance_from_id("METHOD", self, self.__get_parent_node(), prefix + self.__property_name,
                                                  self.__set_method, "METHODS")
        sub_loader.load()


# ==================================================================================================
# FONCTIONS
# ==================================================================================================
