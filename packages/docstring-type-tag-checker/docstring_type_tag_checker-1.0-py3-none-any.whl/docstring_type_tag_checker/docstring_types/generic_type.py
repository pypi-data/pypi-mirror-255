# coding=utf-8
"""
This module contains the GenericType class
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

# ===================================
class GenericType(BaseDocstringType):
    """
    This class represents generic types docstrings

    Class attributes:
    :type __scope_chars: list[str]
    :cvar __scope_chars: list of character begining a "group"

    :type __reversed_scope_char: list[str]
    :cvar __reversed_scope_char: list of character ending a "group". Same order as __scope_chars


    Instance attributes:
    :type __name: str
    :ivar __name: the name / import path of the Generic type

    :type __subtypes: list[BaseDocstringType]
    :ivar __subtypes: the subtypes of the Generic type. Ex : dict[str, int] ==> (str, int)
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
        return "Generic"

    # ===========================
    def __init__(self, str_data):
        """
        Initialization of a GenericType instance

        :type str_data: str
        :param str_data: the docstring
        """
        super().__init__(str_data)
        self.__name = ""
        self.__subtypes = []

        self.__init_from_str_data()

    # =============================
    def __init_from_str_data(self):
        """
        Method to be called to initialize the content of the instance from its docstring
        """
        self.__name = self.get_str_data().split('[')[0]
        try:
            name, tokens = self.__get_name_and_tokens()
        except Exception:
            factory = self.get_factory()
            self.__subtypes.append(factory.get_instance_from_id("String", self.get_str_data()[1:-1]))
            self.__set_is_valid(False)
        else:
            self.__name = name
            for token in tokens:
                self.__subtypes.append(BaseDocstringType.get_type_object(token))

    # ==============================
    def __get_name_and_tokens(self):
        """
        This method is designed to get the main parts of the generic docstring :
          - a name part with the name/import path of the generic type
          - the parts for the subtypes of the generic type

        :rtype: (str, list[str])
        :return: a name part with the name/import path of the generic type, the parts for the subtypes of the generic type
        """
        str_data = self.get_str_data()
        idx = str_data.index("[")
        name = str_data[:idx]

        tokens = []
        tmp_chars = []
        scopes = []
        for char in self.get_str_data()[idx+1:-1]:
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

            elif (len(scopes) == 0) and (char == ","):
                if len(tmp_chars) > 0:
                    tokens.append("".join(tmp_chars).strip())
                    tmp_chars = []

            else:
                tmp_chars.append(char)

        if len(tmp_chars) > 0:
            tokens.append("".join(tmp_chars).strip())

        return name, tokens

    # ==========================
    def rebuild_docstring(self):
        """
        This method is designed to rebuild the docstring from the content of the instance

        :rtype: str
        :return: the rebuilt docstring
        """
        res = "%s[%s]" % (self.__name, ", ".join([elem.rebuild_docstring() for elem in self.__subtypes]))

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
        res_list.insert(0, shift + "GENERIC[%s]" % self.__name)

        return "\n".join(res_list)

    # ===========================
    def __get_type_strings(self):
        """
        This method is designed to get all the strings of types in this instance and sub instances, including basic types

        :rtype: set[str]
        :return: the strings of types in this instance and sub instances including basic types
        """
        res = set()
        res.add(self.__name)
        for elem in self.__subtypes:
            res = res.union(elem.get_type_strings(restrict=False))

        return res


# ==================================================================================================
# FONCTIONS
# ==================================================================================================
