import unittest

from packages.manifest_utils import sort_topologically

class TestTopologicalSort(unittest.TestCase):
    def test_simple_graph(self):
        graph = {'a': ['b', 'c'], 'b': ['c'], 'c': []}
        expected_order = ['c', 'b', 'a']
        self.assertEqual(sort_topologically(graph), expected_order)

    def test_graph_with_cycle(self):
        graph = {'a': ['b'], 'b': ['c'], 'c': ['a']}
        with self.assertRaises(ValueError):
            sort_topologically(graph)

    def test_disconnected_graph(self):
        graph = {'a': ['b'], 'b': ['c'], 'c': [], 'd': []}
        expected_order = ['c', 'b', 'a', 'd']
        self.assertEqual(sort_topologically(graph), expected_order)