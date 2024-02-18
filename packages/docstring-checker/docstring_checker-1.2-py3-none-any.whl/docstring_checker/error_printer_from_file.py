# coding=utf-8
"""
This module contains the ErrorPrinterFromFile class
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
import os


# ==================================================================================================
# INITIALISATIONS
# ==================================================================================================

# ==================================================================================================
# CLASSES
# ==================================================================================================

# ================================
class ErrorPrinterFromFile(object):
    """
    This class is designed to handle errors printing from the error file

    Instance attributes:
    :type __error_filepath: str
    :ivar __error_filepath: the path to the error file

    :type __lib_name_to_path: dict[str, str]
    :ivar __lib_name_to_path: dictionnary linking the name of a library to its system file

    :type __filepaths_to_lines: dict[str, list[str]]
    :ivar __filepaths_to_lines: dictionnary linking the path to a source file to its lines

    :type __erorr_lines_set: set[str]
    :ivar __erorr_lines_set: set of lines pointing to the line of a docstring in a source file where there is an error

    :type __last_input_in_erorr_lines_set: str
    :ivar __last_input_in_erorr_lines_set: last added element to __erorr_lines_set

    :type __tmp_lines: list[str]
    :ivar __tmp_lines: lines of error from the error file for the current item

    :type __complementary_data: dict[str, list[str]]
    :ivar __complementary_data: dictionnary linking a line pointing to the line of a docstring in a source file where there is an error
                                to the matching lines of error from the error file for the current item
    """

    # ================================================
    def __init__(self, error_filepath, library_paths):
        """
        Initialization of a ErrorPrinterFromFile instance

        :type error_filepath: str
        :param error_filepath: the path to the error file

        :type library_paths: Iterable[str]
        :param library_paths: list of path to the parser libraries
        """
        self.__error_filepath = error_filepath
        self.__lib_name_to_path = {os.path.basename(elem): elem for elem in library_paths}
        self.__filepaths_to_lines = {}
        self.__erorr_lines_set = set()
        self.__last_input_in_erorr_lines_set = ""
        self.__tmp_lines = []
        self.__complementary_data = {}

    # ================
    def __reset(self):
        """
        This method is designed to reset the instance between two run
        """
        self.__filepaths_to_lines = {}
        self.__erorr_lines_set = set()
        self.__last_input_in_erorr_lines_set = ""
        self.__tmp_lines = []
        self.__complementary_data = {}

    # ===============================
    def __get_error_file_lines(self):
        """
        This method is designed to get the lines of the error file

        :rtype: list[str]
        :return: the lines of the error file
        """
        f = open(self.__error_filepath, "r")
        lines = f.readlines()
        f.close()

        return lines

    # =============================================
    def __lines_points_to_lib(self, stripped_line):
        """
        This method is designed to check if a line from the error file points to a problematic doc

        :type stripped_line: str
        :param stripped_line: the stripped line from the error file

        :rtype: (str, list[str], str)
        :return: the path to the library concerned by the error,
                 import path to the problematic doc
                 the tag indiating the type of docstring (ex : @function, @method...)

                 If the line does not points to a problematic doc, ("", [], "") is returned
        """
        lib_path = ""
        type_str = ""
        splits = []
        if stripped_line.find(".") != -1:
            cond = stripped_line.startswith("@function ")
            cond |= stripped_line.startswith("@method ")
            cond |= stripped_line.startswith("@class ")
            cond |= stripped_line.startswith("@property_getter ")
            cond |= stripped_line.startswith("@property_setter ")
            cond |= stripped_line.startswith("@module ")
            if cond:
                splits = stripped_line.split(".")
                try:
                    type_data = splits[0].split(" ")
                    type_str = type_data[0]
                    test_name = type_data[1]
                    splits[0] = test_name
                    lib_path = self.__lib_name_to_path[test_name]
                except Exception:
                    self.__tmp_lines.append(stripped_line)

        return lib_path, splits, type_str

    # ==========
    @classmethod
    def __get_text_path(cls, lib_path, splits):
        """
        This method is designed to get the path to the file pointed by an error

        :type lib_path: str
        :param lib_path: the path to the library concerned by the error

        :type splits: list[str]
        :param splits: the import path to the problematic docstring (library name removed)

        :rtype: str
        :return: the path to the file pointed by the error
        """
        test_path = ""
        i = len(splits)
        while i > 0:
            test_path = os.path.join(lib_path, os.sep.join(splits[:i])) + ".py"
            if os.path.isfile(test_path):
                i = 0
            else:
                test_path = ""
                i -= 1

        return test_path

    # ==========================================
    def __get_source_file_lines(self, filepath):
        """
        This method is designed to get the lines of a source file

        :type filepath: str
        :param filepath: the path to the source file

        :rtype: list[str]
        :return: the lines of the source file
        """
        try:
            file_lines = self.__filepaths_to_lines[filepath]
        except KeyError:
            try:
                f = open(filepath, "r")
                file_lines = f.readlines()
                f.close()
            except Exception:
                file_lines = []
            self.__filepaths_to_lines[filepath] = file_lines

        return file_lines

    # ==========
    @classmethod
    def __get_line_number(cls, file_lines, tokens, type_str):
        """
        This method is designed to get the line number where to find a docstring in a soure file

        :type file_lines: list[str]
        :param file_lines: the lines of the source file

        :type tokens: list[str]
        :param tokens: import path to the doc to search

        :type type_str: str
        :param type_str: the tag indiating the type of docstring (ex : @function, @method...)

        :rtype: int
        :return: the line number where to find the docstring in the soure file
        """
        search_startswith = []
        search_equal = []
        tgt_name = tokens[-1]
        start_line = 0
        if type_str == "@function":
            search_startswith.append("def %s(")
        elif type_str == "@class":
            search_startswith.append("class %s(")
            search_equal.append("class %s:")
        elif type_str in ("@method", "@property_getter"):
            start_line = cls.__get_line_number(file_lines, tokens[:-1], "@class")
            file_lines = file_lines[start_line:]
            search_startswith.append("def %s(")
        elif type_str == "@property_getter":
            start_line = cls.__get_line_number(file_lines, tokens[:-1], "@class")
            file_lines = file_lines[start_line:]
            search_equal.append("@%s.setter")

        if type_str != "@module":
            line_number = 0
            for i, file_line in enumerate(file_lines):
                file_line = file_line.strip()
                cond = False
                for key in search_startswith:
                    cond |= file_line.startswith(key % tgt_name)
                for key in search_equal:
                    cond |= file_line == (key % tgt_name)
                if cond:
                    line_number = i + 1
                    break

            res = start_line + line_number
        else:
            res = 1

        return res

    # ==================================================
    def __add_input_in_erorr_lines_set(self, new_input):
        """
        This method is designed to reset update the memory when an error points to a new doc line

        :type new_input: str
        :param new_input: a line pointing to the line of a docstring in a source file where there is an error
        """
        if self.__last_input_in_erorr_lines_set != "":
            prev_data = self.__complementary_data.setdefault(self.__last_input_in_erorr_lines_set, [])
            prev_data.extend(self.__tmp_lines)
            self.__tmp_lines = []
        self.__last_input_in_erorr_lines_set = new_input
        self.__erorr_lines_set.add(new_input)

    # ==========================================================================
    def __upadte_from_pointer_error_file_line(self, lib_path, splits, type_str):
        """
        This method is designed to update the memory when a new line pointing to an error is met in the error file

        :type lib_path: str
        :param lib_path: the path to the library where the doc error is to be found

        :type splits: list[str]
        :param splits: the import path to the error doc

        :type type_str: str
        :param type_str: the tag indiating the type of docstring (ex : @function, @method...)
        """
        del splits[0]
        text_path = self.__get_text_path(lib_path, splits)
        if text_path != "":
            file_lines = self.__get_source_file_lines(text_path)
            line_number = self.__get_line_number(file_lines, splits, type_str)
            new_input = 'File "%s", line %i' % (text_path, line_number)
            self.__add_input_in_erorr_lines_set(new_input)
            self.__tmp_lines.append("%s %s.%s" % (type_str, lib_path.split(os.sep)[-1], ".".join(splits)))

    # ============================================
    def __upadte_from_error_file_line(self, line):
        """
        This method is designed to update the memory for a new line of the error file

        :type line: str
        :param line: the line of the error file
        """
        line = line.strip()
        lib_path, splits, type_str = self.__lines_points_to_lib(line)
        if lib_path == "":
            self.__tmp_lines.append(line)
        else:
            self.__upadte_from_pointer_error_file_line(lib_path, splits, type_str)

    # ============
    def run(self):
        """
        This method is designed to print the errors of the error file by adding pointers to the error lines in the source files
        """
        self.__reset()
        error_file_lines = self.__get_error_file_lines()
        if len(error_file_lines) > 0:
            for line in error_file_lines:
                self.__upadte_from_error_file_line(line)
        self.__complementary_data.setdefault(self.__last_input_in_erorr_lines_set, []).extend(self.__tmp_lines)

        for elem in sorted(self.__erorr_lines_set):
            descr = self.__complementary_data.get(elem, [])
            if len(descr) > 0:
                print(descr[0])
                del descr[0]
            print(elem)
            if len(descr) > 0:
                print("\n".join(descr))

        self.__reset()


# ==================================================================================================
# FONCTIONS
# ==================================================================================================
