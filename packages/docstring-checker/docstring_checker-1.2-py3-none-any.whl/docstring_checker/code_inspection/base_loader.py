# coding=utf-8
"""
This module contains the BaseLoader class
"""
from __future__ import annotations

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
from class_factory import ClassFactoryUser, BaseClassFactory
from protected_method_metaclass import Protected


# ==================================================================================================
# INITIALISATIONS
# ==================================================================================================

# ==================================================================================================
# CLASSES
# ==================================================================================================

# =================================
class BaseLoader(ClassFactoryUser):
    """
    This class is the base class for all data loaders of the docstring_checker project

    :type __parent_node: docstring_checker.doc_node.DocNode
    :ivar __parent_node: the hierarchical node where data will be added

    :type __parent_loader: NoneType | BaseLoader
    :ivar __parent_loader: the parent loader
    """

    # ==========
    @classmethod
    def __get_factory_id(cls):
        """
        This method is designed to get the ID of the factory dedicated to this class
        The name of the directory where subclasses are to be found is a good idea

        :rtype: str
        :return: the ID of the factory dedicated to this class
        """
        return os.path.dirname(os.path.abspath(__file__))

    # ==========
    @classmethod
    def __get_import_data_for_factory(cls):
        """
        This method is designed to get the list of settings to import subclasses. Each item of the list contains :
          - import_path : path from which files to import are searched recursively : <import_path>/*/**/<format_name>
          - import_val : string replacing import path to import the files.
            ex : <import_path>/a/b/<file name>
               - if import_val == "":
                 the file will be imported this way : "from a.b import <module name>
               - otherwise:
                   the file will be imported this way  "from <import_val>.a.b import <module name>
          - format_name : glob token used to find the file to import (ex : task_*.py)

        :rtype: list[(str, str, str)]
        :return: the list of settings to import subclasses : (import_path, import_val, format_name)
        """
        import_path = os.path.join(cls.__get_factory_id(), "loaders")
        format_name = "*.py"
        import_val = "docstring_checker.code_inspection.loaders"

        return [(import_path, import_val, format_name)]

    # ==========
    @classmethod
    def __get_base_class_for_factory(cls):
        """
        This method is designed to get the base class for the factory

        :rtype: type
        :return: the base class for the factory
        """
        return BaseLoader

    # ==========
    @classmethod
    def __get_id_function_name_for_factory(cls):
        """
        This method is designed to get the name of the method returning the ID of the class for the factory

        :rtype: str
        :return: the name of the method returning the ID of the class for the factory
        """
        return "get_loader_id"

    # ==================================================
    def __init__(self, parent_node, parent_loader=None):
        """
        Initialization of a BaseLoader instance

        :type parent_node: docstring_checker.doc_node.DocNode
        :param parent_node: the hierarchical node where data will be added

        :type parent_loader: NoneType | BaseLoader
        :param parent_loader: the parent loader
        """
        self.__parent_node = parent_node
        self.__parent_loader = parent_loader

    # ========
    @Protected
    def __get_parent_node(self):
        """
        This method is designed to get the hierarchical node where data will be added

        :rtype: docstring_checker.doc_node.DocNode
        :return: the hierarchical node where data will be added
        """
        return self.__parent_node

    # ========
    @Protected
    def __get_parent_loader(self):
        """
        This method is designed to get the parent loader

        :rtype: NoneType | BaseLoader
        :return: the parent loader
        """
        return self.__parent_loader

    # ========
    @Protected
    def __get_highest_parent_loader(self):
        """
        This method is designed to get the highest parent loader

        :rtype: BaseLoader
        :return: the highest parent loader
        """
        res = self
        while res.__parent_loader is not None:
            res = res.__get_parent_loader()

        return res

    # ========
    @Protected
    @classmethod
    def __get_prefix(cls, name):
        """
        This method is designed to get the prefix for private attribute of a class or module

        :type name: str
        :param name: the name of the class or module

        :rtype: str
        :return: the prefix for private attribute of the class or module
        """
        return "_%s" % name

    # ========
    @Protected
    @classmethod
    def __get_true_name(cls, mangled_name, prefix):
        """
        This method is designed to get the true name (not mangled name) of a class or module member

        :type mangled_name: str
        :param mangled_name: the mangled name

        :type prefix: str
        :param prefix: the prefix for mangled name

        :rtype: str
        :return: the true name
        """
        if mangled_name.startswith(prefix):
            res = mangled_name[len(prefix):]
        else:
            res = mangled_name

        return res

    # ========
    @Protected
    @classmethod
    def __reformat_docstring(cls, docstring, decal=''):
        """
        This function is designed to reformat docstring and correct indents

        :type docstring: str
        :param docstring: the docstring

        :type decal: str
        :param decal: additional indentation character

        :rtype: str
        :return: the formated docstring
        """
        if docstring is None:
            new_docstring = ''
        else:
            if docstring.startswith('\n'):
                docstring = docstring[1:]
            if docstring.endswith('\n'):
                docstring = docstring[:-1]
            docstring = docstring.replace('\t', '    ')
            splits = docstring.split('\n')
            nb_min = 10000
            for i in range(len(splits)):
                line = splits[i]
                if line.strip() != '':
                    nb_test = len(line) - len(line.lstrip())
                    if nb_test < nb_min:
                        nb_min = nb_test

            linker = "<br>\n"
            new_docstring = linker.join([decal + elem[nb_min:] for elem in splits])

        return new_docstring

    # ========
    @Protected
    def __check_method_docstring(self, docstring, signature, code):
        """
        This function is designed to check the consistency of the docsting of a function with its code and signature.

        :type docstring: str
        :param docstring: the docstring of the function

        :type signature: inspect.Signature
        :param signature: the signature of the function

        :type code: str
        :param code: the code of the function (with docstring + commentaries)

        :rtype: list[str]
        :return: liens of the the error message (empty list if the docstring is consistent with the code and the signature)
        """
        doc_format = self.__get_doc_format_function()

        msgs = []
        if docstring != '':
            if docstring.find("XXX") != -1 or docstring.find("???") != -1:
                msg = "'XXX' or '???' found in docstring"
                msgs.append(msg)
            code_split = code.rstrip().replace('\t', '    ').split('\n')
            docstring_split = docstring.replace('\t', '    ').split("\n")
            docstring_params = self.__get_defined_parameters_in_docstring(docstring_split)

            if code.find("raise NotImplementedError") == -1:
                return_found = self.__search_for_return_or_yield(code_split, word_to_search="return")
                yield_found = self.__search_for_return_or_yield(code_split, word_to_search="yield")
                if yield_found:
                    if (docstring.find(doc_format.get_return_tag()) == -1) or (
                            docstring.find(doc_format.get_rtype_tag() + " Generator[") == -1):
                        msg = "return for yield (Generator[XXX]) missing in docstring"
                        msgs.append(msg)
                elif return_found:
                    if (docstring.find(doc_format.get_return_tag()) == -1) or (docstring.find(doc_format.get_rtype_tag()) == -1):
                        msg = "return missing in docstring"
                        msgs.append(msg)
                elif (docstring.find(doc_format.get_return_tag()) != -1) or (docstring.find(doc_format.get_rtype_tag()) != -1):
                    msg = "return in docstring but no yield or return statement in code"
                    msgs.append(msg)

            signature_splits = [elem for elem in signature.parameters if elem not in ['self', 'cls', 'mcs', '_self', '_cls', '_mcs']]

            for elem in signature_splits:
                if elem != "":
                    if (elem.find("]") == -1) and (elem.find("[") == -1):
                        if docstring.find(doc_format.get_type_tag() + elem) == -1 or docstring.find(
                                doc_format.get_param_tag() + elem) == -1:
                            msgs.append('argument %s is missing in docstring' % elem)

            for param in docstring_params:
                if param not in signature_splits:
                    msg = "argument %s defined in docstring but not present in signature" % param
                    msgs.append(msg)
        else:
            msgs.append('no docstring!')

        return msgs

    # =====================================================
    def __get_defined_parameters_in_docstring(self, lines):
        """
        This funuction is designed to get the names of the parameters found in the docstring of a function

        :type lines: list[str]
        :param lines:  the code lines of the function

        :rtype: set[str]
        :return: the names of the parameters found in the docstring of the
        """
        doc_format = self.__get_doc_format_function()

        res = set()
        for line in lines:
            striped_line = line.strip()
            if striped_line.startswith(doc_format.get_type_tag()):
                param = striped_line[len(doc_format.get_type_tag()):].split(":")[0].strip()
                res.add(param)
            elif striped_line.startswith(doc_format.get_param_tag()):
                param = striped_line[len(doc_format.get_param_tag()):].split(":")[0].strip()
                res.add(param)
        return res

    # ==========
    @classmethod
    def __search_for_return_or_yield(cls, lines, word_to_search="return"):
        """
        This function is designed to check if "return" or "yield" is found within the code of a function

        :type lines: list[str]
        :param lines:  the code lines of the function

        :type word_to_search: str
        :param word_to_search: the word to search (return or yield)

        :rtype: bool
        :return: True if return (or yield) is found within the code of a function, False otherwise
        """
        word_found = False
        ignore_mode = False
        first = True
        token = ""
        for line in lines:
            striped_line = line.rstrip()
            full_strip = line.strip()
            if ignore_mode:
                if not line.startswith(token) and full_strip != "":
                    ignore_mode = False
            if not ignore_mode:
                if full_strip.startswith("def "):
                    if not first:
                        token = line.split("def")[0] + " "
                        ignore_mode = True
                    else:
                        first = False
                elif (word_to_search == "yield") and striped_line.endswith(" %s" % word_to_search):
                    word_found = True
                    break
                elif striped_line.find(" %s " % word_to_search) != -1 and full_strip.startswith("%s" % word_to_search):
                    word_found = True
                    break

        return word_found

    # ========
    @Protected
    def __write_error(self, data):
        """
        This method is designed to write an error

        :type data: str
        :param data: the data to write in the error file
        """
        module_node = self.__get_highest_parent_loader()
        module_node.__write_error(data)

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
        module_node = self.__get_highest_parent_loader()
        return module_node.__is_handled_exception(exception_header)

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
        module_node = self.__get_highest_parent_loader()
        module_node.__update_problematic_types(cur_class, class_name, item_name, test_item)

    # ========
    @Protected
    def __get_doc_format_function(self):
        """
        This method is designed to get the DocFormat instance

        :rtype: docstring_checker.code_inspection.doc_format.DocFormat
        :return: the DocFormat instance
        """
        module_node = self.__get_highest_parent_loader()
        return module_node.__get_doc_format_function()

    # =============
    def load(self):
        """
        This method is designed to perform data loading
        """
        raise NotImplementedError("The method 'load' is not overloaded for subclass %s !" % str(self.__class__))


# ==================================================================================================
# FONCTIONS
# ==================================================================================================
