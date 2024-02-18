import unittest

from packages.manifest_utils import get_tests_and_nodes

class TestGetTestsAndNodes(unittest.TestCase):
    # Returns a tuple with two dictionaries.
    def test_returns_tuple_with_two_dictionaries(self):
        # Arrange
        manifest = {
            'nodes': {
                'node1': {
                    'resource_type': 'test',
                    'name': 'test1',
                    'depends_on': {
                        'nodes': ['node2']
                    }
                },
                'node2': {
                    'resource_type': 'model',
                    'name': 'model1'
                }
            }
        }
    
        # Act
        result = get_tests_and_nodes(manifest)
    
        # Assert
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], dict)
        self.assertIsInstance(result[1], dict)

    # The first dictionary contains the tests and their data.
    def test_first_dictionary_contains_tests_and_data(self):
        # Arrange
        manifest = {
            'nodes': {
                'node1': {
                    'resource_type': 'test',
                    'name': 'test1',
                    'depends_on': {
                        'nodes': ['node2']
                    }
                },
                'node2': {
                    'resource_type': 'model',
                    'name': 'model1'
                }
            }
        }
    
        # Act
        result = get_tests_and_nodes(manifest)
    
        # Assert
        self.assertIn('test1', result[0])
        self.assertEqual(result[0]['test1'], manifest['nodes']['node1'])

    # The second dictionary contains the nodes and the tests that depend on them.
    def test_second_dictionary_contains_nodes_and_tests(self):
        # Arrange
        manifest = {
            'nodes': {
                'node1': {
                    'resource_type': 'test',
                    'name': 'test1',
                    'depends_on': {
                        'nodes': ['node2']
                    }
                },
                'node2': {
                    'resource_type': 'model',
                    'name': 'model1'
                }
            }
        }
    
        # Act
        result = get_tests_and_nodes(manifest)
    
        # Assert
        self.assertIn('node2', result[1])
        self.assertEqual(result[1]['node2'], ['test1'])