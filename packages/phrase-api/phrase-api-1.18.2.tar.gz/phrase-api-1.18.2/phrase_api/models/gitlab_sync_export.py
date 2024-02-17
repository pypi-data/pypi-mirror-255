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


class GitlabSyncExport(object):
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
        'merge_request_id': 'int',
        'merge_request_web_url': 'str'
    }

    attribute_map = {
        'merge_request_id': 'merge_request_id',
        'merge_request_web_url': 'merge_request_web_url'
    }

    def __init__(self, merge_request_id=None, merge_request_web_url=None, local_vars_configuration=None):  # noqa: E501
        """GitlabSyncExport - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._merge_request_id = None
        self._merge_request_web_url = None
        self.discriminator = None

        if merge_request_id is not None:
            self.merge_request_id = merge_request_id
        if merge_request_web_url is not None:
            self.merge_request_web_url = merge_request_web_url

    @property
    def merge_request_id(self):
        """Gets the merge_request_id of this GitlabSyncExport.  # noqa: E501


        :return: The merge_request_id of this GitlabSyncExport.  # noqa: E501
        :rtype: int
        """
        return self._merge_request_id

    @merge_request_id.setter
    def merge_request_id(self, merge_request_id):
        """Sets the merge_request_id of this GitlabSyncExport.


        :param merge_request_id: The merge_request_id of this GitlabSyncExport.  # noqa: E501
        :type: int
        """

        self._merge_request_id = merge_request_id

    @property
    def merge_request_web_url(self):
        """Gets the merge_request_web_url of this GitlabSyncExport.  # noqa: E501


        :return: The merge_request_web_url of this GitlabSyncExport.  # noqa: E501
        :rtype: str
        """
        return self._merge_request_web_url

    @merge_request_web_url.setter
    def merge_request_web_url(self, merge_request_web_url):
        """Sets the merge_request_web_url of this GitlabSyncExport.


        :param merge_request_web_url: The merge_request_web_url of this GitlabSyncExport.  # noqa: E501
        :type: str
        """

        self._merge_request_web_url = merge_request_web_url

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
        if not isinstance(other, GitlabSyncExport):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, GitlabSyncExport):
            return True

        return self.to_dict() != other.to_dict()
