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
from phrase_api.models.projects_quality_performance_score200_response_any_of_data import ProjectsQualityPerformanceScore200ResponseAnyOfData  # noqa: E501
from phrase_api.rest import ApiException

class TestProjectsQualityPerformanceScore200ResponseAnyOfData(unittest.TestCase):
    """ProjectsQualityPerformanceScore200ResponseAnyOfData unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test ProjectsQualityPerformanceScore200ResponseAnyOfData
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # model = phrase_api.models.projects_quality_performance_score200_response_any_of_data.ProjectsQualityPerformanceScore200ResponseAnyOfData()  # noqa: E501

        """
        if include_optional :
            return ProjectsQualityPerformanceScore200ResponseAnyOfData(
                translations = [
                    phrase_api.models.projects_quality_performance_score_200_response_any_of_data_translations_inner.projects_quality_performance_score_200_response_anyOf_data_translations_inner(
                        engine = '', 
                        score = 1.337, 
                        id = '', )
                    ]
            )
        else :
            return ProjectsQualityPerformanceScore200ResponseAnyOfData(
        )
        """

    def testProjectsQualityPerformanceScore200ResponseAnyOfData(self):
        """Test ProjectsQualityPerformanceScore200ResponseAnyOfData"""
        inst_req_only = self.make_instance(include_optional=False)
        inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == '__main__':
    unittest.main()
