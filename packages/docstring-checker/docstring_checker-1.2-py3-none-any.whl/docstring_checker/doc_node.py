# coding=utf-8
"""
This module contains the DocNode class
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
from hierarchical_storage import HierarchicalNode


# ==================================================================================================
# INITIALISATIONS
# ==================================================================================================

# ==================================================================================================
# CLASSES
# ==================================================================================================

# ==============================
class DocNode(HierarchicalNode):
    """
    This class is dedicated to contain doc data for the different items of a project

    Class attributes:
    :type __categories: dict[str, dict[str, str]]
    :cvar __categories: dictionnary linking a node category to a dictionnary linking a generic tag to the matching node tag

    :type __parents_categories: dict[str, str]
    :cvar __parents_categories: dictionnary linking the category of a node the the category of its parent node. "", for None.

    :type __error_header_tags: dict[str, str]
    :cvar __error_header_tags: dictionnary linking a node category to the matching error tag in the error file.
    """
    __categories = {"root_node": {"name": "ProjectName"},
                    "MODULES": {"name": "ModuleName",
                                "docstring": "ModuleDoc"},
                    "CLASSES": {"name": "ClassName",
                                "docstring": "ClassDoc"},
                    "STATIC_METHODS": {"name": "SMethodName",
                                       "docstring": "SMethodDoc",
                                       "signature": "SMethodSignature"},
                    "CLASS_METHODS": {"name": "CMethodName",
                                      "docstring": "CMethodDoc",
                                      "signature": "CMethodSignature"},
                    "METHODS": {"name": "IMethodName",
                                "docstring": "IMethodDoc",
                                "signature": "IMethodSignature"},
                    "FUNCTIONS": {"name": "FunctionName",
                                  "docstring": "FunctionDoc",
                                  "signature": "FunctionSignature"}}

    __parents_categories = {"root_node": "",
                            "MODULES": "root_node",
                            "CLASSES": "MODULES",
                            "STATIC_METHODS": "CLASSES",
                            "CLASS_METHODS": "CLASSES",
                            "METHODS": "CLASSES",
                            "FUNCTIONS": "MODULES"}

    __error_header_tags = {"MODULES": "@module",
                           "CLASSES": "@class",
                           "FUNCTIONS": "@function",
                           "STATIC_METHODS": "@method",
                           "CLASS_METHODS": "@method"}

    # ==========
    @classmethod
    def __check_parent_category(cls, node_category, parent):
        """
        This method is designed to check if the node category of the node to create matches the node category of the parent node.
        If their is a mismatch, an exception is raised.

        :type node_category: str
        :param node_category: the node category of the node to create

        :type parent: NoneType | DocNode
        :param parent: the parent node
        """
        valid_parent_category = cls.__parents_categories.get(node_category, None)
        if valid_parent_category is not None:
            if parent is None:
                if valid_parent_category != "":
                    raise Exception("A %s node must have a parent node !" % node_category)
            else:
                if valid_parent_category == "":
                    raise Exception("A %s node must have no parent !" % node_category)

                parent_category = parent.get_node_category()
                if parent_category != valid_parent_category:
                    raise Exception("A %s node must have a %s parent !" % (node_category, valid_parent_category))

    # ==========
    @classmethod
    def get_property_getter_prefix(cls):
        """
        This method is designed to get the prefix for the name of property getter nodes

        :rtype: str
        :return: the prefix for the name of property getter nodes
        """
        return "(property.getter) "

    # ==========
    @classmethod
    def get_property_setter_prefix(cls):
        """
        This method is designed to get the prefix for the name of property setter nodes

        :rtype: str
        :return: the prefix for the name of property setter nodes
        """
        return "(property.setter) "

    # ===================================================
    def __init__(self, node_category, name, parent=None):
        """
        Initialization of a DocNode instance

        :type node_category: str
        :param node_category: the node category

        :type name: str
        :param name: the name of the node

        :type parent: NoneType | DocNode
        :param parent: the parent of the node
        """
        self.__check_parent_category(node_category, parent)
        super().__init__(node_category, name, parent=parent)

    # ===================================
    def get_allowed_child_category(self):
        """
        This method is designed to get the list of allowed child category (except doc, error and href)

        :rtype: list[str]
        :return: the list of allowed child category
        """
        res = []
        my_cat = self.get_node_category()
        for key, value in self.__parents_categories.items():
            if my_cat == value:
                res.append(key)

        return res

    # ============================
    def __get_tag(self, tag_name):
        """
        This method is designed to get a node tag from a generic tag name

        :type tag_name: str
        :param tag_name: the generic tag name

        :rtype: str
        :return: the node tag
        """
        category = self.get_node_category()
        sub_dict = self.__categories[category]

        return sub_dict[tag_name]

    # =====================
    def get_doc_name(self):
        """
        This method is designed to get the name mathcing the name tag

        :rtype: str
        :return: the name mathcing the name tag
        """
        tag = self.__get_tag("name")

        return self.get_data(tag)

    # =============================
    def set_doc_name(self, value):
        """
        This method is designed to set the name mathcing the name tag

        :type value: str
        :param value: the name mathcing the name tag
        """
        tag = self.__get_tag("name")

        self.set_data(tag, value)

    # ======================
    def get_docstring(self):
        """
        This method is designed to get the docstring recorded in the node

        :rtype: str
        :return: the docstring recorded in the node
        """
        tag = self.__get_tag("docstring")

        return self.get_data(tag)

    # =============================
    def set_docstring(self, value):
        """
        This method is designed to set the docstring recorded in the node

        :type value: str
        :param value: the docstring recorded in the node
        """
        tag = self.__get_tag("docstring")

        self.set_data(tag, value)

    # ======================
    def get_signature(self):
        """
        This method is designed to get the str signature recorded in the node

        :rtype: str
        :return: the str signature recorded in the node
        """
        tag = self.__get_tag("signature")

        return self.get_data(tag)

    # =============================
    def set_signature(self, value):
        """
        This method is designed to set the str signature recorded in the node

        :type value: str
        :param value: the str signature recorded in the node
        """
        tag = self.__get_tag("signature")

        self.set_data(tag, value)

    # ========================
    def get_module_node(self):
        """
        This method is designed to get the module node of this node

        :rtype: DocNode
        :return: the module node of this node
        """
        cur_cat = self.get_node_category()
        res = None
        if cur_cat != "root_node":
            res = self
            while cur_cat != "MODULES":
                res = res.get_parent()
                cur_cat = res.get_node_category()

        return res

    # ===============================
    def get_module_import_path(self):
        """
        This method is designed to get the import path of the module node of this node

        :rtype: str
        :return: the import path of the module node of this node
        """
        module_node = self.get_module_node()
        if module_node is None:
            res = ""
        else:
            res = module_node.get_data("ModuleImportPath")

        return res

    # ============================
    def get_doc_header_line(self):
        """
        This method is designed to get the error header of the node

        :rtype: str
        :return: the error header of the node
        """
        module_import_path = self.get_module_import_path()
        node_category = self.get_node_category()
        res = ""

        if node_category == "METHODS":
            name = self.get_doc_name()
            class_name = self.get_parent().get_doc_name()
            join_list = (module_import_path, class_name, name.split(" ")[-1])
            if name.startswith(self.get_property_getter_prefix()):
                tag = "@property_getter"
            elif name.startswith(self.get_property_setter_prefix()):
                tag = "@property_setter"
            else:
                tag = "@method"

        else:
            tag = self.__error_header_tags.get(node_category, "")
            if tag == "@module":
                join_list = module_import_path.split(".")
            else:
                join_list = (module_import_path, self.get_doc_name())

        if tag != "":
            res = "%s %s" % (tag, ".".join(join_list))

        return res


# ==================================================================================================
# FONCTIONS
# ==================================================================================================
