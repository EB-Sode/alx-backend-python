#!/usr/bin/env python3
"""Unit and integration tests for the GithubOrgClient."""
import unittest
from unittest import mock
from parameterized import parameterized
from parameterized import parameterized_class
from client import GithubOrgClient
from unittest.mock import patch, PropertyMock
from fixtures import TEST_PAYLOAD


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

    def test_public_repos_url(self):
        """Test that _public_repos_url returns repos_url from org payload"""
        test_payload = {
            "repos_url": "https://api.github.com/orgs/test-org/repos"
            }

        with mock.patch.object(
            GithubOrgClient, "org",
                new_callable=unittest.mock.PropertyMock
        ) as mock_org:
            mock_org.return_value = test_payload
            client = GithubOrgClient("test-org")

            result = client._public_repos_url
            self.assertEqual(result, test_payload["repos_url"])

            # mock_org.assert_called_once()

    @patch("client.get_json")
    def test_public_repos(self, mock_json):
        """
        this method unit-test GithubOrgClient.public_repos
        """
        payload = [{"name": "Google"}, {"name": "Twitter"}]
        mock_json.return_value = payload

        with patch(
            "client.GithubOrgClient._public_repos_url",
            new_callable=PropertyMock
        ) as mock_public:

            mock_public.return_value = "hello world"
            test_class = GithubOrgClient("test")
            result = test_class.public_repos()

            expected = [item["name"] for item in payload]
            self.assertEqual(result, expected)

            mock_public.assert_called_once()
            mock_json.assert_called_once()

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """
        Test that has_license returns True if repo has the specified license
        """
        result = GithubOrgClient.has_license(
            repo, license_key
        )
        self.assertEqual(result, expected)


@parameterized_class(
    (
        "org_payload",
        "repos_payload",
        "expected_repos",
        "apache2_repos",
    ),
    TEST_PAYLOAD
)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration test for GithubOrgClient.public_repos method"""

    @classmethod
    def setUpClass(self):
        """Set up patcher for requests.get before all tests"""
        self.get_patcher = patch("requests.get")
        mock_get = self.get_patcher.start()

        def side_effect(url):
            """Return payload depending on URL"""
            mock_response = mock.MagicMock()
            if url.endswith("/repos"):
                mock_response.json.return_value = self.repos_payload
            else:  # assume it's the org URL
                mock_response.json.return_value = self.org_payload
            return mock_response

        mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(self):
        """Stop patcher after all tests"""
        self.get_patcher.stop()

    def test_public_repos(self):
        """Test that public_repos returns expected repo list"""
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        """Test filtering repos by license"""
        client = GithubOrgClient("google")
        self.assertEqual(
            client.public_repos(license="apache-2.0"),
            self.apache2_repos
        )
