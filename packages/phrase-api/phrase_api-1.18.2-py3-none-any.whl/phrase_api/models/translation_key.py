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


class TranslationKey(object):
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
        'id': 'str',
        'name': 'str',
        'description': 'str',
        'name_hash': 'str',
        'plural': 'bool',
        'tags': 'List[str]',
        'data_type': 'str',
        'created_at': 'datetime',
        'updated_at': 'datetime'
    }

    attribute_map = {
        'id': 'id',
        'name': 'name',
        'description': 'description',
        'name_hash': 'name_hash',
        'plural': 'plural',
        'tags': 'tags',
        'data_type': 'data_type',
        'created_at': 'created_at',
        'updated_at': 'updated_at'
    }

    def __init__(self, id=None, name=None, description=None, name_hash=None, plural=None, tags=None, data_type=None, created_at=None, updated_at=None, local_vars_configuration=None):  # noqa: E501
        """TranslationKey - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._id = None
        self._name = None
        self._description = None
        self._name_hash = None
        self._plural = None
        self._tags = None
        self._data_type = None
        self._created_at = None
        self._updated_at = None
        self.discriminator = None

        if id is not None:
            self.id = id
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        if name_hash is not None:
            self.name_hash = name_hash
        if plural is not None:
            self.plural = plural
        if tags is not None:
            self.tags = tags
        if data_type is not None:
            self.data_type = data_type
        if created_at is not None:
            self.created_at = created_at
        if updated_at is not None:
            self.updated_at = updated_at

    @property
    def id(self):
        """Gets the id of this TranslationKey.  # noqa: E501


        :return: The id of this TranslationKey.  # noqa: E501
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this TranslationKey.


        :param id: The id of this TranslationKey.  # noqa: E501
        :type: str
        """

        self._id = id

    @property
    def name(self):
        """Gets the name of this TranslationKey.  # noqa: E501


        :return: The name of this TranslationKey.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this TranslationKey.


        :param name: The name of this TranslationKey.  # noqa: E501
        :type: str
        """

        self._name = name

    @property
    def description(self):
        """Gets the description of this TranslationKey.  # noqa: E501


        :return: The description of this TranslationKey.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this TranslationKey.


        :param description: The description of this TranslationKey.  # noqa: E501
        :type: str
        """

        self._description = description

    @property
    def name_hash(self):
        """Gets the name_hash of this TranslationKey.  # noqa: E501


        :return: The name_hash of this TranslationKey.  # noqa: E501
        :rtype: str
        """
        return self._name_hash

    @name_hash.setter
    def name_hash(self, name_hash):
        """Sets the name_hash of this TranslationKey.


        :param name_hash: The name_hash of this TranslationKey.  # noqa: E501
        :type: str
        """

        self._name_hash = name_hash

    @property
    def plural(self):
        """Gets the plural of this TranslationKey.  # noqa: E501


        :return: The plural of this TranslationKey.  # noqa: E501
        :rtype: bool
        """
        return self._plural

    @plural.setter
    def plural(self, plural):
        """Sets the plural of this TranslationKey.


        :param plural: The plural of this TranslationKey.  # noqa: E501
        :type: bool
        """

        self._plural = plural

    @property
    def tags(self):
        """Gets the tags of this TranslationKey.  # noqa: E501


        :return: The tags of this TranslationKey.  # noqa: E501
        :rtype: List[str]
        """
        return self._tags

    @tags.setter
    def tags(self, tags):
        """Sets the tags of this TranslationKey.


        :param tags: The tags of this TranslationKey.  # noqa: E501
        :type: List[str]
        """

        self._tags = tags

    @property
    def data_type(self):
        """Gets the data_type of this TranslationKey.  # noqa: E501


        :return: The data_type of this TranslationKey.  # noqa: E501
        :rtype: str
        """
        return self._data_type

    @data_type.setter
    def data_type(self, data_type):
        """Sets the data_type of this TranslationKey.


        :param data_type: The data_type of this TranslationKey.  # noqa: E501
        :type: str
        """

        self._data_type = data_type

    @property
    def created_at(self):
        """Gets the created_at of this TranslationKey.  # noqa: E501


        :return: The created_at of this TranslationKey.  # noqa: E501
        :rtype: datetime
        """
        return self._created_at

    @created_at.setter
    def created_at(self, created_at):
        """Sets the created_at of this TranslationKey.


        :param created_at: The created_at of this TranslationKey.  # noqa: E501
        :type: datetime
        """

        self._created_at = created_at

    @property
    def updated_at(self):
        """Gets the updated_at of this TranslationKey.  # noqa: E501


        :return: The updated_at of this TranslationKey.  # noqa: E501
        :rtype: datetime
        """
        return self._updated_at

    @updated_at.setter
    def updated_at(self, updated_at):
        """Sets the updated_at of this TranslationKey.


        :param updated_at: The updated_at of this TranslationKey.  # noqa: E501
        :type: datetime
        """

        self._updated_at = updated_at

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
        if not isinstance(other, TranslationKey):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, TranslationKey):
            return True

        return self.to_dict() != other.to_dict()
