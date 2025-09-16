#!/usr/bin/env python3
import unittest
from unittest.mock import patch
from utils import access_nested_map, get_json, memoize
from parameterized import parameterized


class TestAccessNestedMap(unittest.TestCase):
    '''Test access_nested_map function to check utils.py'''
    @parameterized.expand([
        ({}, ("a",), KeyError),
        ({"a": 1}, ("a", "b"), KeyError)
    ])
    def test_access_nested_map_exception(self, nested_map, path, expected):
        '''Test access_nested_map exception when path is invalid'''
        with self.assertRaises(expected):
            access_nested_map(nested_map, path)
    '''parameterized runs thesame test with different inputs'''
    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a", "b"), 2),
        ({"a": {"b": {"c": 3}}}, ("a", "b", "c"), 3)
    ])
    def test_access_nested_map(self, nested_map, path, expected):
        '''Test access_nested_map with valid path'''
        self.assertEqual(access_nested_map(nested_map, path), expected)


class TestGetJson(unittest.TestCase):
    '''Test get_json function to check utils.py'''
    @parameterized.expand([
        {"test_url": "http://example.com", "test_payload": {"payload": True}},
        {"test_url": "http://holberton.io", "test_payload": {"payload": False}}
    ])
    def test_get_json(self, test_url, test_payload):
        '''Test get_json with different URLs and payloads'''
        with patch('utils.requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = test_payload
            self.assertEqual(get_json(test_url), test_payload)


class TestMemoize(unittest.TestCase):
    '''Test memoize function to check utils.py'''
    def test_memoize(self):
        '''Test memoize decorator'''
        class TestClass:
            '''Test class to check memoize decorator'''
            def a_method(self):
                '''A method that returns 42'''
                return 42

            @memoize
            def a_property(self):
                """
                A property that uses memoize to cache the result of a method
                """
                return self.a_method()

        with patch.object(TestClass, 'a_method',
                          return_value=42) as mock_method:
            test_instance = TestClass()
            result1 = test_instance.a_property
            result2 = test_instance.a_property
            self.assertEqual(result1, 42)
            self.assertEqual(result2, 42)
            mock_method.assert_called_once()
