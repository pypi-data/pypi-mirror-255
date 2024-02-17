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


class Comment(object):
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
        'message': 'str',
        'has_replies': 'bool',
        'user': 'UserPreview',
        'created_at': 'datetime',
        'updated_at': 'datetime',
        'mentioned_users': 'List[UserPreview]',
        'locales': 'List[LocalePreview]'
    }

    attribute_map = {
        'id': 'id',
        'message': 'message',
        'has_replies': 'has_replies',
        'user': 'user',
        'created_at': 'created_at',
        'updated_at': 'updated_at',
        'mentioned_users': 'mentioned_users',
        'locales': 'locales'
    }

    def __init__(self, id=None, message=None, has_replies=None, user=None, created_at=None, updated_at=None, mentioned_users=None, locales=None, local_vars_configuration=None):  # noqa: E501
        """Comment - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._id = None
        self._message = None
        self._has_replies = None
        self._user = None
        self._created_at = None
        self._updated_at = None
        self._mentioned_users = None
        self._locales = None
        self.discriminator = None

        if id is not None:
            self.id = id
        if message is not None:
            self.message = message
        if has_replies is not None:
            self.has_replies = has_replies
        if user is not None:
            self.user = user
        if created_at is not None:
            self.created_at = created_at
        if updated_at is not None:
            self.updated_at = updated_at
        if mentioned_users is not None:
            self.mentioned_users = mentioned_users
        if locales is not None:
            self.locales = locales

    @property
    def id(self):
        """Gets the id of this Comment.  # noqa: E501


        :return: The id of this Comment.  # noqa: E501
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this Comment.


        :param id: The id of this Comment.  # noqa: E501
        :type: str
        """

        self._id = id

    @property
    def message(self):
        """Gets the message of this Comment.  # noqa: E501


        :return: The message of this Comment.  # noqa: E501
        :rtype: str
        """
        return self._message

    @message.setter
    def message(self, message):
        """Sets the message of this Comment.


        :param message: The message of this Comment.  # noqa: E501
        :type: str
        """

        self._message = message

    @property
    def has_replies(self):
        """Gets the has_replies of this Comment.  # noqa: E501


        :return: The has_replies of this Comment.  # noqa: E501
        :rtype: bool
        """
        return self._has_replies

    @has_replies.setter
    def has_replies(self, has_replies):
        """Sets the has_replies of this Comment.


        :param has_replies: The has_replies of this Comment.  # noqa: E501
        :type: bool
        """

        self._has_replies = has_replies

    @property
    def user(self):
        """Gets the user of this Comment.  # noqa: E501


        :return: The user of this Comment.  # noqa: E501
        :rtype: UserPreview
        """
        return self._user

    @user.setter
    def user(self, user):
        """Sets the user of this Comment.


        :param user: The user of this Comment.  # noqa: E501
        :type: UserPreview
        """

        self._user = user

    @property
    def created_at(self):
        """Gets the created_at of this Comment.  # noqa: E501


        :return: The created_at of this Comment.  # noqa: E501
        :rtype: datetime
        """
        return self._created_at

    @created_at.setter
    def created_at(self, created_at):
        """Sets the created_at of this Comment.


        :param created_at: The created_at of this Comment.  # noqa: E501
        :type: datetime
        """

        self._created_at = created_at

    @property
    def updated_at(self):
        """Gets the updated_at of this Comment.  # noqa: E501


        :return: The updated_at of this Comment.  # noqa: E501
        :rtype: datetime
        """
        return self._updated_at

    @updated_at.setter
    def updated_at(self, updated_at):
        """Sets the updated_at of this Comment.


        :param updated_at: The updated_at of this Comment.  # noqa: E501
        :type: datetime
        """

        self._updated_at = updated_at

    @property
    def mentioned_users(self):
        """Gets the mentioned_users of this Comment.  # noqa: E501


        :return: The mentioned_users of this Comment.  # noqa: E501
        :rtype: List[UserPreview]
        """
        return self._mentioned_users

    @mentioned_users.setter
    def mentioned_users(self, mentioned_users):
        """Sets the mentioned_users of this Comment.


        :param mentioned_users: The mentioned_users of this Comment.  # noqa: E501
        :type: List[UserPreview]
        """

        self._mentioned_users = mentioned_users

    @property
    def locales(self):
        """Gets the locales of this Comment.  # noqa: E501


        :return: The locales of this Comment.  # noqa: E501
        :rtype: List[LocalePreview]
        """
        return self._locales

    @locales.setter
    def locales(self, locales):
        """Sets the locales of this Comment.


        :param locales: The locales of this Comment.  # noqa: E501
        :type: List[LocalePreview]
        """

        self._locales = locales

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
        if not isinstance(other, Comment):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, Comment):
            return True

        return self.to_dict() != other.to_dict()
