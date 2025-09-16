#!/usr/bin/env python3
import unittest
from unittest.mock import MagicMock, patch, PropertyMock
from client import GithubOrgClient
from parameterized import parameterized, parameterized_class
from fixtures import org_payload, repos_payload, expected_repos, apache2_repos


class TestGithubOrgClient(unittest.TestCase):
    '''
    Test GithubOrgClient class to check client.py
    using parameterized tests and patch to initialize mock get_json
    '''
    @parameterized.expand([
        ("google"),
        ("abc")
    ])
    @patch('client.get_json')
    def test_org(self, org_name, mock_get_json):
        '''Test org method'''
        test_payload = {"payload": True}
        mock_get_json.return_value = test_payload  # Mocking get_json
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

        with patch.object(GithubOrgClient, "org",
                          new_callable=unittest.mock.PropertyMock) as mock_org:
            mock_org.return_value = test_payload
            client = GithubOrgClient("test-org")

            result = client._public_repos_url
            self.assertEqual(result, test_payload["repos_url"])

            mock_org.assert_called_once()

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """Test that public_repos returns expected repo names"""

        # Step 1: Mock payload returned by get_json
        mock_get_json.return_value = [
            {"name": "repo1"},
            {"name": "repo2"},
            {"name": "repo3"},
        ]

        # Step 2: Mock _public_repos_url property
        with patch.object(
            GithubOrgClient,
            "_public_repos_url",
            new_callable=PropertyMock
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

    """Check has_license is a static method"""
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
    """Integration test for GithubOrgClient.public repos"""

    @classmethod
    def setUpClass(cls):
        """Set up patcher for requests.get before all tests"""
        cls.get_patcher = patch("requests.get")

        # Start the patcher
        mock_get = cls.get_patcher.start()

        # Configure side_effect for requests.get().json()
        def side_effect(url):
            """
            Defines a side_effect so when requests.get(url) is called,
            it returns a fake response whose .json() method gives the
            right payload depending on the URL.
            """
            mock_response = MagicMock()
            if url == "https://api.github.com/orgs/google":
                mock_response.json.return_value = cls.org_payload
            elif url == "https://api.github.com/orgs/google/repos":
                mock_response.json.return_value = cls.repos_payload
            else:
                mock_response.json.return_value = {}
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

    # def test_public_repos(self):
    #     """Test that public_repos returns expected repos from fixtures"""
    #     client = GithubOrgClient("google")
    #     self.assertEqual(client.public_repos(), self.expected_repos)

    # def test_public_repos_with_license(self):
    #     """Test that public_repos filters repos by license correctly"""
    #     client = GithubOrgClient("google")
    #     self.assertEqual(
    #         client.public_repos(license="apache-2.0"),
    #         self.apache2_repos
    #     )
