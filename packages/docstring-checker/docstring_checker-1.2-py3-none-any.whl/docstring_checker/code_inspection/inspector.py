# coding=utf-8
"""
This module contains the function to generate the hierarchical structure of a python project
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
import sys
import inspect
from glob import iglob
from typing import Callable, Iterable, Generator, TextIO
from hierarchical_storage import HierarchicalNode, HierarchicalNodeMismatchException
from protected_method_metaclass import ProtectedMethodMetaClass
from docstring_type_tag_checker import BaseDocstringType
from enum import Enum


# ==================================================================================================
# INITIALISATIONS
# ==================================================================================================
TYPE_STR = ":type "
PARAM_STR = ":param "
RETURN_STR = ":return:"
RTYPE_STR = ":rtype:"


# ==================================================================================================
# FONCTIONS
# ==================================================================================================

# =========================
def set_doc_mode(doc_mode):
    """
    This function is designed to update the documentation mode and matching tags

    :type doc_mode: str
    :param doc_mode: sphinx or epidoc
    """
    global TYPE_STR
    global PARAM_STR
    global RETURN_STR
    global RTYPE_STR
    if doc_mode == "sphinx":
        TYPE_STR = ":type "
        PARAM_STR = ":param "
        RETURN_STR = ":return:"
        RTYPE_STR = ":rtype:"
    else:
        TYPE_STR = "@type "
        PARAM_STR = "@param "
        RETURN_STR = "@return:"
        RTYPE_STR = "@rtype:"


# ======================================
def get_python_files_iterator(dir_path):
    """
    This method is designed to get an iterator over the python files within a directory and all its sub directories.
    __init__.py files are ignored

    :type dir_path: str
    :param dir_path: path to the directory to inspect

    :rtype: Generator[str]
    :return:n iterator over the python files within a directory and all its sub directories.
    """
    # ========================================================
    # boucle sur les sous fichiers python des sous repertoires
    for filepath in iglob(dir_path + os.sep + "**" + os.sep + "*.py", recursive=True):
        if not filepath.endswith("__init__.py"):
            yield filepath
        else:
            yield filepath


# =============================
def get_python_files(dir_path):
    """
    This function is designed to get the list of python files within a directory and all its sub directories.
    __init__.py files are ignored

    :type dir_path: str
    :param dir_path: path to the directory to inspect

    :rtype: list[str]
    :return: the list of python files within a directory and all its sub directories.
    """
    return [elem for elem in get_python_files_iterator(dir_path)]


# ==================================
def get_classes_from_file(filepath):
    """
    This function is designed to get the names of classes within a python file

    :type filepath: str
    :param filepath: the path to the python file

    :rtype: list[str]
    :return:  the names of classes within the python file
    """
    f1 = open(filepath, 'r', encoding="utf8")
    class_names = []
    line = f1.readline()
    while line != '':
        line = line.strip()
        if line.startswith('class') and line.endswith(':'):
            classname = line.split(' ')[1]
            if classname.find('(') != -1:
                classname = classname.split('(')[0]
            class_names.append(classname)
        line = f1.readline()
    f1.close()
    return class_names


# ==========================================
def reformat_docstring(docstring, decal=''):
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
        # linker = "</p><br><p>"
        linker = "<br>\n"
        new_docstring = linker.join([decal + elem[nb_min:] for elem in splits])
        # new_docstring = "<p>" + new_docstring + "</p>"
    return new_docstring


# ===========================
def search_for_return(lines):
    """
    This function is designed to check if "return" is found within the code of a function

    :type lines: list[str]
    :param lines:  the code lines of the function

    :rtype: bool
    :return: True if return is found within the code of a function, False otherwise
    """
    true_return_found = False
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
            elif striped_line.find(" return ") != -1 and full_strip.startswith("return"):
                true_return_found = True
                break

    return true_return_found


# ==========================
def search_for_yield(lines):
    """
    This function is designed to check if "yield" is found within the code of a function

    :type lines: list[str]
    :param lines:  the code lines of the function

    :rtype: bool
    :return: True if yield is found within the code of a function, False otherwise
    """
    yield_found = False
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
            elif striped_line.endswith(" yield"):
                yield_found = True
                break
            elif striped_line.find(" yield ") != -1 and full_strip.startswith("yield"):
                yield_found = True
                break

    return yield_found


# =============================================
def get_defined_parameters_in_docstring(lines):
    """
    This funuction is designed to get the names of the parameters found in the docstring of a function

    :type lines: list[str]
    :param lines:  the code lines of the function

    :rtype: set[str]
    :return: the names of the parameters found in the docstring of the
    """
    res = set()
    for line in lines:
        striped_line = line.strip()
        if striped_line.startswith(TYPE_STR):
            param = striped_line[len(TYPE_STR):].split(":")[0].strip()
            res.add(param)
        elif striped_line.startswith(PARAM_STR):
            param = striped_line[len(PARAM_STR):].split(":")[0].strip()
            res.add(param)
    return res


# =====================================================
def check_method_docstring(docstring, signature, code):
    """
    This function is designed to check the consistency of the docsting of a function with its code and signature.

    :type docstring: str
    :param docstring: the docstring of the function

    :type signature: inspect.Signature
    :param signature: the signature of the function

    :type code: str
    :param code: the code of the function (with docstring + commentaries)

    :rtype: str
    :return: the error message (empty string if the docstring is consistent with the code and the signature)
    """
    msgs = []
    if docstring != '':
        if docstring.find("XXX") != -1 or docstring.find("???") != -1:
            msg = "'XXX' or '???' found in docstring"
            msgs.append(msg)
        code_split = code.rstrip().replace('\t', '    ').split('\n')
        docstring_split = docstring.replace('\t', '    ').split("\n")
        docstring_params = get_defined_parameters_in_docstring(docstring_split)

        if code.find("raise NotImplementedError") == -1:
            return_found = search_for_return(code_split)
            yield_found = search_for_yield(code_split)
            if yield_found:
                if (docstring.find(RETURN_STR) == -1) or (docstring.find(RTYPE_STR + " Generator[") == -1):
                    msg = "return for yield (Generator[XXX]) missing in docstring"
                    msgs.append(msg)
            elif return_found:
                if (docstring.find(RETURN_STR) == -1) or (docstring.find(RTYPE_STR) == -1):
                    msg = "return missing in docstring"
                    msgs.append(msg)
            elif (docstring.find(RETURN_STR) != -1) or (docstring.find(RTYPE_STR) != -1):
                msg = "return in docstring but no yield or return statement in code"
                msgs.append(msg)

        signature_splits = [elem for elem in signature.parameters if elem not in ['self', 'cls', 'mcs', '_self', '_cls', '_mcs']]

        for elem in signature_splits:
            if elem != "":
                if (elem.find("]") == -1) and (elem.find("[") == -1):
                    if docstring.find(TYPE_STR + elem) == -1 or docstring.find(PARAM_STR + elem) == -1:
                        msgs.append('argument %s is missing in docstring' % elem)
        for param in docstring_params:
            if param not in signature_splits:
                msg = "argument %s defined in docstring but not present in signature" % param
                msgs.append(msg)
    else:
        msgs.append('no docstring!')

    return '\n'.join(msgs)


# ============================================
def get_exception_checks(exception_file_path):
    """
    This method is designed to get the list of functions/methods or classes that must not be analyzed

    :type exception_file_path: str
    :param exception_file_path: the path to the exception file

    :rtype: list[str]
    :return: list of functions/methods or classes that must not be analyzed
    """
    exception_checks_list = []
    if os.path.isfile(exception_file_path):
        f2 = open(exception_file_path, 'r')
        line = f2.readline()
        while line != '':
            line = line.strip()
            if line != '':
                exception_checks_list.append(line)
            line = f2.readline()
        f2.close()
    elif os.path.isdir(os.path.dirname(exception_file_path)):
        f2 = open(exception_file_path, "w")
        f2.close()
    return exception_checks_list


# =============================================================================================
def create_additional_classes_nodes(root_node, error_file, problematic_types, exception_checks,
                                    doc_string_coverage, additional_classes):
    """
    This method is designed to analyze the additional classes and generate the associated doc

    :type root_node: HierarchicalNode
    :param root_node: node to be filled with the data of the additional classes

    :type error_file: TextIO
    :param error_file: the error file to be completed

    :type problematic_types: dict
    :param problematic_types: dictionnary used to register the encountred problems

    :type exception_checks: list[str]
    :param exception_checks: list of functions/methods or classes that must not be analyzed

    :type doc_string_coverage: list[int]
    :param doc_string_coverage: [number of OK docsrings, total number of docstrings]

    :type additional_classes: list[type]
    :param additional_classes: list of classes to be analyzed
    """
    new_path = "additional_classes"
    module_name = "additional_classes"
    module_node = HierarchicalNode("MODULES", new_path, root_node)
    module_node.set_data("ModuleName", module_name)
    module_node.set_data("ModulePath", new_path)
    module_node.set_data("ModuleImportPath", new_path.replace(os.sep, "."))
    sorted_classes = sorted(additional_classes, key=lambda x: x.__name__)
    for additional_class in sorted_classes:
        name = additional_class.__name__
        create_class_node(additional_class, module_name, module_name, name, module_node, error_file, problematic_types, exception_checks,
                          doc_string_coverage)


# ==========================================================================================================================
def create_module_node(module_path, root_node, error_file, modules_to_avoid, dir_path0, problematic_types, exception_checks,
                       doc_string_coverage):
    """
    This funtion is designed to analyze a module and generate the associated doc

    :type module_path: str
    :param module_path: the path to the module path

    :type root_node: HierarchicalNode
    :param root_node: node containing the data of the project to be completed

    :type error_file: TextIO
    :param error_file: the error file to be completed

    :type modules_to_avoid: list[str]
    :param modules_to_avoid: liste of modules not to analyze

    :type dir_path0: str
    :param dir_path0: reference path for relative paths

    :type problematic_types: dict
    :param problematic_types: dictionnary used to register the encountred problems

    :type exception_checks: list[str]
    :param exception_checks: list of functions/methods or classes that must not be analyzed

    :type doc_string_coverage: list[int]
    :param doc_string_coverage: [number of OK docsrings, total number of docstrings]
    """
    str_to_write = ""
    new_path = module_path.replace(dir_path0, '')[1:]
    new_path = new_path[0:-3]
    splits = new_path.split(os.sep)
    new_test_path = new_path.replace(os.sep, '.')
    module_name = splits[-1].replace('.py', '')
    if module_name not in modules_to_avoid:
        module_node = HierarchicalNode("MODULES", new_path, root_node)
        module_node.set_data("ModuleName", module_name)
        module_node.set_data("ModulePath", new_path)
        module_node.set_data("ModuleImportPath", new_path.replace(os.sep, "."))

        if module_name == "__init__":
            import_name = splits[-2]
            loc = '.'.join(splits[:-2])

        else:
            loc = '.'.join(splits[:-1])
            import_name = module_name

        if module_name == "__init__" and len(splits) == 2:
            print('import ' + import_name)
            exec('import ' + import_name)
        else:
            print('from ' + loc + ' import ' + import_name)
            exec('from ' + loc + ' import ' + import_name)

        cur_module = eval(import_name)

        module_doc = cur_module.__doc__
        if module_doc is not None and module_doc != "":
            doc_string_coverage[0] += 1
        else:
            str_to_write = "no docstring!\n"
        doc_string_coverage[1] += 1
        names = sorted(cur_module.__dict__.keys())
        known_in_module = {}
        for name in names:
            test_item = cur_module.__dict__[name]

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
                known_in_module[name] = (source_module_import_path, item_name)

            if isinstance(test_item, type):
                test_class_module = cur_module.__dict__[name].__module__
                if new_test_path == test_class_module:
                    create_class_node(test_item, module_name, new_test_path, name, module_node, error_file, problematic_types,
                                      exception_checks, doc_string_coverage)

            elif type(test_item).__name__ == "function" and callable(test_item):
                test_function_module = cur_module.__dict__[name].__module__
                if new_test_path == test_function_module:
                    if name.startswith('_{0}'.format(name)):
                        true_function_name = name.replace('_{0}'.format(module_name), '')
                    else:
                        true_function_name = name
                    create_function_node(true_function_name, test_item, module_name, new_test_path, module_node, error_file,
                                         exception_checks, doc_string_coverage)

        module_node.set_data("KnownInModule", known_in_module)

        if str_to_write != '':
            print(str_to_write)
            error_file.write("@module " + module_path + '\n')
            error_file.write(str_to_write + '\n')
            splits = str_to_write.split("\n")
            str_to_add = '<div><p><span style="color:red;font-weight: bold">' + "\n<br>".join(splits) + "</span></p></div>"
            module_doc += str_to_add
            error_node = HierarchicalNode("ERRORS", module_name, module_doc)
            error_node.set_data('ModuleName', module_name)

        module_node.set_data('ModuleDoc', module_doc)

# =============================
# noinspection PyShadowingNames
def create_class_node(cur_class, module_name, module_path, name, module_node, error_file, problematic_types,
                      exception_checks, doc_string_coverage):
    """
    This funtion is designed to analyze a class and generate the associated doc

    :type cur_class: type
    :param cur_class: the analyzed class

    :type module_name: str
    :param module_name: the name of the module

    :type module_path: str
    :param module_path: the path to the module path

    :type name: str
    :param name: the name of the class

    :type module_node: HierarchicalNode
    :param module_node: node containing the data of the module to be completed

    :type error_file: TextIO
    :param error_file: the error file to be completed

    :type problematic_types: dict
    :param problematic_types: dictionnary used to register the encountred problems

    :type exception_checks: list[str]
    :param exception_checks: list of functions/methods or classes that must not be analyzed

    :type doc_string_coverage: list[int]
    :param doc_string_coverage: [number of OK docsrings, total number of docstrings]
    """
    properties = []
    class_attributes = []
    class_doc = cur_class.__doc__
    class_doc = reformat_docstring(class_doc)

    class_node = HierarchicalNode("CLASSES", name, module_node)
    class_node.set_data('ClassName', name)

    str_to_write = ''
    if not issubclass(cur_class, Enum):
        test_name = "_" + name + "__old_classdict_keys"
        if test_name in cur_class.__dict__:
            method_names = sorted(cur_class.__dict__[test_name])
        else:
            method_names = sorted(cur_class.__dict__.keys())
        for method_name in method_names:
            try:
                cur_method = cur_class.__dict__[method_name]
            except Exception:
                continue
            if method_name.startswith('_{0}'.format(name)):
                true_method_name = method_name.replace('_{0}'.format(name), '')
            else:
                true_method_name = method_name

            ref_text = type(cur_method).__name__
            if ref_text == "classmethod":
                cur_method = cur_method.__func__
            elif ref_text == "staticmethod":
                cur_method = cur_method.__func__
            elif ref_text == "property":
                properties.append(method_name)
                create_property_nodes(method_name, cur_method, module_name, module_path, name, class_node, error_file, exception_checks,
                                      doc_string_coverage)
                continue
            elif ref_text != "function":
                if method_name not in ['__doc__', '__module__', '__dict__', '__weakref__', "__hash__"]:
                    if (true_method_name != "__protected_methods") or (not isinstance(cur_class, ProtectedMethodMetaClass)):
                        class_attributes.append(method_name)
                continue
            if callable(cur_method):
                method_type = ref_text
                if method_type == "function":
                    method_type = "method"
                create_method_node(true_method_name, cur_method, module_name, module_path, name, class_node, error_file, exception_checks,
                                   doc_string_coverage, method_type)
            else:
                bases = [base_name.__name__ for base_name in cur_class.__bases__]
                if method_name not in ['__dict__', '__weakref__'] and 'type' not in bases:
                    pb_type = type(cur_method).__name__
                    if pb_type not in ['str', 'dict', 'list']:
                        if pb_type in problematic_types:
                            problematic_types[pb_type].append((module_name, name, method_name))
                        else:
                            problematic_types[pb_type] = [(module_name, name, method_name)]

        if "__init__" in method_names:
            cur_method = cur_class.__dict__["__init__"]
            detected_attributes = detect_attributes(cur_method)
        else:
            detected_attributes = set()
        if class_doc is not None and class_doc.strip() != "":
            prefix = '_' + name
            attribute_not_found = False
            for class_attribute in class_attributes:
                if class_attribute.startswith(prefix + '__'):
                    true_class_attribute = class_attribute[len(prefix):]
                else:
                    true_class_attribute = class_attribute
                test_line = module_path + "." + name + "." + true_class_attribute
                if (test_line not in exception_checks) and (
                        true_class_attribute not in ("__orig_bases__", "__parameters__", "__annotations__")):
                    if class_doc.find('type %s:' % true_class_attribute) == -1:
                        str_to_write += "missing class attribute %s in class doc\n" % true_class_attribute
                        attribute_not_found = True
                    elif (class_doc.find('cvar %s:' % true_class_attribute) == -1) and (
                            true_class_attribute not in ("__orig_bases__", "__parameters__", "__annotations__")):
                        str_to_write += "missing class attribute "
                        str_to_write += true_class_attribute
                        str_to_write += " in class doc\n"
                        attribute_not_found = True
            for detected_attribute in detected_attributes:
                if detected_attribute.startswith(prefix + '__'):
                    true_instance_attribute = detected_attribute[len(prefix):]
                else:
                    true_instance_attribute = detected_attribute
                test_line = module_path + "." + name + "." + true_instance_attribute
                if test_line not in exception_checks:
                    if class_doc.find('type %s:' % true_instance_attribute) == -1:
                        str_to_write += "missing instance attribute "
                        str_to_write += true_instance_attribute
                        str_to_write += " in class doc\n"
                        attribute_not_found = True
                    elif class_doc.find('ivar %s:' % true_instance_attribute) == -1:
                        str_to_write += "missing instance attribute "
                        str_to_write += true_instance_attribute
                        str_to_write += " in class doc\n"
                        attribute_not_found = True

            test_line = module_path + "." + name + "." + "__doc__"
            xxx_found = False
            if test_line not in exception_checks:
                if class_doc.find("XXX") != -1 or class_doc.find("???") != -1:
                    str_to_write += "'XXX' or '???' present in class doc !\n"
                    xxx_found = True

            if not attribute_not_found or xxx_found:
                doc_string_coverage[0] += 1
        else:
            str_to_write += "no docstring!\n"
        doc_string_coverage[1] += 1
    else:
        if class_doc is None or class_doc == "":
            str_to_write += "no docstring!\n"

    if str_to_write != '':
        error_file.write("@class " + module_path + '.' + name + '\n')
        error_file.write(str_to_write + '\n')
        splits = str_to_write.split("\n")
        str_to_add = '<div><p><span style="color:red;font-weight: bold">' + "\n<br>".join(splits) + "</span></p></div>"
        class_doc += str_to_add
        error_node = HierarchicalNode("ERRORS", name, class_node)
        error_node.set_data('ClassName', name)

    class_node.set_data('ClassDoc', class_doc)


# =================================
def detect_attributes(init_method):
    """
    This function is designed to detect instance attributes by reading the content of the __init__ method

    :type init_method: Callable
    :param init_method: the __init__ method

    :rtype: set[str]
    :return: the names of the instance attributes
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

    return detected_attributes


# ================================================================================================================================
def create_property_nodes(method_name, cur_method, module_name, module_path, class_name, class_node, error_file, exception_checks,
                          doc_string_coverage):
    """
    This funtion is designed to analyze a property and generate the associated doc

    :type method_name: str
    :param method_name: the name of the property

    :type cur_method: property
    :param cur_method: the analyzed property

    :type module_name: str
    :param module_name: the name of the module

    :type module_path: str
    :param module_path: the path to the module path

    :type class_name: str
    :param class_name: the name of the class

    :type class_node: HierarchicalNode
    :param class_node: node containing the data of the class to be completed

    :type error_file: TextIO
    :param error_file: the error file to be completed

    :type exception_checks: list[str]
    :param exception_checks: list of functions/methods or classes that must not be analyzed

    :type doc_string_coverage: list[int]
    :param doc_string_coverage: [number of OK docsrings, total number of docstrings]
    """
    get_method = cur_method.fget
    set_method = cur_method.fset
    if get_method is not None:
        error_found = False
        cur_doc = get_method.__doc__
        cur_doc = reformat_docstring(cur_doc)
        try:
            # noinspection PyUnresolvedReferences
            meta_wrapped = get_method.__meta_wrapped__
        except Exception:
            source_code = inspect.getsource(get_method)
            signature = inspect.signature(get_method)
        else:
            source_code = inspect.getsource(meta_wrapped)
            signature = inspect.signature(get_method)
        cur_signature = inspect.signature(get_method)
        str_cur_signature = str(cur_signature)
        if str_cur_signature.endswith("typing.Type"):
            str_cur_signature = "->".join(str_cur_signature.split("->")[0:-1]).rstrip()
        getter_name = "(property.getter) " + method_name
        property_getter_node = HierarchicalNode("METHODS", getter_name, class_node)
        property_getter_node.set_data('IMethodName', getter_name)
        test_val = check_method_docstring(cur_doc, signature, source_code)
        if test_val != '':
            test_line = "@property_getter " + module_path + '.' + class_name + '.' + 'property ' + method_name
            if test_line not in exception_checks:
                error_file.write(test_line + '\n')
                error_file.write(test_val + '\n\n')
                splits = test_val.split("\n")
                str_to_add = '<div><p><span style="color:red;font-weight: bold">' + "\n<br>".join(splits) + "</span></p></div>"
                cur_doc += str_to_add
                error_found = True
                error_node = HierarchicalNode("ERRORS", getter_name, property_getter_node)
                error_node.set_data('ClassName', class_name)
                error_node.set_data('MethodName', getter_name)
        property_getter_node.set_data('IMethodSignature', str_cur_signature)
        property_getter_node.set_data('IMethodDoc', cur_doc)
        if not error_found:
            doc_string_coverage[0] += 1
        doc_string_coverage[1] += 1
    if set_method is not None:
        error_found = False
        cur_doc = set_method.__doc__
        cur_doc = reformat_docstring(cur_doc)
        try:
            # noinspection PyUnresolvedReferences
            meta_wrapped = set_method.__meta_wrapped__
        except Exception:
            source_code = inspect.getsource(set_method)
            signature = inspect.signature(set_method)
        else:
            source_code = inspect.getsource(meta_wrapped)
            signature = inspect.signature(meta_wrapped)
        cur_signature = inspect.signature(set_method)
        str_cur_signature = str(cur_signature)
        if str_cur_signature.endswith("typing.Type"):
            str_cur_signature = "->".join(str_cur_signature.split("->")[0:-1]).rstrip()
        setter_name = "(property.setter) " + method_name
        property_setter_node = HierarchicalNode("METHODS", setter_name, class_node)
        property_setter_node.set_data('IMethodName', setter_name)
        test_val = check_method_docstring(cur_doc, signature, source_code)
        if test_val != '':
            test_line = "@property_setter " + module_path + '.' + class_name + '.' + 'property ' + method_name + ' setter'
            if test_line not in exception_checks:
                error_file.write(test_line + '\n')
                error_file.write(test_val + '\n\n')
                splits = test_val.split("\n")
                str_to_add = '<div><p><span style="color:red;font-weight: bold">' + "\n<br>".join(splits) + "</span></p></div>"
                cur_doc += str_to_add
                error_found = True
                error_node = HierarchicalNode("ERRORS", setter_name, property_setter_node)
                error_node.set_data('ClassName', class_name)
                error_node.set_data('MethodName', setter_name)
        property_setter_node.set_data('IMethodSignature', str_cur_signature)
        property_setter_node.set_data('IMethodDoc', cur_doc)
        if not error_found:
            doc_string_coverage[0] += 1
        doc_string_coverage[1] += 1


# =============================================================================================================================
def create_function_node(true_function_name, cur_function, module_name, module_path, module_node, error_file, exception_checks,
                         doc_string_coverage):
    """
    This funtion is designed to analyze a function and generate the associated doc

    :type true_function_name: str
    :param true_function_name: the name of the function

    :type cur_function: Callable
    :param cur_function: the function

    :type module_name: str
    :param module_name: the name of the module

    :type module_path: str
    :param module_path: the path to the module path

    :type module_node: HierarchicalNode
    :param module_node: node containing the data of the module to be completed

    :type error_file: TextIO
    :param error_file: the error file to be completed

    :type exception_checks: list[str]
    :param exception_checks: list of functions/methods or classes that must not be analyzed

    :type doc_string_coverage: list[int]
    :param doc_string_coverage: [number of OK docsrings, total number of docstrings]
    """
    error_found = False
    function_doc = cur_function.__doc__
    function_doc = reformat_docstring(function_doc)
    try:
        cur_signature = inspect.signature(cur_function)
    except ValueError:
        pass
    else:
        str_cur_signature = str(cur_signature)
        if str_cur_signature.endswith("typing.Type"):
            str_cur_signature = "->".join(str_cur_signature.split("->")[0:-1]).rstrip()
        try:
            meta_wrapped = cur_function.__meta_wrapped__
        except Exception:
            source_code = inspect.getsource(cur_function)
            signature = inspect.signature(cur_function)
        else:
            source_code = inspect.getsource(meta_wrapped)
            signature = inspect.signature(meta_wrapped)
        function_node = HierarchicalNode("FUNCTIONS", true_function_name, module_node)
        function_node.set_data("FunctionName", true_function_name)
        test_val = check_method_docstring(function_doc, signature, source_code)
        if test_val != '':
            test_line = "@function " + module_path + '.' + true_function_name
            if test_line not in exception_checks:
                error_file.write(test_line + '\n')
                error_file.write(test_val + '\n\n')
                splits = test_val.split('\n')
                str_to_add = '<div><p><span style="color:red;font-weight: bold">' + "\n<br>".join(splits) + "</span></p></div>"
                function_doc += str_to_add
                error_found = True
                error_node = HierarchicalNode("ERRORS", true_function_name, function_node)
                error_node.set_data('FunctionName', true_function_name)
        function_node.set_data("FunctionSignature", str_cur_signature)
        function_node.set_data("FunctionDoc", function_doc)
        if not error_found:
            doc_string_coverage[0] += 1
        doc_string_coverage[1] += 1


# ==================================================================================================================================
def create_method_node(true_method_name, cur_method, module_name, module_path, class_name, class_node, error_file, exception_checks,
                       doc_string_coverage, method_type="method"):
    """
    This funtion is designed to analyze a method and generate the associated doc

    :type true_method_name: str
    :param true_method_name: the name of the method

    :type cur_method: Callable
    :param cur_method: the method

    :type module_name: str
    :param module_name: the name of the module

    :type module_path: str
    :param module_path: the path to the module path

    :type class_name: str
    :param class_name: the name of the class containing the method

    :type class_node: HierarchicalNode
    :param class_node: node containing the data of the module to be completed

    :type error_file: TextIO
    :param error_file: the error file to be completed

    :type exception_checks: list[str]
    :param exception_checks: list of functions/methods or classes that must not be analyzed

    :type doc_string_coverage: list[int]
    :param doc_string_coverage: [number of OK docsrings, total number of docstrings]

    :type method_type: str
    :param method_type: the type of method (method, staticmethod or classmethod)
    """
    if method_type == "method":
        category = "METHODS"
        name_str = "IMethodName"
        signature_str = "IMethodSignature"
        doc_str = "IMethodDoc"
    elif method_type == "staticmethod":
        category = "STATIC_METHODS"
        name_str = "SMethodName"
        signature_str = "SMethodSignature"
        doc_str = "SMethodDoc"
    else:
        category = "CLASS_METHODS"
        name_str = "CMethodName"
        signature_str = "CMethodSignature"
        doc_str = "CMethodDoc"
    error_found = False

    method_doc = cur_method.__doc__
    method_doc = reformat_docstring(method_doc)
    try:
        cur_signature = inspect.signature(cur_method)
    except ValueError:
        pass
    else:
        str_cur_signature = str(cur_signature)
        if str_cur_signature.endswith("typing.Type"):
            str_cur_signature = "->".join(str_cur_signature.split("->")[0:-1]).rstrip()
        try:
            meta_wrapped = cur_method.__meta_wrapped__
        except Exception:
            source_code = inspect.getsource(cur_method)
            signature = inspect.signature(cur_method)
        else:
            source_code = inspect.getsource(meta_wrapped)
            signature = inspect.signature(meta_wrapped)
        method_node = HierarchicalNode(category, true_method_name, class_node)
        method_node.set_data(name_str, true_method_name)
        test_val = check_method_docstring(method_doc, signature, source_code)
        if test_val != '':
            test_line = "@method " + module_path + '.' + class_name + '.' + true_method_name
            if test_line not in exception_checks:
                error_file.write(test_line + '\n')
                error_file.write(test_val + '\n\n')
                splits = test_val.split("\n")
                str_to_add = '<div><p><span style="color:red;font-weight: bold">' + "\n<br>".join(splits) + "</span></p></div>"
                method_doc += str_to_add
                error_found = True
                error_node = HierarchicalNode("ERRORS", true_method_name, method_node)
                error_node.set_data('ClassName', class_name)
                error_node.set_data('MethodName', true_method_name)
        method_node.set_data(signature_str, str_cur_signature)
        method_node.set_data(doc_str, method_doc)
        if not error_found:
            doc_string_coverage[0] += 1
        doc_string_coverage[1] += 1


# ===================================================================================================================
def initialize_project_root_node(project_name, source_directories, output_dir, modules_to_avoid, additional_classes):
    """
    This function is designed to initialize the HierarchicalNode containing the data of the project

    :type project_name: str
    :param project_name: the name of the project

    :type source_directories: Iterable[str]
    :param source_directories: the list of source directories to analyze

    :type output_dir: str
    :param output_dir: path to the output directory

    :type modules_to_avoid: list[str]
    :param modules_to_avoid: liste of modules not to analyze

    :type additional_classes: list[type]
    :param additional_classes: list of additional classes for inspection

    :rtype: HierarchicalNode
    :return: the HierarchicalNode containing the data of the project
    """
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    # ==================================================================
    # Chemin vers le fichiers des exceptions (methodes a ne pas traiter)
    # S'il n'y a pas d'exception remplacer par un empty string
    # Le fichier se compose de ligne de ce type:
    #     <nom_du_module>.<nom_de_la_classe>.<nom_de_la_methode>
    # ex: tablewrapper.Adder_phaseTableWrapper.__custom_add_check
    # Ce fichier peut etre rapidement constitue en reprenant les lignes du fichier d'erreur
    exception_file = os.path.join(output_dir, '..', 'exception_check.txt')

    # ===============================================
    # Chemin vers le fichier d'erreur qui recapitule
    # les probleme de coherence des docstring
    # Obligatoire
    error_file = os.path.join(output_dir, 'errors.txt')

    # ===========================================================================================
    # Dictionnaire Qui contient en clef les types problematique et en valeur des donnees relative
    # Si quelque chose est printe en consol c'est qu'on a rencontre de tels types, il faut savoir pourquoi
    problematic_types = {}

    # ============================================
    # Recuperation des methodes a ne pas inspecter
    exception_checks = get_exception_checks(exception_file)

    # ==================================================
    # Recuperation de tous les chemins vers les modules
    # et mise a jour du Pythonpath si necessaire
    python_files_by_source_directory = []
    root_names = []
    for source_dir in source_directories:
        root_names.append(os.path.basename(source_dir))
        dir_path0 = os.path.dirname(source_dir)
        if dir_path0 not in sys.path:
            sys.path.insert(0, dir_path0)

        python_files = get_python_files_iterator(source_dir)
        python_files_by_source_directory.append(python_files)

    # ======================================================================
    # Ouverture des fichiers de sortie et d'erreur et boucle sur les modules

    root_node = HierarchicalNode("root_node", project_name)
    root_node.set_data("ProjectName", project_name)
    g = open(error_file, 'w', encoding="utf8")
    doc_string_coverage = [0, 0]
    for i, source_dir in enumerate(source_directories):
        python_files = python_files_by_source_directory[i]
        for module_path in python_files:
            dir_path0 = os.path.dirname(source_dir)
            create_module_node(module_path, root_node, g, modules_to_avoid, dir_path0, problematic_types, exception_checks,
                               doc_string_coverage)

        create_additional_classes_nodes(root_node, g, problematic_types, exception_checks, doc_string_coverage, additional_classes)
    g.close()

    # =================
    # print des erreurs
    for pb_type in problematic_types:
        print(pb_type)
        print(problematic_types[pb_type])

    root_node.set_data("RootNames", root_names)

    return root_node


# =====================================
def handle_docs(root_node, error_file):
    # TODO ajouter la gestion des exceptions
    """
    This function is designed to modify the structure of the HierarchicalNode to integrate all the docstring nodes

    :type root_node: HierarchicalNode
    :param root_node: the HierarchicalNode containing the data of the project

    :type error_file: TextIO
    :param error_file: the error file where to write the errors
    """
    # ============================================================================================
    # Construction des dictionnaire class_name_to_module_path et module_path_to_module_output_file
    #     - class_name_to_module_path relie un nom de classe a tous les chemins de module qui declarent une classe de ce nom
    #     - module_path_to_module_output_file relie le chemins d'un module au nom de son fichier html
    class_name_to_module_path = {}
    module_path_to_module_output_file = {}
    nb_module_files = {}
    for module_node in root_node.get_children_in_category_iterator("MODULES"):
        module_path = module_node.get_name()
        module_name = module_node.get_data("ModuleName")
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

    # =========================
    # Boucle sur les modules...
    for module_node in root_node.get_children_in_category_iterator("MODULES"):

        # ================================
        # Boucle sur les classes du module
        for class_node in module_node.get_children_in_category_iterator("CLASSES"):

            # ==============================================================
            # Mise a jour de la donnee hierarchisee pour la doc de la classe
            class_doc = class_node.get_data("ClassDoc")
            class_node.remove_data("ClassDoc")
            tokenize_doc(class_doc, class_node, root_node, error_file)

            # ================================================
            # Boucle sur les methodes statiques de la clase...
            for static_method_node in class_node.get_children_in_category_iterator("STATIC_METHODS"):
                # =========================================================================
                # Mise a jour de la donnee hierarchisee pour la doc de la methode statique
                static_method_doc = static_method_node.get_data("SMethodDoc")
                static_method_node.remove_data("SMethodDoc")
                tokenize_doc(static_method_doc, static_method_node, root_node, error_file)

            # ================================================
            # Boucle sur les methodes de classe de la clase...
            for class_method_node in class_node.get_children_in_category_iterator("CLASS_METHODS"):

                # =========================================================================
                # Mise a jour de la donnee hierarchisee pour la doc de la methode de classe
                class_method_doc = class_method_node.get_data("CMethodDoc")
                class_method_node.remove_data("CMethodDoc")
                tokenize_doc(class_method_doc, class_method_node, root_node, error_file)

            # ======================================
            # Boucle sur les methodes de la clase...
            for method_node in class_node.get_children_in_category_iterator("METHODS"):

                # ===============================================================
                # Mise a jour de la donnee hierarchisee pour la doc de la methode
                method_doc = method_node.get_data("IMethodDoc")
                method_node.remove_data("IMethodDoc")
                tokenize_doc(method_doc, method_node, root_node, error_file)

        # =====================================
        # Boucle sur les fonctions du module...
        for function_node in module_node.get_children_in_category_iterator("FUNCTIONS"):

            # ===============================================================
            # Mise a jour de la donnee hierarchisee pour la doc de la methode
            function_doc = function_node.get_data("FunctionDoc")
            function_node.remove_data("FunctionDoc")
            tokenize_doc(function_doc, function_node, root_node, error_file)


# =================================================================
def tokenize_type_line(doc, node, str_type_to_href_data, name="1"):
    """
    This method is designed to update the type line of the doc of a function or method and add the sub nodes for the docstring.

    :type doc: str
    :param doc: the type line of the doc of the function or method

    :type node: HierarchicalNode
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
                i += 2*len(splited_tokens) - 1

    for token in tokens:
        new_node = HierarchicalNode("DOC", name, node)
        class_name = token[0]
        new_node.set_data("text", class_name)
        if token[1] == "href":
            href_node = HierarchicalNode("HREF", "href", new_node)
            href_path_data = str_type_to_href_data[class_name]
            href_node.set_data("href", href_path_data)
        name += "1"

    return name


# =============================================================================
def get_from_package(root_node, tgt_name, init_node=None, search_module=False):
    """
    This function is designed to get a node from a package

    :type root_node: HierarchicalNode
    :param root_node: node containing the project

    :type tgt_name: str
    :param tgt_name: name of the data (class, function, module, package) to find in the indicated package or module

    :type init_node: NoneType | HierarchicalNode
    :param init_node: node of a module, or package where to find the data

    :type search_module: bool
    :param search_module: True if the searched data point to a module/package, False otherwise

    :rtype: NoneType | HierarchicalNode
    :return: the node matching the indicated data. None if not found
    """
    res = None
    if tgt_name.find(".") != -1:
        splits = tgt_name.split(".")
        for sub_name in splits[:-1]:
            init_node = get_from_package(root_node, sub_name, init_node=init_node, search_module=True)
            if init_node is None:
                break

        if init_node is not None:
            res = get_from_package(root_node, splits[-1], init_node=init_node, search_module=search_module)

    elif init_node is None:
        module_import_path = "%s.__init__" % tgt_name
        for module_node in root_node.get_children_in_category_iterator("MODULES"):
            if module_node.get_data("ModuleImportPath") == module_import_path:
                res = module_node
                break

    else:
        modules_dict = init_node.get_data("KnownInModule")
        try:
            module_import_path, item_name = modules_dict[tgt_name]
        except KeyError:
            pass
        else:
            test_module_import_path = module_import_path
            if item_name == "__init__":
                test_module_import_path = "%s.__init__" % test_module_import_path

            for module_node in root_node.get_children_in_category_iterator("MODULES"):
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


# ============================================
def extract_types_dict(line, node, root_node):
    """
    This function is designed to get a dictionnary linking classnames to their href data for a docstring type line

    :type line: str
    :param line: the docstring type line

    :type node: HierarchicalNode
    :param node: the node of the class, function or method containing the doc

    :type root_node: HierarchicalNode
    :param root_node: the node of the project

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
            if splits[0] in root_node.get_data("RootNames"):
                module_import_path = ".".join(splits[:-1])
                for module_node in root_node.get_children_in_category_iterator("MODULES"):
                    if module_node.get_data("ModuleImportPath") == module_import_path:
                        ref_node = module_node
                        break

                if ref_node is None:
                    ref_node = get_from_package(root_node, module_import_path, init_node=None, search_module=True)

                if ref_node is None:
                    print("GNARK 1")
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
                for module_node in root_node.get_children_in_category_iterator("MODULES"):
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


# =================================================
def tokenize_doc(doc, node, root_node, error_file):
    """
    This method is designed to update the node of a function or method and add the sub nodes for the docstring.

    :type doc: str
    :param doc: the docstring of the function or method

    :type node: HierarchicalNode
    :param node: the node of the function or method

    :type root_node: HierarchicalNode
    :param root_node: root node of the project

    :type error_file: TextIO
    :param error_file: the error file where to write the errors
    """
    name = "1"
    doc_lines = doc.split("\n")
    errors = []
    for line in doc_lines:
        stripped_line = line.strip()
        if stripped_line.startswith(TYPE_STR) or stripped_line.startswith(RTYPE_STR):
            types_dict, loc_errors = extract_types_dict(stripped_line, node, root_node)
            errors += loc_errors
            name = tokenize_type_line(line, node, types_dict, name=name)
        else:
            new_node = HierarchicalNode("DOC", name, node)
            name += "1"
            new_node.set_data("text", line + "\n")

    category = node.get_node_category()
    module_node = node
    while module_node.get_node_category() != "MODULES":
        module_node = module_node.get_parent()
    module_path = module_node.get_data("ModuleImportPath")
    if category == "CLASSES":
        first_line = "@class " + module_path + '.' + node.get_data("ClassName")
    elif category.find("METHODS") != -1:
        class_node = node.get_parent()
        class_name = class_node.get_data("ClassName")
        if node.get_name().startswith("property.getter."):
            method_name = node.get_data("IMethodName").split("(")[-1]
            first_line = "@property_getter " + module_path + '.' + class_name + '.' + 'property ' + method_name
        elif node.get_name().startswith("property.setter."):
            method_name = node.get_data("IMethodName").split("(")[-1]
            first_line = "@property_getter " + module_path + '.' + class_name + '.' + 'property ' + method_name
        else:
            if category == "METHODS":
                name_str = "IMethodName"
            elif category == "STATIC_METHODS":
                name_str = "SMethodName"
            else:
                name_str = "CMethodName"
            first_line = "@method " + module_path + '.' + class_name + '.' + node.get_data(name_str)
    else:  # FUNCTIONS
        first_line = "@function " + module_path + '.' + node.get_data("FunctionName")

    for error in errors:
        error_file.write(first_line + '\n')
        error_file.write(error + '\n\n')
        splits = error.split("\n")
        str_to_add = '<div><p><span style="color:red;font-weight: bold">' + "\n<br>".join(splits) + "</span></p></div>"
        new_node = HierarchicalNode("DOC", name, node)
        name += "1"
        new_node.set_data("text", str_to_add + "\n")
        # error_node = HierarchicalNode("ERRORS", name, class_node)
        # error_node.set_data('ClassName', name)


# ===============================================================================
def get_project_root_node(dir_path0, project_name, output_dir, modules_to_avoid):
    """
    This function is designed to get the completed node of the project

    :type dir_path0: str
    :param dir_path0: chemin vers le repertoire juste au dessus du package/projet

    :type project_name: str
    :param project_name: le nom du package/projet

    :type output_dir: str
    :param output_dir: le chemin vers le repertoire de sortie ou seront generes les htmls

    :type modules_to_avoid: list[str]
    :param modules_to_avoid: liste des modules a ne pas traiter

    :rtype: HierarchicalNode
    :return: le noeud racine du projet python
    """
    root_node = initialize_project_root_node(dir_path0, project_name, output_dir, modules_to_avoid,
                                             [])

    error_filepath = os.path.join(output_dir, 'errors.txt')
    error_file = open(error_filepath, 'w', encoding="utf8")
    handle_docs(root_node, error_file)
    error_file.close()

    return root_node


# ============================
def get_attr_types(class_doc):
    """
    This function is designed to get all the class names found in a docstring

    :type class_doc: str
    :param class_doc: the docstring

    :rtype: set[str]
    :return: ll the class names found in the docstring
    """
    class_names = set()
    splits = class_doc.split("\n")
    for line in splits:
        line = line.strip()
        if line.startswith(":type "):
            try:
                class_name = line.split(":")[2]
            except Exception:
                pass
            else:
                class_name = class_name.strip()
                class_names.add(class_name)
    return class_names


# # ====================================================================================
# def generate_xlsx_class_diagram(dir_path0, project_name, modules_to_avoid, xlsx_path):
#     """
#     Cette fonction n'est encore qu'un test!
#     Elle peremet de generer un fichier Excel qui decrit le diagramme de classe
#     Ce fichier peut etre lu par Yed
#
#     :type dir_path0: str
#     :param dir_path0: chemin vers le repertoire juste au dessus du package/projet
#
#     :type project_name: str
#     :param project_name: le nom du package/projet
#
#     :type modules_to_avoid: list[str]
#     :param modules_to_avoid: liste des modules a ne pas traiter
#
#     :type xlsx_path: str
#     :param xlsx_path: the path to the xlsx file to create
#     """
#     workbook = Workbook(xlsx_path)
#     worksheet = workbook.add_worksheet()
#     worksheet.write("A1", "source")
#     worksheet.write("B1", "target")
#     worksheet.write("C1", "type")
#     line_idx = 2
#     # ====================================
#     # Repertoire a partir duquel le chemin de module
#     # seront ecrits dans la doc de facon relative
#     sys.path.insert(0, dir_path0)
#
#     # =======================================================
#     # Repertoire dans lequel on va chercher tous les modules
#     # de facon recursive
#     dir_path1 = os.path.join(dir_path0, project_name)
#
#     # ==================================================
#     # Recuperation de tous les chemins vers les modules
#     python_files = get_python_files(dir_path1)
#
#     # =========================================================
#     # Parcourt des modules pour extraire les classes du projets
#     # les classes sont ajoutees a class_set
#     class_set = set()
#     for module_path in python_files:
#         new_path = module_path.replace(dir_path0, '')[1:]
#         new_path = new_path[0:-3]
#         splits = new_path.split(os.sep)
#         new_test_path = new_path.replace(os.sep, '.')
#         module_name = splits[-1].replace('.py', '')
#         if module_name not in modules_to_avoid:
#             loc = '.'.join(splits[:-1])
#             print('from ' + loc + ' import ' + module_name)
#             exec('from ' + loc + ' import ' + module_name)
#             cur_module = eval(module_name)
#             names = sorted(cur_module.__dict__.keys())
#             for name in names:
#                 test_item = cur_module.__dict__[name]
#                 if isinstance(test_item, type):
#                     test_class_module = cur_module.__dict__[name].__module__
#                     if new_test_path == test_class_module:
#                         class_set.add(test_item)
#
#     for cur_class in class_set:
#         class_name = cur_class.__name__
#         class_doc = cur_class.__doc__
#         bases = cur_class.__bases__
#         for base in bases:
#             worksheet.write(line_idx, 0, class_name)
#             worksheet.write(line_idx, 1, base.__name__)
#             worksheet.write(line_idx, 2, "inherit")
#             line_idx += 1
#
#         if class_doc is not None:
#             attr_types = get_attr_types(class_doc)
#             for attr_type in attr_types:
#                 worksheet.write(line_idx, 0, class_name)
#                 worksheet.write(line_idx, 1, attr_type)
#                 worksheet.write(line_idx, 2, "agregate")
#                 line_idx += 1
#
#     workbook.close()


# # ======================================================================================
# def generate_graphml_class_diagram(dir_path0, project_name, modules_to_avoid, graphml_path):
#     """
#     Elle peremet de generer un fichier graphml qui decrit le diagramme de classe
#
#     :type dir_path0: str
#     :param dir_path0: chemin vers le repertoire juste au dessus du package/projet
#
#     :type project_name: str
#     :param project_name: le nom du package/projet
#
#     :type modules_to_avoid: list[str]
#     :param modules_to_avoid: liste des modules a ne pas traiter
#
#     :type graphml_path: str
#     :param graphml_path: le chemin vers le fichier graphml
#     """
#     graph = Graph()
#
#     # ====================================
#     # Repertoire a partir duquel le chemin de module
#     # seront ecrits dans la doc de facon relative
#     sys.path.insert(0, dir_path0)
#
#     # =======================================================
#     # Repertoire dans lequel on va chercher tous les modules
#     # de facon recursive
#     dir_path1 = os.path.join(dir_path0, project_name)
#
#     # ==================================================
#     # Recuperation de tous les chemins vers les modules
#     python_files = get_python_files(dir_path1)
#
#     # =========================================================
#     # Parcourt des modules pour extraire les classes du projets
#     # les classes sont ajoutees a class_set
#     class_dict = {}
#     nodes_dict = {}
#     for module_path in python_files:
#         new_path = module_path.replace(dir_path0, '')[1:]
#         new_path = new_path[0:-3]
#         splits = new_path.split(os.sep)
#         new_test_path = new_path.replace(os.sep, '.')
#         module_name = splits[-1].replace('.py', '')
#         if module_name not in modules_to_avoid:
#             loc = '.'.join(splits[:-1])
#             print('from ' + loc + ' import ' + module_name)
#             exec('from ' + loc + ' import ' + module_name)
#             cur_module = eval(module_name)
#             names = sorted(cur_module.__dict__.keys())
#             for name in names:
#                 test_item = cur_module.__dict__[name]
#                 if isinstance(test_item, type):
#                     test_class_module = cur_module.__dict__[name].__module__
#                     if new_test_path == test_class_module:
#                         class_dict[name] = test_item
#                         nodes_dict[name] = graph.add_node(name)
#     for class_name, cur_class in class_dict.items():
#         class_doc = cur_class.__doc__
#         bases = cur_class.__bases__
#         class_node = nodes_dict[class_name]
#         for base in bases:
#             base_name = base.__name__
#             try:
#                 base_node = nodes_dict[base_name]
#             except KeyError:
#                 base_node = graph.add_node(base_name)
#                 nodes_dict[base_name] = base_node
#             graph.add_edge(class_node, base_node)
#         #
#         # if class_doc is not None:
#         #     attr_types = get_attr_types(class_doc)
#         #     for attr_type in attr_types:
#         #         worksheet.write(line_idx, 0, class_name)
#         #         worksheet.write(line_idx, 1, attr_type)
#         #         worksheet.write(line_idx, 2, "agregate")
#         #         line_idx += 1
#         graph.save_to_graphml(graphml_path)


# ========================
if __name__ == "__main__":
    GV4_dir = r"C:\Users\mmalbert\Desktop\Geraldyne_V4_V4\Geraldyne_V4_V4"
    GV4_modules_to_avoid = ['generate_config_file', 'main', 'runtime_hook',
                            'test_acceleration_extraction', 'test_displacement_extraction',
                            'test_velocity_extraction', 'text_csv_timed_data_export',
                            'test_egeri_h5_model', 'test_plot2d_visu', 'inspector', 'conf']
    # GV4_root_node = get_project_root_node(GV4_dir, "Geraldyne_V4", ".", GV4_modules_to_avoid)
    # print(GV4_root_node)
