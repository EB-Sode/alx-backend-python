#!/usr/bin/env python3
"""Unit and integration tests for the GithubOrgClient."""
import unittest
from unittest import mock
from parameterized import parameterized
from client import GithubOrgClient

class TestGithubOrgClient(unittest.TestCase):
    """Tests for GithubOrgClient"""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @mock.patch('client.get_json')
    def test_org(self, org_name, mock_get_json):
        """Test that .org returns the expected payload"""
        test_payload = {"payload": True}
        mock_get_json.return_value = test_payload

        client = GithubOrgClient(org_name)
        self.assertEqual(client.org, test_payload)

        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )
