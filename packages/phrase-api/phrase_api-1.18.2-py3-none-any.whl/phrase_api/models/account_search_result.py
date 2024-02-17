# coding: utf-8

"""
    Phrase Strings API Reference

    The version of the OpenAPI document: 2.0.0
    Contact: support@phrase.com
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from phrase_api.configuration import Configuration


class AccountSearchResult(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'query': 'str',
        'excerpt': 'str',
        'key': 'KeyPreview',
        'locale': 'LocalePreview',
        'project': 'Project',
        'translation': 'Translation',
        'other_translations': 'List[Translation]'
    }

    attribute_map = {
        'query': 'query',
        'excerpt': 'excerpt',
        'key': 'key',
        'locale': 'locale',
        'project': 'project',
        'translation': 'translation',
        'other_translations': 'other_translations'
    }

    def __init__(self, query=None, excerpt=None, key=None, locale=None, project=None, translation=None, other_translations=None, local_vars_configuration=None):  # noqa: E501
        """AccountSearchResult - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._query = None
        self._excerpt = None
        self._key = None
        self._locale = None
        self._project = None
        self._translation = None
        self._other_translations = None
        self.discriminator = None

        if query is not None:
            self.query = query
        if excerpt is not None:
            self.excerpt = excerpt
        if key is not None:
            self.key = key
        if locale is not None:
            self.locale = locale
        if project is not None:
            self.project = project
        if translation is not None:
            self.translation = translation
        if other_translations is not None:
            self.other_translations = other_translations

    @property
    def query(self):
        """Gets the query of this AccountSearchResult.  # noqa: E501


        :return: The query of this AccountSearchResult.  # noqa: E501
        :rtype: str
        """
        return self._query

    @query.setter
    def query(self, query):
        """Sets the query of this AccountSearchResult.


        :param query: The query of this AccountSearchResult.  # noqa: E501
        :type: str
        """

        self._query = query

    @property
    def excerpt(self):
        """Gets the excerpt of this AccountSearchResult.  # noqa: E501


        :return: The excerpt of this AccountSearchResult.  # noqa: E501
        :rtype: str
        """
        return self._excerpt

    @excerpt.setter
    def excerpt(self, excerpt):
        """Sets the excerpt of this AccountSearchResult.


        :param excerpt: The excerpt of this AccountSearchResult.  # noqa: E501
        :type: str
        """

        self._excerpt = excerpt

    @property
    def key(self):
        """Gets the key of this AccountSearchResult.  # noqa: E501


        :return: The key of this AccountSearchResult.  # noqa: E501
        :rtype: KeyPreview
        """
        return self._key

    @key.setter
    def key(self, key):
        """Sets the key of this AccountSearchResult.


        :param key: The key of this AccountSearchResult.  # noqa: E501
        :type: KeyPreview
        """

        self._key = key

    @property
    def locale(self):
        """Gets the locale of this AccountSearchResult.  # noqa: E501


        :return: The locale of this AccountSearchResult.  # noqa: E501
        :rtype: LocalePreview
        """
        return self._locale

    @locale.setter
    def locale(self, locale):
        """Sets the locale of this AccountSearchResult.


        :param locale: The locale of this AccountSearchResult.  # noqa: E501
        :type: LocalePreview
        """

        self._locale = locale

    @property
    def project(self):
        """Gets the project of this AccountSearchResult.  # noqa: E501


        :return: The project of this AccountSearchResult.  # noqa: E501
        :rtype: Project
        """
        return self._project

    @project.setter
    def project(self, project):
        """Sets the project of this AccountSearchResult.


        :param project: The project of this AccountSearchResult.  # noqa: E501
        :type: Project
        """

        self._project = project

    @property
    def translation(self):
        """Gets the translation of this AccountSearchResult.  # noqa: E501


        :return: The translation of this AccountSearchResult.  # noqa: E501
        :rtype: Translation
        """
        return self._translation

    @translation.setter
    def translation(self, translation):
        """Sets the translation of this AccountSearchResult.


        :param translation: The translation of this AccountSearchResult.  # noqa: E501
        :type: Translation
        """

        self._translation = translation

    @property
    def other_translations(self):
        """Gets the other_translations of this AccountSearchResult.  # noqa: E501


        :return: The other_translations of this AccountSearchResult.  # noqa: E501
        :rtype: List[Translation]
        """
        return self._other_translations

    @other_translations.setter
    def other_translations(self, other_translations):
        """Sets the other_translations of this AccountSearchResult.


        :param other_translations: The other_translations of this AccountSearchResult.  # noqa: E501
        :type: List[Translation]
        """

        self._other_translations = other_translations

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, AccountSearchResult):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, AccountSearchResult):
            return True

        return self.to_dict() != other.to_dict()
