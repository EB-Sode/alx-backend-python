#!/usr/bin/env python3
"""Unit and integration tests for the GithubOrgClient."""
import unittest
from unittest import mock
from parameterized import parameterized
from client import GithubOrgClient
from parameterized import parameterized_class
from fixtures import org_payload, repos_payload, apache2_repos, expected_repos


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

            mock_org.assert_called_once()

    @mock.patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """Test that public_repos returns expected repo names"""

        # Step 1: Mock payload returned by get_json
        mock_get_json.return_value = [
            {"name": "repo1"},
            {"name": "repo2"},
            {"name": "repo3"},
        ]

        # Step 2: Mock _public_repos_url property
        with mock.patch.object(
            GithubOrgClient,
            "_public_repos_url",
            new_callable=mock.PropertyMock
        ) as mock_repos_url:
            mock_repos_url.return_value = (
                "https://api.github.com/orgs/test-org/repos"
            )

            client = GithubOrgClient("test-org")
            result = client.public_repos()

            # Step 3: Assertions
            self.assertEqual(result, ["repo1", "repo2", "repo3"])

            # Step 4: Ensure mocks were called correctly
            mock_repos_url.assert_called_once()
            mock_get_json.assert_called_once_with(
                "https://api.github.com/orgs/test-org/repos"
                )

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


@parameterized_class([
    {
        "org_payload": org_payload,
        "repos_payload": repos_payload,
        "expected_repos": expected_repos,
        "apache2_repos": apache2_repos,
    }
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration test for GithubOrgClient.public repos method"""

    @classmethod
    def setUpClass(cls):
        """Set up patcher for requests.get before all tests"""
        cls.get_patcher = mock.patch("requests.get")

        # Start the patcher
        mock_get = cls.get_patcher.start()

        # Configure side_effect for requests.get().json()
        def side_effect(url):
            """
            Defines a side_effect so when requests.get(url) is called,
            it returns a fake response whose .json() method gives the
            right payload depending on the URL.
            """
            mock_response = mock.MagicMock()
            if url.endswith("/repos"):
                mock_response.json.return_value = cls.repos_payload
            else:  # assume it's the org url
                mock_response.json.return_value = cls.org_payload
            return mock_response

        mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls):
        """Stop patcher after all tests"""
        cls.get_patcher.stop()

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


if __name__ == "__main__":
    unittest.main()
