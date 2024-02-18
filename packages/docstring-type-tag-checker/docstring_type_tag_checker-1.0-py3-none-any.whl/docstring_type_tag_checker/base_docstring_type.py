# coding=utf-8
"""
This module contains the class BaseDocstringType
"""
from . import __author__, __email__, __version__, __maintainer__, __date__


# ==================================================================================================
# IMPORTS
# ==================================================================================================
import os
import builtins
from protected_method_metaclass import Protected
from class_factory import ClassFactoryUser


# ==================================================================================================
# INITIALISATIONS
# ==================================================================================================

# ==================================================================================================
# CLASSES
# ==================================================================================================

# ========================================
class BaseDocstringType(ClassFactoryUser):
    """
    Base class for all types of docstring

    Class attributes:
    :type __basic_types: set[str]
    :cvar __basic_types: set of all name of types that must be considered as known (built essentially from builtins)

    :type __base_basic_types: set[str]
    :cvar __base_basic_types: set of names used as types in docstring but not known in builtins


    Instance attributes:
    :type __str_data: str
    :ivar __str_data: the analyzed docstring

    :type __is_valid: bool
    :ivar __is_valid: True if the docstring is valid, False otherwise
    """
    __basic_types = set()
    __base_basic_types = {"NoneType", "any"}

    # ==========
    @classmethod
    def get_type_object(cls, str_data):
        """
        This method is designed to get an instance of a subclass of BaseDocstringType for a docstring

        :type str_data: str
        :param str_data: the analyzed docstring

        :rtype: BaseDocstringType
        :return: the instance of a subclass of BaseDocstringType for the docstring
        """
        str_data = str_data.strip()
        factory = cls.get_factory()
        special_idx, special_char = cls.__get_first_special_char(str_data)
        if special_char == "[":
            end_group_char_index = cls.__get_end_group_char_index(str_data, special_idx, "[", "]")
            if end_group_char_index == len(str_data) - 1:
                res = factory.get_instance_from_id("Generic", str_data)
            else:
                _, special_char2 = cls.__get_first_special_char(str_data[end_group_char_index + 1:])
                if special_char2 == "|":
                    res = factory.get_instance_from_id("Union", str_data)
                else:
                    res = factory.get_instance_from_id("String", str_data)
        elif (special_char == "(") and (special_idx == 0):
            end_group_char_index = cls.__get_end_group_char_index(str_data, special_idx, "(", ")")
            if end_group_char_index == len(str_data) - 1:
                res = factory.get_instance_from_id("Tuple", str_data)
            elif str_data[end_group_char_index + 1:].strip()[:2] == "->":
                res = factory.get_instance_from_id("Function", str_data)
            else:
                _, special_char2 = cls.__get_first_special_char(str_data[end_group_char_index + 1:])
                if special_char2 == "|":
                    res = factory.get_instance_from_id("Union", str_data)
                else:
                    res = factory.get_instance_from_id("String", str_data)
        elif special_char == "|":
            res = factory.get_instance_from_id("Union", str_data)
        else:
            res = factory.get_instance_from_id("String", str_data)

        return res

    # ==========
    @classmethod
    def __get_first_special_char(cls, str_data):
        """
        This method is designed to get the first special character found in docstring

        :type str_data: str
        :param str_data: the docstring

        :rtype: (int | str)
        :return: the position of the first special character and the character
        """
        special_idx = -1
        special_char = ""
        for char in ("[", "(", ",", "|"):
            try:
                idx = str_data.index(char)
            except ValueError:
                pass
            else:
                if (special_idx == -1) or (idx < special_idx):
                    special_char = char
                    special_idx = idx

        return special_idx, special_char

    # ==========
    @classmethod
    def __get_end_group_char_index(cls, str_data, start_idx, start_char, end_char):
        """
        This method is designed to get the index of a character ending a group in a docstring

        :type str_data: str
        :param str_data: the docstring

        :type start_idx: int
        :param start_idx: position from which analysis begins (usualy matches start_char)

        :type start_char: str
        :param start_char: the character starting the group (ex : "( "or "[" )

        :type end_char: str
        :param end_char: the character ending the group (ex : ")" or "]" )

        :rtype: int
        :return: the index of the character ending the group in the docstring
        """
        data_dict = {start_char: 1,
                     end_char: -1}
        level = 0
        i_found = -1
        for i, char in enumerate(str_data[start_idx:]):
            level += data_dict.get(char, 0)
            if level == 0:
                i_found = i + start_idx
                break

        return i_found

    # ===========================
    def __init__(self, str_data):
        """
        Initialization of a BaseDocstringType instance

        :type str_data: str
        :param str_data: the docstring
        """
        self.__str_data = str_data.strip()
        self.__is_valid = True

    # =============================
    def __init_from_str_data(self):
        """
        Method to be called to initialize the content of the instance from its docstring
        """
        pass

    # =====================
    def get_str_data(self):
        """
        This method is designed to get the docstring

        :rtype: str
        :return: the docstring
        """
        return self.__str_data

    # =================
    def is_valid(self):
        """
        This method is designed to check if the docstring is valid

        :rtype: bool
        :return: True if the docstring is valid, False otherwise
        """
        return self.__is_valid

    # ========
    @Protected
    def __set_is_valid(self, value):
        """
        This method is designed to update the validity of the docstring

        :type value: bool
        :param value: True if the docstring is valid, False otherwise
        """
        self.__is_valid = value

    # ==========
    @classmethod
    def __get_factory_id(cls):
        """
        This method is designed to get the ID of the factory dedicated to this class
        The name of the directory where subclasses are to be found is a good idea

        :rtype: str
        :return: the ID of the factory dedicated to this class
        """
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "docstring_types")

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
        import_path = cls.__get_factory_id()
        format_name = "*.py"
        import_val = "docstring_type_tag_checker.docstring_types"

        return [(import_path, import_val, format_name)]

    # ==========
    @classmethod
    def __get_base_class_for_factory(cls):
        """
        This method is designed to get the base class for the factory

        :rtype: type
        :return: the base class for the factory
        """
        return BaseDocstringType

    # ==========
    @classmethod
    def __get_id_function_name_for_factory(cls):
        """
        This method is designed to get the name of the method returning the ID of the class for the factory

        :rtype: str
        :return: the name of the method returning the ID of the class for the factory
        """
        return "get_docstring_type"

    # ==========================
    def rebuild_docstring(self):
        """
        This method is designed to rebuild the docstring from the content of the instance

        :rtype: str
        :return: the rebuilt docstring
        """
        msg = "The method 'rebuild_docstring' is not overloaded for class %s !" % str(self.__class__)
        raise NotImplementedError(msg)

    # ========================================
    def get_type_strings(self, restrict=True):
        """
        This method is designed to get all the strings of types in this instance and sub instances

        :type restrict: bool
        :param restrict: If True, basic types are removed from the result, otherwise they are kept

        :rtype: set[str]
        :return: the strings of types in this instance and sub instances
        """
        res = self.__get_type_strings()
        if restrict:
            res = res.difference(self.__get_basic_types())

        return res

    # ========
    @Protected
    def __get_type_strings(self):
        """
        This method is designed to get all the strings of types in this instance and sub instances, including basic types

        :rtype: set[str]
        :return: the strings of types in this instance and sub instances including basic types
        """
        msg = "The method '__get_type_strings' is not overloaded for class %s !" % str(self.__class__)
        raise NotImplementedError(msg)

    # ========
    @Protected
    @classmethod
    def __get_basic_types(cls):
        """
        This method is designed to get all the names of types that must be considered as known (mostly built from builtins)
        It is a protected method used as shortcut to __cur_get_basic_types which is not protected but private

        :rtype: set[str]
        :return: all the names of types that must be considered as known (mostly built from builtins)
        """
        return cls.__cur_get_basic_types()

    # ==========
    @classmethod
    def __first_get_basic_types(cls):
        """
        This methos is called the first time __cur_get_basic_types is called.
        It initializes __basic_types from builtins and then have __cur_get_basic_types point to __next_get_basic_types

        :rtype: set[str]
        :return: all the names of types that must be considered as known (mostly built from builtins)
        """
        for key, value in builtins.__dict__.items():
            if isinstance(value, type):
                cls.__basic_types.add(key)
        cls.__basic_types = cls.__basic_types.union(cls.__base_basic_types)
        cls.__cur_get_basic_types = cls.__next_get_basic_types

        return cls.__basic_types

    # ==========
    @classmethod
    def __next_get_basic_types(cls):
        """
        This method is designed to get all the names of types that must be considered as known (mostly built from builtins)

        :rtype: set[str]
        :return: all the names of types that must be considered as known (mostly built from builtins)
        """
        return cls.__basic_types

    __cur_get_basic_types = __first_get_basic_types

    # ==========================
    def __str__(self, shift=""):
        """
        Overloaded __str__ method (used for signature and typing)

        :type shift: str
        :param shift: character used to shift the result to the right

        :rtype: str
        :return: an str representation of the isntance
        """
        return super().__str__()

# ==================================================================================================
# FONCTIONS
# ==================================================================================================
