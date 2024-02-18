# coding=utf-8
"""
This module contains the ClassLoader class
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
from typing import Callable, Generator
from enum import Enum
import inspect
from protected_method_metaclass import ProtectedMethodMetaClass
from docstring_checker.doc_node import DocNode
from ..base_loader import BaseLoader


# ==================================================================================================
# INITIALISATIONS
# ==================================================================================================

# ==================================================================================================
# CLASSES
# ==================================================================================================

# ============================
class ClassLoader(BaseLoader):
    """
    This class is dedicated to load doc data from a class

    Class attributes:
    :type __reserved_class_attribute: tuple[str]
    :cvar __reserved_class_attribute: tuple of class attributes that should be taken into account


    Instance attributes:
    :type __class: NoneType | Callable
    :ivar __class: the inspected class

    :type __class_name: str
    :ivar __class_name: the name of the class

    :type __class_prefix: str
    :ivar __class_prefix: the prefix for private attributes of the class

    :type __class_attributes: list[str]
    :ivar __class_attributes: list of names of the class attributes as found in the class

    :type __instance_attributes: set[str]
    :ivar __instance_attributes: set of names of the instance attributes as found in the __init__ method

    :type __lines_to_write: list[str]
    :ivar __lines_to_write: list of error lines ot write

    :type __class_node: NoneType | DocNode
    :ivar __class_node: the node containing the data of the class
    """
    __reserved_class_attribute = ("__orig_bases__", "__parameters__", "__annotations__")

    # ==========
    @classmethod
    def get_loader_id(cls):
        """
        This method is designed to get the ID of the loader

        :rtype: str
        :return: the ID of the loader
        """
        return "CLASS"

    # ====================================================================
    def __init__(self, module_loader, module_node, the_class, class_name):
        """
        Initialization of a ClassLoader instance

        :type module_loader: docstring_checker.code_inspection.loaders.module_loader.ModuleLoader
        :param module_loader: the parent loader

        :type module_node: DocNode
        :param module_node: the hierarchical node where data will be added

        :type class_name: str
        :param class_name: the name of the class

        :type the_class: type
        :param the_class: the class
        """
        super().__init__(module_node, parent_loader=module_loader)
        self.__class = the_class
        self.__class_name = class_name
        self.__class_prefix = self.__get_prefix(self.__class_name)
        self.__class_attributes = []
        self.__instance_attributes = set()
        self.__lines_to_write = []

        self.__class_node = None

    # =======================
    def get_class_name(self):
        """
        This method is designed to get the name of the class

        :rtype: str
        :return: the name of the class
        """
        return self.__class_name

    # =============
    def load(self):
        """
        This method is designed to perform data loading
        """
        self.__initialize_class_node()
        self.__update_from_class_members()
        self.__analyze_class_doc()
        self.__handle_lines_to_write()

    # ================================
    def __initialize_class_node(self):
        """
        This method is designed to initialize the node of the class
        """
        class_node = DocNode("CLASSES", self.__class_name, self.__get_parent_node())
        class_node.set_doc_name(self.__class_name)

        class_doc = self.__reformat_docstring(self.__class.__doc__)
        class_node.set_docstring(class_doc)

        self.__class_node = class_node

    # ====================================
    def __update_from_class_members(self):
        """
        This method is designed to update the class node from the content of the class
        """
        if not issubclass(self.__class, Enum):
            factory = self.get_factory()

            for item_name, test_item in self.__get_item_data_iterator():
                if item_name == "__init__":
                    self.__detect_attributes(test_item)

                true_item_name = self.__get_true_name(item_name, self.__class_prefix)
                ref_text = type(test_item).__name__
                if ref_text in ("function", "classmethod", "staticmethod"):
                    if ref_text != "function":
                        test_item = test_item.__func__

                    if callable(test_item):
                        method_type = ref_text
                        if method_type == "function":
                            method_type = "METHODS"
                        elif method_type == "classmethod":
                            method_type = "CLASS_METHODS"
                        else:  # staticmethod
                            method_type = "STATIC_METHODS"

                        sub_loader = factory.get_instance_from_id("METHOD", self, self.__class_node, true_item_name, test_item, method_type)
                        sub_loader.load()
                    else:
                        self.__update_problematic_types(self.__class, self.__class_name, true_item_name, test_item)

                elif ref_text == "property":
                    sub_loader = factory.get_instance_from_id("PROPERTY", self, self.__class_node, true_item_name, test_item)
                    sub_loader.load()

                elif item_name not in ['__doc__', '__module__', '__dict__', '__weakref__', "__hash__"]:
                    if (true_item_name != "__protected_methods") or (not isinstance(self.__class, ProtectedMethodMetaClass)):
                        self.__class_attributes.append(item_name)

    # ============================
    def __analyze_class_doc(self):
        """
        This method is designed to check the doc of the class
        """
        class_doc = self.__class_node.get_docstring()
        if class_doc is None or class_doc == "":
            self.__lines_to_write.append("no docstring!")

        elif not issubclass(self.__class, Enum):
            self.__check_class_attributes()
            self.__check_instance_attributes()
            self.__check_xxx()

    # =================================
    def __check_class_attributes(self):
        """
        This method is desigend to check that the doc of the class matches the class attributes
        """
        class_doc = self.__class_node.get_docstring()
        base_test_line = self.__class_node.get_doc_header_line()
        for class_attribute_name in self.__class_attributes:
            true_class_attribute = self.__get_true_name(class_attribute_name, self.__class_prefix)
            test_line = "%s.%s" % (base_test_line, true_class_attribute)
            if (not self.__is_handled_exception(test_line)) and (true_class_attribute not in self.__reserved_class_attribute):
                if class_doc.find('type %s:' % true_class_attribute) == -1:
                    self.__lines_to_write.append("missing class attribute %s in class doc !" % true_class_attribute)
                elif class_doc.find('cvar %s:' % true_class_attribute) == -1:
                    self.__lines_to_write.append("missing class attribute %s in class doc !" % true_class_attribute)

    # ====================================
    def __check_instance_attributes(self):
        """
        This method is desigend to check that the doc of the class matches the isntance attributes
        """
        class_doc = self.__class_node.get_docstring()
        base_test_line = self.__class_node.get_doc_header_line()

        for detected_attribute in self.__instance_attributes:
            true_instance_attribute = self.__get_true_name(detected_attribute, self.__class_prefix)
            test_line = "%s.%s" % (base_test_line, true_instance_attribute)
            if not self.__is_handled_exception(test_line):
                if class_doc.find('type %s:' % true_instance_attribute) == -1:
                    self.__lines_to_write.append("missing instance attribute %s in class doc !" % true_instance_attribute)
                elif class_doc.find('ivar %s:' % true_instance_attribute) == -1:
                    self.__lines_to_write.append("missing instance attribute %s in class doc !" % true_instance_attribute)

    # ====================
    def __check_xxx(self):
        """
        This method is designed to check that the doc of the class does not content XXX or ???
        """
        class_doc = self.__class_node.get_docstring()

        if not self.__is_handled_exception(self.__class_node.get_doc_header_line()):
            if class_doc.find("XXX") != -1 or class_doc.find("???") != -1:
                self.__lines_to_write.append("'XXX' or '???' present in class doc !")

    # ================================
    def __handle_lines_to_write(self):
        """
        This method is designed to handle lines of errors
        """
        if len(self.__lines_to_write) != 0:
            class_doc = self.__class_node.get_docstring()
            self.__write_error(self.__class_node.get_doc_header_line() + "\n")
            for line in self.__lines_to_write:
                self.__write_error(line)
                self.__write_error("\n")
            str_to_add = '<div><p><span style="color:red;font-weight: bold">' + "\n<br>".join(self.__lines_to_write) + "</span></p></div>"
            class_doc += str_to_add
            error_node = DocNode("ERRORS", self.__class_name, self.__class_node)
            error_node.set_data(self.__class_node.get_doc_name(), self.__class_name)

            self.__class_node.set_docstring(class_doc)

    # =================================
    def __get_item_data_iterator(self):
        """
        This method is designed to get an iterator over the content of the class

        :rtype: Generator[(str, any)]
        :return: an iterator over the content of the class (name and item)
        """
        test_name = self.__class_prefix + "__old_classdict_keys"
        if test_name in self.__class.__dict__:
            item_names = sorted(self.__class.__dict__[test_name])
        else:
            item_names = sorted(self.__class.__dict__.keys())

        for item_name in item_names:
            try:
                test_item = self.__class.__dict__[item_name]
            except KeyError:
                pass
            else:
                yield item_name, test_item

    # =========================================
    def __detect_attributes(self, init_method):
        """
        This function is designed to detect instance attributes by reading the content of the __init__ method

        :type init_method: Callable
        :param init_method: the __init__ method
        """
        detected_attributes = set()
        try:
            meta_wrapped = init_method.__meta_wrapped__
        except Exception:
            source_code = inspect.getsource(init_method)
        else:
            source_code = inspect.getsource(meta_wrapped)
        lines = source_code.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('self.'):
                line = line[5:]
                splits = line.split('=')
                if len(splits) > 1:
                    test_name = splits[0].replace(' ', '').replace('\t', '')
                    if test_name.replace('_', '').isalnum():
                        detected_attributes.add(test_name)

        self.__instance_attributes = detected_attributes


# ==================================================================================================
# FONCTIONS
# ==================================================================================================
