# coding=utf-8
"""
This module contains the FunctionType class
"""
from . import __author__, __email__, __version__, __maintainer__, __date__


# ==================================================================================================
# IMPORTS
# ==================================================================================================
from docstring_type_tag_checker.base_docstring_type import BaseDocstringType


# ==================================================================================================
# INITIALISATIONS
# ==================================================================================================

# ==================================================================================================
# CLASSES
# ==================================================================================================

# ====================================
class FunctionType(BaseDocstringType):
    """
    This class represents functions docstrings

    Class attributes:
    :type __scope_chars: list[str]
    :cvar __scope_chars: list of character begining a "group"

    :type __reversed_scope_char: list[str]
    :cvar __reversed_scope_char: list of character ending a "group". Same order as __scope_chars


    Instance attributes:
    :type __tuple_type: NoneType | docstring_type_tag_checker.docstring_types.tuple_type.TupleType
    :ivar __tuple_type: the BaseDocstringType instance for the arguments of the function

    :type __result_type: BaseDocstringType
    :ivar __result_type: the BaseDocstringType instance for the result of the function
    """
    __scope_chars = ["(", "["]
    __reversed_scope_char = [")", "]"]

    # ==========
    @classmethod
    def get_docstring_type(cls):
        """
        This method is designed to get the ID o the class for the factory

        :rtype: str
        :return: the ID o the class for the factory
        """
        return "Function"

    # ===========================
    def __init__(self, str_data):
        """
        Initialization of a FunctionType instance

        :type str_data: str
        :param str_data: the docstring
        """
        super().__init__(str_data)
        self.__tuple_type = None
        self.__result_type = None

        self.__init_from_str_data()

    # =============================
    def __init_from_str_data(self):
        """
        Method to be called to initialize the content of the instance from its docstring
        """
        try:
            tuple_str, result_str = self.__get_main_tokens()
        except Exception:
            self.__set_is_valid(False)
        else:
            factory = self.get_factory()
            self.__tuple_type = factory.get_instance_from_id("Tuple", tuple_str)
            self.__result_type = BaseDocstringType.get_type_object(result_str)

    # ==========================
    def __get_main_tokens(self):
        """
        This method is designed to get the main parts of the function docstring :
          - a tuple part with arguments types
          - a result part with the type of the result

        :rtype: (str, str)
        :return: a tuple part with arguments types, a result part with the type of the result
        """
        tuple_str = ""
        tmp_chars = []
        scopes = []
        in_first_tuple = True
        str_data = self.get_str_data()
        for char in str_data:
            if not in_first_tuple:
                tmp_chars.append(char)
            elif char in self.__scope_chars:
                scopes.append(char)
                tmp_chars.append(char)

            elif char in self.__reversed_scope_char:
                idx = self.__reversed_scope_char.index(char)
                test_char = self.__scope_chars[idx]
                tmp_chars.append(char)
                if (len(scopes) > 0) and (scopes[-1] == test_char):
                    del scopes[-1]
                    if len(scopes) == 0 and in_first_tuple:
                        in_first_tuple = False
                        tuple_str = "".join(tmp_chars)
                        tmp_chars = []
                else:
                    raise Exception("closing character '%s' does not match previous opening character !" % char)
            else:
                tmp_chars.append(char)

        if len(tmp_chars) > 0:
            result_str = "".join(tmp_chars).strip()
            if result_str[:2] == "->":
                result_str = result_str[2:]
            else:
                raise Exception("No '->' character after tuple for function type !")
        else:
            raise Exception("No '->' character after tuple for function type !")

        return tuple_str, result_str

    # ==========================
    def rebuild_docstring(self):
        """
        This method is designed to rebuild the docstring from the content of the instance

        :rtype: str
        :return: the rebuilt docstring
        """
        res = "%s -> %s" % (self.__tuple_type.rebuild_docstring(), self.__result_type.rebuild_docstring())

        return res

    # ==========================
    def __str__(self, shift=""):
        """
        Overloaded __str__ method

        :type shift: str
        :param shift: character used to shift the result to the right

        :rtype: str
        :return: an str representation of the isntance
        """
        res_list = [shift + "FUNCTION",
                    self.__tuple_type.__str__(shift + "    "),
                    self.__result_type.__str__(shift + "    ")]

        return "\n".join(res_list)

    # ===========================
    def __get_type_strings(self):
        """
        This method is designed to get all the strings of types in this instance and sub instances, including basic types

        :rtype: set[str]
        :return: the strings of types in this instance and sub instances including basic types
        """
        res = self.__tuple_type.get_type_strings(restrict=False)
        res = res.union(self.__result_type.get_type_strings(restrict=False))

        return res


# ==================================================================================================
# FONCTIONS
# ==================================================================================================
