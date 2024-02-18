# coding=utf-8
"""
This module contains the StringType class
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

# ==================================================================================================
# FONCTIONS
# ==================================================================================================

# ==================================
class StringType(BaseDocstringType):
    """
    This class represents string docstrings
    """

    # ==========
    @classmethod
    def get_docstring_type(cls):
        """
        This method is designed to get the ID o the class for the factory

        :rtype: str
        :return: the ID o the class for the factory
        """
        return "String"

    # ==========================
    def rebuild_docstring(self):
        """
        This method is designed to rebuild the docstring from the content of the instance

        :rtype: str
        :return: the rebuilt docstring
        """
        return self.get_str_data()

    # ===========================
    def __get_type_strings(self):
        """
        This method is designed to get all the strings of types in this instance and sub instances, including basic types

        :rtype: set[str]
        :return: the strings of types in this instance and sub instances including basic types
        """
        res = set()
        res.add(self.get_str_data())

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
        return shift + "STRING " + self.get_str_data()

