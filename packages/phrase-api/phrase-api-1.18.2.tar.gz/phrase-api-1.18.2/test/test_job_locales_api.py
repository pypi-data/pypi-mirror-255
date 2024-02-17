# coding: utf-8

"""
    Phrase Strings API Reference

    The version of the OpenAPI document: 2.0.0
    Contact: support@phrase.com
    Generated by: https://openapi-generator.tech
"""


from __future__ import absolute_import

import unittest

import phrase_api
from phrase_api.api.job_locales_api import JobLocalesApi  # noqa: E501
from phrase_api.rest import ApiException


class TestJobLocalesApi(unittest.TestCase):
    """JobLocalesApi unit test stubs"""

    def setUp(self):
        self.api = phrase_api.api.job_locales_api.JobLocalesApi()  # noqa: E501

    def tearDown(self):
        pass

    def test_job_locale_complete(self):
        """Test case for job_locale_complete

        Complete a job locale  # noqa: E501
        """
        pass

    def test_job_locale_complete_review(self):
        """Test case for job_locale_complete_review

        Review a job locale  # noqa: E501
        """
        pass

    def test_job_locale_delete(self):
        """Test case for job_locale_delete

        Remove a target locale from a job  # noqa: E501
        """
        pass

    def test_job_locale_reopen(self):
        """Test case for job_locale_reopen

        Reopen a job locale  # noqa: E501
        """
        pass

    def test_job_locale_show(self):
        """Test case for job_locale_show

        Show single job target locale  # noqa: E501
        """
        pass

    def test_job_locale_update(self):
        """Test case for job_locale_update

        Update a job target locale  # noqa: E501
        """
        pass

    def test_job_locales_create(self):
        """Test case for job_locales_create

        Add a target locale to a job  # noqa: E501
        """
        pass

    def test_job_locales_list(self):
        """Test case for job_locales_list

        List job target locales  # noqa: E501
        """
        pass


if __name__ == '__main__':
    unittest.main()
