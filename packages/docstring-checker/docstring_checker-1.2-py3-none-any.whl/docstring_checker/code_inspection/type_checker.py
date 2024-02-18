# coding=utf-8
"""
This module contains the TypeChecker class
"""
import os.path

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
from typing import TextIO
from docstring_checker.doc_node import DocNode
from hierarchical_storage.hierarchical_node import HierarchicalNodeMismatchException
from docstring_type_tag_checker import BaseDocstringType


# ==================================================================================================
# INITIALISATIONS
# ==================================================================================================

# ==================================================================================================
# CLASSES
# ==================================================================================================

# ========================
class TypeChecker(object):
    """
    This class is designed to check the types docstring and reformat the docstrings for HTML generation

    Instance attributes:
    :type __root_node: DocNode
    :ivar __root_node: the root node of the project

    :type __doc_format: docstring_checker.code_inspection.doc_format.DocFormat
    :ivar __doc_format: instance handling the different docstring formats

    :type __error_file: TextIO
    :ivar __error_file: the error file

    :type __is_handled_exception: (str) -> bool
    :ivar __is_handled_exception: function to check if an error is handled from its header in error file
    """
    # ==============================================================================
    def __init__(self, root_node, doc_format, error_filepath, is_handled_exception):
        """
        Initialization of a TypeChecker instance

        :type root_node: DocNode
        :param root_node: the root node of the project

        :type doc_format: docstring_checker.code_inspection.doc_format.DocFormat
        :param doc_format: instance handling the different docstring formats

        :type error_filepath: str
        :param error_filepath: the path to the error file

        :type is_handled_exception: (str) -> bool
        :param is_handled_exception: function to check if an error is handled from its header in error file
        """
        self.__root_node = root_node
        self.__doc_format = doc_format
        self.__error_file = open(error_filepath, mode="a+", encoding="utf8")
        self.__is_handled_exception = is_handled_exception

    # ====================
    def handle_docs(self):
        """
        This function is designed to modify the structure of the DocNode to integrate all the docstring nodes
        """
        class_name_to_module_path = {}
        module_path_to_module_output_file = {}
        nb_module_files = {}
        for module_node in self.__root_node.get_children_in_category_iterator("MODULES"):
            module_path = module_node.get_name()
            module_name = module_node.get_doc_name()
            for class_node in module_node.get_children_in_category_iterator("CLASSES"):
                class_name = class_node.get_name()
                previous_data = class_name_to_module_path.get(class_name, [])
                previous_data.append(module_path)
            if module_name not in nb_module_files:
                nb_module_files[module_name] = 1
                file_name = module_name + ".html"
            else:
                file_name = module_name + "_" + str(nb_module_files[module_name]) + ".html"
                nb_module_files[module_name] += 1
            module_node.set_data("output_path", file_name)
            module_path_to_module_output_file[module_path] = file_name

        self.__treat_node(self.__root_node)

        self.__error_file.flush()
        self.__error_file.close()

    # ===========================
    def __treat_node(self, node):
        """
        This function is designed to treat a node and its subnodes

        :type node: DocNode
        :param node: the ndoe to treat
        """
        category = node.get_node_category()
        if category not in ("root_node", "MODULES"):
            self.__tokenize_doc(node)

        for sub_category in node.get_allowed_child_category():
            for child_node in node.get_children_in_category_iterator(sub_category):
                self.__treat_node(child_node)

    # =============================
    def __tokenize_doc(self, node):
        """
        This method is designed to update the node of a function or method or class and add the sub nodes for the docstring.

        :type node: DocNode
        :param node: the node of the function or method
        """
        name, errors = self.__add_doc_nodes(node)
        self.__handle_errors(node, name, errors)

    # ===========
    @classmethod
    def __get_module_path(cls, node):
        """
        This method is designed to get the import path of the module of a node

        :type node: DocNode
        :param node: the node

        :rtype: str
        :return: the import path of the module of a node
        """
        while node.get_node_category() != "MODULES":
            node = node.get_parent()

        return node.get_data("ModuleImportPath")

    # ===============================
    def __add_doc_nodes(self, node):
        """
        This method is designed to add the 'DOC' subnodes of a node for HTML generation

        :type node: DocNode
        :param node: the node

        :rtype: (str, list[str])
        :return: the name of the next DOC node to generate, list of detected errors
        """
        doc = node.get_docstring()
        name = "1"
        doc_lines = doc.split("\n")
        errors = []
        for line in doc_lines:
            stripped_line = line.strip()
            if stripped_line.startswith(self.__doc_format.get_type_tag()) or stripped_line.startswith(self.__doc_format.get_rtype_tag()):
                types_dict, loc_errors = self.__extract_types_dict(stripped_line, node)
                errors += loc_errors
                name = self.__tokenize_type_line(line, node, types_dict, name=name)
            else:
                new_node = DocNode("DOC", name, node)
                name += "1"
                new_node.set_data("text", line + "\n")

        return name, errors

    # ============================================
    def __handle_errors(self, node, name, errors):
        """
        This method is designed to handle and write the errors and add the doc nodes for errors

        :type node: DocNode
        :param node: the analyzed node

        :type name: str
        :param name: the name of the next DOC node to generate

        :type errors: list[str]
        :param errors: lsit of detected errors
        """
        first_line = node.get_doc_header_line()
        if not self.__is_handled_exception(first_line):
            for error in errors:
                self.__write_in_error_file(first_line + '\n')
                self.__write_in_error_file(error + '\n\n')
                splits = error.split("\n")
                str_to_add = '<div><p><span style="color:red;font-weight: bold">' + "\n<br>".join(splits) + "</span></p></div>"
                new_node = DocNode("DOC", name, node)
                name += "1"
                new_node.set_data("text", str_to_add + "\n")

    # ====================================
    def __write_in_error_file(self, data):
        """
        This method is designed to write in the error file

        :type data: str
        :param data: the data to write in the error file
        """
        if self.__error_file is not None:
            self.__error_file.write(data)

    # =========================================
    def __extract_types_dict(self, line, node):
        """
        This function is designed to get a dictionnary linking classnames to their href data for a docstring type line

        :type line: str
        :param line: the docstring type line

        :type node: DocNode
        :param node: the node of the class, function or method containing the doc

        :rtype: (dict[str, str], list[str])
        :return:  dictionnary linking classnames to their href data for the docstring type line,
                  error messages for bad typing
        """
        errors = []
        type_string = line.strip().split(":")[-1][:-len("<br>")]
        parsed_type = BaseDocstringType.get_type_object(type_string)
        type_names = parsed_type.get_type_strings()
        types_dict = {}
        for type_name in type_names:
            splits = type_name.split(".")
            if len(splits) == 1:
                ref_node = node
                while ref_node.get_node_category() != "MODULES":
                    ref_node = ref_node.get_parent()
            else:
                ref_node = None
                if splits[0] in self.__root_node.get_data("RootNames"):
                    module_import_path = ".".join(splits[:-1])
                    for module_node in self.__root_node.get_children_in_category_iterator("MODULES"):
                        if module_node.get_data("ModuleImportPath") == module_import_path:
                            ref_node = module_node
                            break

                    if ref_node is None:
                        ref_node = self.__get_from_package(module_import_path, init_node=None, search_module=True)

                    if ref_node is None:
                        errors.append("No module with path '%s'" % module_import_path)

            if ref_node is not None:
                modules_dict = ref_node.get_data("KnownInModule")
                try:
                    module_import_path, item_name = modules_dict[splits[-1]]
                except KeyError:
                    errors.append("class '%s' not found in module '%s'" % (type_name, ref_node.get_data("ModuleImportPath")))
                else:
                    module_name = module_import_path.split(".")[-1]
                    file_name = "%s.html" % module_name
                    idx = -1
                    for module_node in self.__root_node.get_children_in_category_iterator("MODULES"):
                        if module_node.get_data("ModuleImportPath") == module_import_path:
                            idx += 1
                            if module_node is ref_node:
                                break
                    if idx == -1:
                        # ===================================================================
                        # Le type est défini dans un module qui n'est pas un module du projet
                        pass
                    else:
                        if idx != 0:
                            file_name = "%s_%i.html" % (module_name, idx)

                        types_dict[type_name] = '"' + file_name + "#" + item_name + '_head"'

        return types_dict, errors

    # ==========================================================================
    def __get_from_package(self, tgt_name, init_node=None, search_module=False):
        """
        This function is designed to get a node from a package

        :type tgt_name: str
        :param tgt_name: name of the data (class, function, module, package) to find in the indicated package or module

        :type init_node: NoneType | DocNode
        :param init_node: node of a module, or package where to find the data

        :type search_module: bool
        :param search_module: True if the searched data point to a module/package, False otherwise

        :rtype: NoneType | DocNode
        :return: the node matching the indicated data. None if not found
        """
        res = None
        if tgt_name.find(".") != -1:
            splits = tgt_name.split(".")
            for sub_name in splits[:-1]:
                init_node = self.__get_from_package(sub_name, init_node=init_node, search_module=True)
                if init_node is None:
                    break

            if init_node is not None:
                res = self.__get_from_package(splits[-1], init_node=init_node, search_module=search_module)

        elif init_node is None:
            module_import_path = "%s.__init__" % tgt_name
            for module_node in self.__root_node.get_children_in_category_iterator("MODULES"):
                if module_node.get_data("ModuleImportPath") == module_import_path:
                    res = module_node
                    break

        else:
            modules_dict = init_node.get_data("KnownInModule")
            try:
                module_import_path, item_name = modules_dict[tgt_name]
            except KeyError:
                # Ca n'est pas un module ou une classe définie dans le __init__.py => on cherche un package
                if init_node.get_module_import_path().endswith(".__init__"):
                    str_to_search = ".%s.__init__" % tgt_name
                    for child in init_node.get_parent().get_children_in_category_iterator("MODULES"):
                        if child.get_module_import_path().endswith(str_to_search):
                            res = child
            else:
                test_module_import_path = module_import_path
                if item_name == "__init__":
                    test_module_import_path = "%s.__init__" % test_module_import_path

                for module_node in self.__root_node.get_children_in_category_iterator("MODULES"):
                    if module_node.get_data("ModuleImportPath") == test_module_import_path:
                        res = module_node
                        break

                if (res is not None) and (not search_module) and (item_name not in ("", "__init__")):
                    res_found = False
                    for category_name in ("CLASSES", "FUNCTIONS"):
                        try:
                            res = res.get_child(category_name, tgt_name)
                        except HierarchicalNodeMismatchException:
                            pass
                        else:
                            res_found = True
                            break

                    if not res_found:
                        res = None

        return res

    # ==========
    @classmethod
    def __tokenize_type_line(cls, doc, node, str_type_to_href_data, name="1"):
        """
        This method is designed to update the type line of the doc of a function or method and add the sub nodes for the docstring.

        :type doc: str
        :param doc: the type line of the doc of the function or method

        :type node: DocNode
        :param node: the node of the function or method

        :type str_type_to_href_data: dict[str, str]
        :param str_type_to_href_data: dictionnary linking a class name to the matching Href data

        :type name: str
        :param name: name of the first doc node to create

        :rtype: str
        :return: name of the next doc node to create after the function is called
        """
        tokens = [[doc, "standard"]]
        for class_name in sorted(str_type_to_href_data, key=len, reverse=True):
            i = 0
            while i < len(tokens):
                cur_token = tokens[i]
                if cur_token[1] == "href":
                    i += 1
                else:
                    splited_tokens = cur_token[0].split(class_name)
                    del tokens[i]
                    tokens.insert(i, [splited_tokens[0], "standard"])
                    idx = i + 1
                    for token in splited_tokens[1:]:
                        tokens.insert(idx, [class_name, "href"])
                        idx += 1
                        tokens.insert(idx, [token, "standard"])
                        idx += 1
                    i += 2 * len(splited_tokens) - 1

        for token in tokens:
            new_node = DocNode("DOC", name, node)
            class_name = token[0]
            new_node.set_data("text", class_name)
            if token[1] == "href":
                href_node = DocNode("HREF", "href", new_node)
                href_path_data = str_type_to_href_data[class_name]
                href_node.set_data("href", href_path_data)
            name += "1"

        return name


# ==================================================================================================
# FONCTIONS
# ==================================================================================================
