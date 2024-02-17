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
from phrase_api.models.locale_create_parameters import LocaleCreateParameters  # noqa: E501
from phrase_api.rest import ApiException

class TestLocaleCreateParameters(unittest.TestCase):
    """LocaleCreateParameters unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test LocaleCreateParameters
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # model = phrase_api.models.locale_create_parameters.LocaleCreateParameters()  # noqa: E501

        """
        if include_optional :
            return LocaleCreateParameters(
                branch = 'my-feature-branch', 
                name = 'de', 
                code = 'de-DE', 
                default = True, 
                main = True, 
                rtl = True, 
                source_locale_id = 'abcd1234abcd1234abcd1234abcd1234', 
                fallback_locale_id = 'abcd1234abcd1234abcd1234abcd1234', 
                unverify_new_translations = True, 
                unverify_updated_translations = True, 
                autotranslate = True
            )
        else :
            return LocaleCreateParameters(
        )
        """

    def testLocaleCreateParameters(self):
        """Test LocaleCreateParameters"""
        inst_req_only = self.make_instance(include_optional=False)
        inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == '__main__':
    unittest.main()
