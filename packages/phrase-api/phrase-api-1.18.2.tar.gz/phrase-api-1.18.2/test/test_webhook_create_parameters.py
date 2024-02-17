# coding: utf-8

"""
    Phrase Strings API Reference

    The version of the OpenAPI document: 2.0.0
    Contact: support@phrase.com
    Generated by: https://openapi-generator.tech
"""


from __future__ import absolute_import

import unittest
import datetime

import phrase_api
from phrase_api.models.webhook_create_parameters import WebhookCreateParameters  # noqa: E501
from phrase_api.rest import ApiException

class TestWebhookCreateParameters(unittest.TestCase):
    """WebhookCreateParameters unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test WebhookCreateParameters
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # model = phrase_api.models.webhook_create_parameters.WebhookCreateParameters()  # noqa: E501

        """
        if include_optional :
            return WebhookCreateParameters(
                callback_url = 'http://example.com/hooks/phraseapp-notifications', 
                secret = 'secr3t', 
                description = 'My webhook for chat notifications', 
                events = 'locales:create,translations:update', 
                active = True, 
                include_branches = True
            )
        else :
            return WebhookCreateParameters(
        )
        """

    def testWebhookCreateParameters(self):
        """Test WebhookCreateParameters"""
        inst_req_only = self.make_instance(include_optional=False)
        inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == '__main__':
    unittest.main()
