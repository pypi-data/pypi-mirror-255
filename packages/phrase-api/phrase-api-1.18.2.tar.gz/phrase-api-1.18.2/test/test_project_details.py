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
from phrase_api.models.project_details import ProjectDetails  # noqa: E501
from phrase_api.rest import ApiException

class TestProjectDetails(unittest.TestCase):
    """ProjectDetails unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test ProjectDetails
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # model = phrase_api.models.project_details.ProjectDetails()  # noqa: E501

        """
        if include_optional :
            return ProjectDetails(
                id = '', 
                name = '', 
                slug = '', 
                main_format = '', 
                project_image_url = '', 
                media = '', 
                account = {"id":"abcd1234","name":"Company Account","slug":"company_account","company":"My Awesome Company","created_at":"2015-01-28T09:52:53Z","updated_at":"2015-01-28T09:52:53Z","company_logo_url":"http://assets.example.com/company_logo.png"}, 
                space = {"id":"2e7574e8f2372906a03110c2a7cfe671","name":"My first space","created_at":"2020-02-25T12:17:25Z","updated_at":"2020-03-13T14:46:57Z","projects_count":2}, 
                point_of_contact = phrase_api.models.user_preview.user_preview(
                    id = '', 
                    username = '', 
                    name = '', 
                    gravatar_uid = '', ), 
                created_at = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                updated_at = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                shares_translation_memory = True
            )
        else :
            return ProjectDetails(
        )
        """

    def testProjectDetails(self):
        """Test ProjectDetails"""
        inst_req_only = self.make_instance(include_optional=False)
        inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == '__main__':
    unittest.main()
