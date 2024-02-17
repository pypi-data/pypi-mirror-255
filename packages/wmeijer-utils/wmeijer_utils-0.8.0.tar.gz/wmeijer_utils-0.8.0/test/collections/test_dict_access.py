import unittest

from wmeijer_utils.collections import dict_access as d


class TestDictAccess(unittest.TestCase):

    def test_has_all_keys(self):
        my_dict = {"key_a": 123, "key_b": "asdf", "key_c": {789321}}

        self.assertTrue(d.has_all_keys(my_dict, ["key_a", "key_b", "key_c"]))
        self.assertTrue(d.has_all_keys(my_dict, ["key_a", "key_c"]))
        self.assertTrue(d.has_all_keys(my_dict, []))
        self.assertFalse(d.has_all_keys(my_dict, ["key_a", "key_b", "key_c", "key_d"]))
        self.assertFalse(d.has_all_keys(my_dict, ["key_d"]))

    def test_safe_add_list_element(self):
        my_dict = {}

        # Check 1: New element
        d.safe_add_list_element(my_dict, "key_a", "element_1")

        self.assertIn("key_a", my_dict)
        self.assertIsInstance(my_dict["key_a"], list)
        self.assertIs(len(my_dict["key_a"]), 1)

        # Check 2: pre-existing list
        my_dict = {"key_a": [0, 1, 2]}
        d.safe_add_list_element(my_dict, "key_a", 4)

        self.assertTrue(
            all(ele in my_dict["key_a"] for ele in range(3)),
            "Original element is missing.",
        )
        self.assertIn(4, my_dict["key_a"], "New element is missing")

    def test_safe_add_set_element(self):
        my_dict = {}

        # Check 1: New element
        d.safe_add_set_element(my_dict, "key_a", "element_1")

        self.assertIn("key_a", my_dict)
        self.assertIsInstance(my_dict["key_a"], set)
        self.assertIs(len(my_dict["key_a"]), 1)

        # Check 2: pre-existing set
        my_set = set()
        my_set.update(range(3))
        my_dict = {"key_a": my_set}
        d.safe_add_set_element(my_dict, "key_a", 4)

        self.assertTrue(
            all(ele in my_dict["key_a"] for ele in range(3)),
            "Original element is missing.",
        )
        self.assertIn(4, my_dict["key_a"], "New element is missing")

    def test_get_nested(self):
        my_dict = {"key_a": "value_a"}

        # Simple test
        self.assertEqual(d.get_nested(my_dict, ["key_a"]), "value_a")

        # Nested test.
        my_dict = {"key_a": {"key_b": {"key_c": 5}}}
        self.assertEqual(d.get_nested(my_dict, ["key_a", "key_b", "key_c"]), 5)

        # Simple missing key
        my_dict = {"key_a": 5}
        self.assertIsNone(d.get_nested(my_dict, ["key_b"]))

        # Nested missing key
        my_dict = {"key_a": {"key_b": {"key_c": 5}}}
        self.assertIsNone(d.get_nested(my_dict, ["key_a", "key_b", "key_d"]))

        # Test with list
        my_dict = {"key_a": {"key_b": [0, 1, 2, 3]}}
        res = d.get_nested(my_dict, ["key_a", "key_b"])
        self.assertIsNotNone(res)
        self.assertEqual(len(res), 4)
        self.assertTrue(all([ele in res for ele in range(4)]))

    def test_get_nested_many_simple_retrieval(self):
        # Simple test
        my_dict = {"key_a": "value"}
        res = d.better_get_nested_many(my_dict, ["key_a"])
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0], "value")

        # Nested array at root test
        my_dict = [{"key_a": "value_0"}, {"key_a": "value_1"}, {"key_a": "value_2"}]
        res = d.better_get_nested_many(my_dict, ["key_a"])
        self.assertEqual(len(res), 3)
        self.assertTrue(all(f"value_{ele}" in res for ele in range(3)))

        # Nested array at sublevel
        my_dict = {
            "key_a": [{"key_b": "value_0"}, {"key_b": "value_1"}, {"key_b": "value_2"}]
        }
        res = d.better_get_nested_many(my_dict, ["key_a", "key_b"])
        self.assertEqual(len(res), 3)
        self.assertTrue(all(f"value_{ele}" in res for ele in range(3)))

    def test_get_nested_many_missing_key(self):
        # Simple missing key test no raise.
        my_dict = {"key_a": "value"}
        res = d.better_get_nested_many(my_dict, ["key_b"], False)
        self.assertEqual(len(res), 0)

        # Simple missing key raise
        my_dict = {"key_a": "value"}
        self.assertRaises(KeyError, d.better_get_nested_many, my_dict, ["key_b"], True)

        # Nested missing key
        my_dict = [{"key_a": "value_0"}, {"key_a": "value_1"}, {"key_b": "value_2"}]
        self.assertRaises(KeyError, d.better_get_nested_many, my_dict, ["key_a"], True)

        # Nested missing key at sublevel
        my_dict = {
            "key_a": [{"key_b": "value_0"}, {"key_b": "value_1"}, {"key_b": "value_2"}]
        }
        self.assertRaises(
            KeyError, d.better_get_nested_many, my_dict, ["key_a", "key_c"], True
        )

    def test_get_nested_many_complex_retrieval(self):
        # # Test tree.
        # my_dict = {
        #     "key_a": [
        #         {"key_b": [{"key_c": 1}, {"key_c": 2}, {"key_c": 3}]},
        #         {"key_b": [{"key_c": 4}, {"key_c": 5}, {"key_c": 6}]},
        #         {"key_b": [{"key_c": 7}, {"key_c": 8}, {"key_c": 0}]},
        #     ]
        # }

        # res = d.better_get_nested_many(my_dict, ["key_a", "key_b", "key_c"])
        # self.assertEqual(len(res), 9)
        # print(res)
        # self.assertTrue(all([ele in res for ele in range(10)]))
        pass
