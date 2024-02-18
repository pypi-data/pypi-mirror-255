# coding=utf-8
"""
This module contains the UnionType class
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

# =================================
class UnionType(BaseDocstringType):
    """
    This class represents union docstrings

    Class attributes:
    :type __scope_chars: list[str]
    :cvar __scope_chars: list of character begining a "group"

    :type __reversed_scope_char: list[str]
    :cvar __reversed_scope_char: list of character ending a "group". Same order as __scope_chars


    Instance attributes:
    :type __subtypes: list[BaseDocstringType]
    :ivar __subtypes: the subtypes of the union.
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
        return "Union"

    # ===========================
    def __init__(self, str_data):
        """
        Initialization of a UnionType instance

        :type str_data: str
        :param str_data: the docstring
        """
        super().__init__(str_data)
        self.__subtypes = []

        self.__init_from_str_data()

    # =============================
    def __init_from_str_data(self):
        """
        Method to be called to initialize the content of the instance from its docstring
        """
        try:
            tokens = self.__get_tokens()
        except Exception:
            factory = self.get_factory()
            self.__subtypes.append(factory.get_instance_from_id("String", self.get_str_data()))
            self.__set_is_valid(False)
        else:
            for token in tokens:
                self.__subtypes.append(BaseDocstringType.get_type_object(token))

    # =====================
    def __get_tokens(self):
        """
        This method is designed to get the parts for the subtypes of the union

        :rtype: list[str]
        :return: the parts for the subtypes of the union
        """
        tokens = []
        tmp_chars = []
        scopes = []
        for char in self.get_str_data():
            if char in self.__scope_chars:
                scopes.append(char)
                tmp_chars.append(char)

            elif char in self.__reversed_scope_char:
                idx = self.__reversed_scope_char.index(char)
                test_char = self.__scope_chars[idx]
                tmp_chars.append(char)
                if (len(scopes) > 0) and (scopes[-1] == test_char):
                    del scopes[-1]
                else:
                    raise Exception("closing character '%s' does not match previous opening character !" % char)

            elif (len(scopes) == 0) and (char == "|"):
                if len(tmp_chars) > 0:
                    tokens.append("".join(tmp_chars).strip())
                    tmp_chars = []

            else:
                tmp_chars.append(char)

        if len(tmp_chars) > 0:
            tokens.append("".join(tmp_chars).strip())

        return tokens

    # ==========================
    def rebuild_docstring(self):
        """
        This method is designed to rebuild the docstring from the content of the instance

        :rtype: str
        :return: the rebuilt docstring
        """
        res = " | ".join([elem.rebuild_docstring() for elem in self.__subtypes])

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
        res_list = [elem.__str__(shift + "    ") for elem in self.__subtypes]
        res_list.insert(0, shift + "UNION")

        return "\n".join(res_list)

    # ===========================
    def __get_type_strings(self):
        """
        This method is designed to get all the strings of types in this instance and sub instances, including basic types

        :rtype: set[str]
        :return: the strings of types in this instance and sub instances including basic types
        """
        res = set()
        for elem in self.__subtypes:
            res = res.union(elem.get_type_strings(restrict=False))

        return res


# ==================================================================================================
# FONCTIONS
# ==================================================================================================
