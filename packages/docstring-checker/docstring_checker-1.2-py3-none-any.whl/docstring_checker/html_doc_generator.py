# coding=utf-8
"""
This module contains the HtmlDocGenerator class
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
from typing import Callable, Iterable, Generator
from shutil import copy, rmtree
from tpt_reading import TptRootNode
from docstring_checker.error_printer_from_file import ErrorPrinterFromFile
from docstring_checker.docstring_checker_base_exception import DocstringCheckerBaseException
from docstring_checker.code_inspection.doc_format import DocFormat, DocFormatEnum
from docstring_checker.code_inspection.docstring_data_collector import DocstringDataCollector
from docstring_checker.code_inspection.type_checker import TypeChecker


# ==================================================================================================
# INITIALISATIONS
# ==================================================================================================

# ==================================================================================================
# CLASSES
# ==================================================================================================

# =============================
class HtmlDocGenerator(object):
    """
    This class defines HTML doc generator for a python project

    Class attributes:
    :type __tool_directory_path: str
    :cvar __tool_directory_path: the path to the docstring_checker tool directory


    Attributs d'instance:
    :type __stylesheet_path: str
    :ivar __stylesheet_path: the path to the stylesheet of the html documentation

    :type __image_directory_path: str
    :ivar __image_directory_path: the path to the directory containing the images for the html documentation

    :type __index_template: TptRootNode
    :ivar __index_template: template data for the index of the html documentation

    :type __module_template: TptRootNode
    :ivar __module_template: template data for a module page of the html documentation

    :type __front_page_template: TptRootNode
    :ivar __front_page_template: template data for the front page of the html data

    :type __project_name: str
    :ivar __project_name: the name of the project

    :type __source_directories_paths: Iterable[str]
    :ivar __source_directories_paths: list of directories containing the source code to analyze

    :type __output_dir: str
    :ivar __output_dir: path to the output directory of the html documentation

    :type __modules_to_avoid: list[str]
    :ivar __modules_to_avoid: list of module names that should not be considered during the analysis

    :type __additional_classes: list[type]
    :ivar __additional_classes: liste of additional classes to analyses (usually built with metaclass)

    :type __errors: list[DocstringCheckerBaseException]
    :ivar __errors: list of errors detected during the analysis

    :type __exception_checks: list[str]
    :ivar __exception_checks: lsit of error headers that should not be found in the error file

    :type __doc_format: DocFormat
    :ivar __doc_format: instance handling the different docstring formats
    """
    __tool_directory_path = os.path.dirname(__file__)

    # ==================================================================================================================
    def __init__(self, index_template_path="", module_template_path="", front_page_template_path="", stylesheet_path="",
                 image_directory_path="", doc_mode=DocFormatEnum.SPINX):
        """
        Initialization of an HtmlDocGenerator instance

        :type index_template_path: str
        :param index_template_path: the path to the template of the index of the html documentation

        :type module_template_path: str
        :param module_template_path: the path to the template of a module page of the html documentation

        :type front_page_template_path: str
        :param front_page_template_path: the path to the template of the front page of the html documentation

        :type stylesheet_path: str
        :param stylesheet_path: the path to the stylesheet of the html documentation

        :type image_directory_path: str
        :param image_directory_path: the path to the directory containing the images for the html documentation

        :type doc_mode: str | DocFormatEnum
        :param doc_mode: the current docstring format
        """
        tpt_directory_path = os.path.join(self.__tool_directory_path, "data", "templates")

        # ====================
        # Formating arguments:
        if index_template_path == "":
            index_template_path = os.path.join(tpt_directory_path, "default_index.tpt")
        if module_template_path == "":
            module_template_path = os.path.join(tpt_directory_path, "default_module.tpt")
        if front_page_template_path == "":
            front_page_template_path = os.path.join(tpt_directory_path, "default_front_page.tpt")
        if stylesheet_path == "":
            stylesheet_path = os.path.join(tpt_directory_path, "default_css.css")
        if image_directory_path == "":
            image_directory_path = os.path.join(self.__tool_directory_path, "data", "img")

        self.__check_input_paths(index_template_path, module_template_path, front_page_template_path, stylesheet_path, image_directory_path)
        index_template, module_template, front_page_template = self.__load_templates(index_template_path, module_template_path,
                                                                                     front_page_template_path)
        # ====================
        # assigning attributes
        self.__stylesheet_path = stylesheet_path
        self.__image_directory_path = image_directory_path
        self.__index_template = index_template
        self.__module_template = module_template
        self.__front_page_template = front_page_template
        self.__project_name = ""
        self.__source_directories_paths = []
        self.__output_dir = ""
        self.__modules_to_avoid = []
        self.__additional_classes = []
        self.__errors = []
        self.__exception_checks = []
        self.__doc_format = DocFormat(doc_mode)

    # ============================
    def get_errors_iterator(self):
        """
        This method is designed to get an iterator over the errors detected during the analysis

        :rtype: Generator[DocstringCheckerBaseException]
        :return: an iterator over the errors detected during the analysis
        """
        for elem in self.__errors:
            yield elem

    # ===================
    def get_errors(self):
        """
        This method is designed to get the list of errors detected during the analysis

        :rtype: list[DocstringCheckerBaseException]
        :return: the list of errors detected during the analysis
        """
        return [elem for elem in self.get_errors_iterator()]

    # ===========
    @staticmethod
    def __check_input_paths(index_template_path, module_template_path, front_page_template_path, stylesheet_path, image_directory_path):
        """
        This method is designed to check that the different paths indicated in the __init__ method are valid
        An error is raised if there is any problem.

        :type index_template_path: str
        :param index_template_path: the path to the template of the index of the html documentation

        :type module_template_path: str
        :param module_template_path: the path to the template of a module page of the html documentation

        :type front_page_template_path: str
        :param front_page_template_path: the path to the template of the front page of the html documentation

        :type stylesheet_path: str
        :param stylesheet_path: the path to the stylesheet of the html documentation

        :type image_directory_path: str
        :param image_directory_path: the path to the directory containing the images for the html documentation
        """
        msgs = ["The template file for the index does not exist !",
                "The template file for the module page does not exist !",
                "The template file for the front page does not exist !",
                "The stylesheet file does not exist !"]
        filepaths = [index_template_path, module_template_path, front_page_template_path, stylesheet_path]
        final_msgs = []

        for filepath, msg in zip(filepaths, msgs):
            if not os.path.isfile(filepath):
                final_msgs.append(msg)

        if not os.path.isdir(image_directory_path):
            final_msgs.append("The images directory does not exist !")

        if len(final_msgs) > 0:
            descr = "Problem with the input data :"
            raise DocstringCheckerBaseException(descr, "\n".join(final_msgs))

    # ================================================================
    def __check_run_paths(self, source_directories_paths, output_dir):
        """
        This method is designed to check the validity of the source directories and of the output directory
        An error is raised if there is any problem.

        :type source_directories_paths: Iterable[str]
        :param source_directories_paths: list of directories containing the source code to analyze

        :type output_dir: str
        :param output_dir: path to the output directory of the html documentation
        """
        final_msgs = []

        for dir_path in source_directories_paths:
            if not os.path.isdir(dir_path):
                final_msgs.append("The path to the sourc directory %s is not valid !" % dir_path)

        if not os.path.isdir(output_dir):
            try:
                self.__run_in_try_except(os.makedirs, "The output directory %s does not exist and cannot be created !", output_dir)
            except DocstringCheckerBaseException as e:
                final_msgs.append(str(e))

        if len(final_msgs) > 0:
            descr = "Problem with the directories :"
            raise DocstringCheckerBaseException(descr, "\n".join(final_msgs))

    # ==========
    @classmethod
    def __load_templates(cls, index_template_path, module_template_path, front_page_template_path):
        """
        This method is designed to load the different template files

        :type index_template_path: str
        :param index_template_path: the path to the template of the index of the html documentation

        :type module_template_path: str
        :param module_template_path: the path to the template of a module page of the html documentation

        :type front_page_template_path: str
        :param front_page_template_path: the path to the template of the front page of the html documentation

        :rtype: (TptRootNode, TptRootNode, TptRootNode)
        :return: template data for the index of the html documentation,
                 template data for a module page of the html documentation,
                 template data for the front page of the html data
        """
        errors = []
        res = []
        filepaths = (index_template_path, module_template_path, front_page_template_path)
        tgt_methods = (cls.__read_index_template, cls.__read_module_template, cls.__read_front_page_template)

        for filepath, tgt_method in zip(filepaths, tgt_methods):
            try:
                res.append(tgt_method(filepath))
            except DocstringCheckerBaseException as e:
                errors.append(str(e))

        if len(errors) > 0:
            descr = "Problem reading templates :"
            raise DocstringCheckerBaseException(descr, "\n".join(errors))

        return tuple(res)

    # ===========
    @staticmethod
    def __run_in_try_except(tgt_function, error_description, *args, **kwargs):
        """
        This method is designed to execute a function within a try/except block and raise a DocstringCheckerBaseException
        if an error occurs.

        :raises DocstringCheckerBaseException: Exception raised if an error occurs

        :type tgt_function: Callable
        :param tgt_function: the called function

        :type error_description: str
        :param error_description: error message to add to the DocstringCheckerBaseException if an error occurs

        :type args: any
        :param args: positional arguments for the function

        :type kwargs: any
        :param kwargs: keyword arguments for the function

        :rtype: any
        :return: the result of the function
        """
        try:
            res = tgt_function(*args, **kwargs)
        except Exception:
            raise DocstringCheckerBaseException(error_description)

        return res

    # ==========
    @classmethod
    def __read_template(cls, template_path, error_description):
        """
        This method is designed to read a template file

        :raises DocstringCheckerBaseException: exception raised if an error occurs

        :type template_path: str
        :param template_path: the path to the template file

        :type error_description: str
        :param error_description:  error message to add to the DocstringCheckerBaseException if an error occurs

        :rtype: TptRootNode
        :return: the template data loaded from the template file
        """
        return cls.__run_in_try_except(TptRootNode, error_description, template_path)

    # ==========
    @classmethod
    def __read_index_template(cls, index_template_path):
        """
        This method is designed to read the template of the index of the html documentation

        :raises DocstringCheckerBaseException: exception raised if an error occurs

        :type index_template_path: str
        :param index_template_path: the path to the template of the index of the html documentation

        :rtype: TptRootNode
        :return: the template data loaded from template of the index of the html documentation
        """
        descr = "Problem reading the template for the index"
        return cls.__read_template(index_template_path, descr)

    # ==========
    @classmethod
    def __read_module_template(cls, module_template_path):
        """
        This method is designed to read the template of a module page of the html documentation

        :raises DocstringCheckerBaseException: exception raised if an error occurs

        :type module_template_path: str
        :param module_template_path: the path to the template of a module page of the html documentation

        :rtype: TptRootNode
        :return: the template data loaded from template of a module page of the html documentation
        """
        descr = "Problem reading the template for a module page"
        return cls.__read_template(module_template_path, descr)

    # ==========
    @classmethod
    def __read_front_page_template(cls, front_page_template_path):
        """
        This method is designed to read the template of the front page of the html documentation

        :raises DocstringCheckerBaseException: exception raised if an error occurs

        :type front_page_template_path: str
        :param front_page_template_path: the path to the template of the front page of the html documentation

        :rtype: TptRootNode
        :return: the template data loaded from template of the front page of the html documentation
        """
        descr = "Problem reading the template for the front page"
        return cls.__read_template(front_page_template_path, descr)

    # ============================
    def __get_doc_directory(self):
        """
        This method is designet to get the path to the "doc_directory" generated in the output diretory

        :rtype: str
        :return: the path to the "doc_directory" generated in the output diretory
        """
        return os.path.abspath(os.path.join(self.__output_dir, "doc_directory"))

    # ==============================
    def __get_stylesheet_name(self):
        """
        This method is designed to the name of the stylesheet file

        :rtype: str
        :return: the name of the stylesheet file
        """
        return os.path.basename(self.__stylesheet_path)

    # ============================
    def get_error_file_path(self):
        """
        This method is designed to get the path to the error file generated in the "doc_directory"

        :rtype: str
        :return: the path to the error file generated in the "doc_directory"
        """
        return os.path.join(self.__get_doc_directory(), "errors.txt")

    # ===============================
    def get_exception_filepath(self):
        """
        This method is designed to get the path to the exception file

        :rtype: str
        :return: the path to the exception file
        """
        return os.path.abspath(os.path.join(self.__get_doc_directory(), '..', 'exception_check.txt'))

    # ==================================
    def __update_exception_checks(self):
        """
        This method is designed to load the content of the exception file and generate it if not existing
        """
        exceptions_filepath = self.get_exception_filepath()
        self.__exception_checks = []
        if os.path.isfile(exceptions_filepath):
            with open(exceptions_filepath, mode='r', encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line != '':
                        self.__exception_checks.append(line)

        elif os.path.isdir(os.path.dirname(exceptions_filepath)):
            f = open(exceptions_filepath, "w")
            f.close()

    # =================================================
    def __is_handled_exception(self, exception_header):
        """
        This method is designed to check if an exception is handled

        :type exception_header: str
        :param exception_header: description of the error

        :rtype: bool
        :return: True if the error is handled, False otherwise.
        """
        return exception_header in self.__exception_checks

    # ================================================================================================================
    def run(self, project_name, source_directories_paths, output_dir, modules_to_avoid=None, additional_classes=None):
        """
        This method is designed to launch the generation of the html documentation of a project

        :type project_name: str
        :param project_name: the name of the project

        :type source_directories_paths: Iterable[str]
        :param source_directories_paths: list of directories containing the source code to analyze

        :type output_dir: str
        :param output_dir: path to the output directory of the html documentation

        :type modules_to_avoid: NoneType | list[str]
        :param modules_to_avoid: list of module names that should not be considered during the analysis

        :type additional_classes: NoneType | list[type]
        :param additional_classes: liste of additional classes to analyses (usually built with metaclass)

        :rtype: bool
        :return: True if the documentation contains errors, False otherwise
        """
        if modules_to_avoid is None:
            modules_to_avoid = []
        if additional_classes is None:
            additional_classes = []

        self.__errors = []
        self.__check_run_paths(source_directories_paths, output_dir)
        self.__project_name = project_name
        self.__source_directories_paths = source_directories_paths
        self.__output_dir = output_dir
        self.__modules_to_avoid = modules_to_avoid
        self.__additional_classes = additional_classes

        self.__update_exception_checks()

        try:
            self.__initialize_output_dir()
            collector = DocstringDataCollector(self.__project_name, source_directories_paths, modules_to_avoid, additional_classes,
                                               self.__doc_format, self.__is_handled_exception, errors_filepath=self.get_error_file_path())
            hierarchical_data = collector.collect_data()
            self.__reformat_docstrings(hierarchical_data)
            html_index_text = self.__get_index_html_data(hierarchical_data)
            self.__write_front_page(hierarchical_data, html_index_text)
            self.__write_html_modules(hierarchical_data, html_index_text)
        except DocstringCheckerBaseException as e:
            self.__errors.append(e)
        except Exception:
            self.__errors.append(DocstringCheckerBaseException("Unexpected error"))
        else:
            if len(self.__errors) > 0:
                raise DocstringCheckerBaseException("Error in documentation creation !", "\n".join(str(self.__errors)))

            error_file = self.get_error_file_path()
            f = open(error_file, "r")
            data = f.read()
            f.close()
            if len(data) > 0:
                descr = "The documentation is not complete or lacks some precisions"
                msg = "Check the %s file" % error_file
                self.__errors.append(DocstringCheckerBaseException(descr, msg))

        return len(self.__errors) == 0

    # ==========================
    def print_error_lines(self):
        """
        This method is designed to print the errors from the error file.
        If possible the line of the doc errors will be displayed
        """
        error_printer = ErrorPrinterFromFile(self.get_error_file_path(), self.__source_directories_paths)
        error_printer.run()

    # ================================
    def __initialize_output_dir(self):
        """
        This method is designed to initialize the output directory
        """
        # =====================================
        # Creation du sous-repertoire de sortie
        doc_directory = self.__get_doc_directory()
        if os.path.isdir(doc_directory):
            self.__run_in_try_except(rmtree, "Impossible de supprimer le sous-repertoire de sortie !", doc_directory)

        self.__run_in_try_except(os.mkdir, "Impossible de creer le sous-repertoire de sortie !", doc_directory)

        # ===========================================================================================
        # Copie des images dans le repertoire pour les rendre accessibles au html et de la stylesheet
        for image_name in os.listdir(self.__image_directory_path):
            copy(os.path.join(self.__image_directory_path, image_name), os.path.join(doc_directory, image_name))
        copy(self.__stylesheet_path, os.path.join(doc_directory, self.__get_stylesheet_name()))

    # =================================================
    def __reformat_docstrings(self, hierarchical_data):
        """
        This method is designed to reformat a docstring for the html format, including Hrefs.

        :type hierarchical_data: docstring_checker.doc_node.DocNode
        :param hierarchical_data: the data from the project in a DocNode instance
        """
        type_checker = TypeChecker(hierarchical_data, self.__doc_format, self.get_error_file_path(), self.__is_handled_exception)
        self.__run_in_try_except(type_checker.handle_docs, "Problem during docstring formating")

    # =================================================
    def __get_index_html_data(self, hierarchical_data):
        """
        This method is designed to the html text of the index

        :type hierarchical_data: docstring_checker.doc_node.DocNode
        :param hierarchical_data: the data from the project in a DocNode instance

        :rtype: str
        :return: the html text of the index
        """
        descr = "Problem during html index building"

        return self.__run_in_try_except(self.__index_template.get_text, descr, hierarchical_data.get_data_dict(), hierarchical_data)

    # ===============================================================
    def __write_front_page(self, hierarchical_data, html_index_text):
        """
        This method is designed to write the front page of the html documentation

        :type hierarchical_data: docstring_checker.doc_node.DocNode
        :param hierarchical_data: the data from the project in a DocNode instance

        :type html_index_text: str
        :param html_index_text: the html text of the index
        """
        hierarchical_data.set_data("Index", html_index_text)
        hierarchical_data.set_data("css_file", self.__get_stylesheet_name())

        descr = "Problem during html front page building"
        html_text = self.__run_in_try_except(self.__front_page_template.get_text, descr, hierarchical_data.get_data_dict(),
                                             hierarchical_data)

        descr = "problem during writing of the html front page"
        file_name = "front_page.html"
        file_path = os.path.join(self.__get_doc_directory(), file_name)
        try:
            f = open(file_path, "w", encoding='utf-8')
            f.write(html_text)
            f.close()
        except Exception:
            raise DocstringCheckerBaseException(descr)

    # =================================================================
    def __write_html_modules(self, hierarchical_data, html_index_text):
        """
        This method is designed to write the html pages of the modules

        :type hierarchical_data: docstring_checker.doc_node.DocNode
        :param hierarchical_data: the data from the project in a DocNode instance

        :type html_index_text: str
        :param html_index_text: the html text of the index
        """
        doc_directory = self.__get_doc_directory()
        css_name = self.__get_stylesheet_name()
        construction_descr = "Probleme building html file for module %s"
        writting_descr = "Probleme writing html file for module% s"

        for module_node in hierarchical_data.get_children_in_category_iterator("MODULES"):
            module_node.set_data("Index", html_index_text)
            module_node.set_data("css_file", css_name)
            module_path = module_node.get_data("ModulePath")
            descr = construction_descr % module_path
            html_text = self.__run_in_try_except(self.__module_template.get_text, descr, module_node.get_data_dict(), module_node)

            file_name = module_node.get_data("output_path")
            file_path = os.path.join(doc_directory, file_name)
            try:
                f = open(file_path, "w", encoding='utf-8')
                f.write(html_text)
                f.close()
            except Exception:
                descr = writting_descr % module_path
                raise DocstringCheckerBaseException(descr)


# ==================================================================================================
# FONCTIONS
# ==================================================================================================
