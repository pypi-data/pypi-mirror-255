# coding=utf-8
"""
This module contains the ModuleLoader class
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
from .base_module_loader import BaseModuleLoader


# ==================================================================================================
# INITIALISATIONS
# ==================================================================================================

# ==================================================================================================
# CLASSES
# ==================================================================================================

# ===================================
class ModuleLoader(BaseModuleLoader):
    """
    This class is dedicated to load doc data from a module

    Instance attributes:
    :type __modules_to_avoid: list[str]
    :ivar __modules_to_avoid: liste of modules not to analyze

    :type __module_rel_path: str
    :ivar __module_rel_path: relative path to the inspected module

    :type __module_import_path: str
    :ivar __module_import_path: import path to the module

    :type __module_name: str
    :ivar __module_name: the name of the module

    :type __module_prefix: str
    :ivar __module_prefix: the prefix for private attributes of the module

    :type __module: NoneType | module
    :ivar __module: the inspected module

    :type __lines_to_write: list[str]
    :ivar __lines_to_write: list of error lines ot write
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

    # ===========================================================================================================================
    def __init__(self, root_node, module_path, dir_path0, modules_to_avoid, write_error_function, is_handled_exception_function,
                 update_problematic_types_function, get_doc_format_function):
        """
        Initialization of a ModuleLoader instance

        :type root_node: DocNode
        :param root_node: the root node of the project

        :type module_path: str
        :param module_path: the path to the inspected module file

        :type dir_path0: str
        :param dir_path0: the path to the directory containing the inspected library

        :type modules_to_avoid: list[str]
        :param modules_to_avoid: liste of modules not to analyze

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
        super().__init__(root_node, write_error_function, is_handled_exception_function, update_problematic_types_function,
                         get_doc_format_function)

        self.__modules_to_avoid = modules_to_avoid
        self.__module_rel_path = os.path.splitext(os.path.relpath(module_path, dir_path0))[0]
        self.__module_import_path = self.__module_rel_path.replace(os.sep, '.')
        self.__module_name = os.path.basename(self.__module_rel_path)
        self.__module_prefix = self.__get_prefix(self.__module_name)
        self.__lines_to_write = []

        self.__module = None

    # ========================
    def get_module_name(self):
        """
        This method is designed to get the name of the module

        :rtype: str
        :return: the name of the module
        """
        return self.__module_name

    # =============
    def load(self):
        """
        This method is designed to perform data loading
        """
        if self.__module_name not in self.__modules_to_avoid:
            self.__load_module()
            self.__initialize_module_node()
            self.__update_module_node()
            self.__analyze_module_doc()
            self.__handle_lines_to_write()

    # =================================
    def __initialize_module_node(self):
        """
        This method is designed to initialize the node of the module
        """
        known_in_module = {}
        module_node = DocNode("MODULES", self.__module_rel_path, self.__get_parent_node())
        module_node.set_doc_name(self.__module_name)

        module_node.set_data("ModulePath", self.__module_rel_path)
        module_node.set_data("ModuleImportPath", self.__module_import_path)
        module_node.set_data("KnownInModule", known_in_module)

        module_doc = self.__reformat_docstring(self.__module.__doc__)
        module_node.set_docstring(module_doc)

        self.__set_module_node(module_node)

    # =============================
    def __update_module_node(self):
        """
        This method is designed to update the node of the module with the content of the module
        """
        factory = self.get_factory()
        module_node = self.__get_module_node()
        for name in sorted(self.__module.__dict__.keys()):
            test_item = self.__module.__dict__[name]
            self.__add_to_known_in_module(name, test_item)

            if isinstance(test_item, type):
                test_class_module = self.__module.__dict__[name].__module__
                if self.__module_import_path == test_class_module:
                    sub_loader = factory.get_instance_from_id("CLASS", self, module_node, test_item, name)
                    sub_loader.load()

            elif type(test_item).__name__ == "function" and callable(test_item):
                test_function_module = test_item.__module__
                if self.__module_import_path == test_function_module:
                    true_function_name = self.__get_true_name(name, self.__module_prefix)
                    sub_loader = factory.get_instance_from_id("FUNCTION", self, module_node, true_function_name, test_item)
                    sub_loader.load()

    # ============================
    def __analyze_module_doc(self):
        """
        This method is designed to check the doc of the module
        """
        module_doc = self.__get_module_node().get_docstring()
        if module_doc is None or module_doc == "":
            self.__lines_to_write.append("no docstring!")

    # ================================
    def __handle_lines_to_write(self):
        """
        This method is designed to handle lines of errors
        """
        if len(self.__lines_to_write) != 0:
            module_doc = self.__get_module_node().get_docstring()
            self.__write_error(self.__get_module_node().get_doc_header_line() + "\n")
            for line in self.__lines_to_write:
                self.__write_error(line)
                self.__write_error("\n")
            str_to_add = '<div><p><span style="color:red;font-weight: bold">' + "\n<br>".join(self.__lines_to_write) + "</span></p></div>"
            module_doc += str_to_add
            error_node = DocNode("ERRORS", self.__module_name, self.__get_module_node())
            error_node.set_data(self.__get_module_node().get_doc_name(), self.__module_name)

            self.__get_module_node().set_docstring(module_doc)

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

    # ======================
    def __load_module(self):
        """
        This method is designed to load (import) the module
        """
        splited_import_path = self.__module_import_path.split(".")
        module_name = splited_import_path[-1]

        if module_name == "__init__":
            import_name = splited_import_path[-2]
            from_import = '.'.join(splited_import_path[:-2])
        else:
            from_import = '.'.join(splited_import_path[:-1])
            import_name = module_name

        if module_name == "__init__" and len(splited_import_path) == 2:
            import_cmd = "import %s" % import_name
        else:
            import_cmd = "from %s import %s" % (from_import, import_name)

        print(import_cmd)
        exec(import_cmd)

        self.__module = eval(import_name)


# ==================================================================================================
# FONCTIONS
# ==================================================================================================
