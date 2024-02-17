import unittest

from wmeijer_utils.collections.safe_dict import SafeDict


class TestSafeDict(unittest.TestCase):
    def test_default_is_primitive(self):
        my_value = 132
        sd = SafeDict(my_value)

        self.assertEqual(sd["key_1"], my_value)

        my_value = 654
        self.assertNotEqual(sd["key_2"], my_value)

    def test_default_is_string(self):
        my_value = "test_string_1"
        sd = SafeDict(my_value)

        self.assertEqual(sd["key_1"], my_value)

        my_value = my_value.replace("test", "other_test")
        self.assertNotEqual(sd["key_2"], my_value)

        my_value = "test_string_2"
        self.assertNotEqual(sd["key_3"], my_value)

    def test_initial_mapping(self):
        my_value = 1500
        my_mapping = {"key_1": 789, "key_2": "something", "key_3": my_value}

        sd = SafeDict(my_value, initial_mapping=my_mapping)

        # Checks mapping correctness.
        for key, value in my_mapping.items():
            self.assertIn(key, sd, "Initial mapping has missing key.")
            self.assertEqual(sd[key], my_mapping[key], "Initial mapping is incorrect.")

        # Check data dependency 1
        my_mapping["key_1"] = "1500"
        self.assertNotEqual(
            sd["key_1"],
            my_mapping["key_1"],
            "Implementation has dependency on external mapping.",
        )

        # Check data dependency 2
        del my_mapping
        self.assertEqual(
            sd["key_1"], 789, "Implementation has dependency on external mapping."
        )

        # Check data dependency 3
        my_value = 1800
        self.assertNotEqual(
            sd["key_3"], my_value, "Implementation has dependency on external mapping."
        )

    def test_default_is_primitive_with_delete(self):
        my_value = 1500
        sd = SafeDict(my_value, delete_when_default=True)

        # Check manually setting default value
        sd["key_1"] = 1500
        self.assertNotIn("key_1", sd, "Setting new item as default should not be kept.")

        # Check manually setting default value through update.
        sd["key_2"] = 8000
        self.assertIn("key_2", sd)
        sd["key_2"] = 1500
        self.assertNotIn("key_2", sd, "Setting new item as default should not be kept.")

    def test_default_is_none(self):
        pass

    def test_default_is_simple_callable(self):
        my_value = "some_value"

        def __my_simple_callable() -> str:
            return my_value

        my_callable = __my_simple_callable
        sd = SafeDict(my_callable)

        # Check instance
        self.assertEqual(sd["key_1"], my_value, "Incorrect  default.")

        # Param test 1: args
        self.assertRaises(
            ValueError,
            SafeDict,
            my_callable,
            default_value_constructor_args=[my_value],
        )

        # Param test 2: kwargs
        self.assertRaises(
            ValueError,
            SafeDict,
            my_callable,
            default_value_constructor_args={"param_a": my_value},
        )

    def test_default_is_parameterized_callable(self):
        my_value = "some_value_34"

        def __my_param_callable(param_a: str) -> str:
            return param_a

        # Check invalid params
        my_callable = __my_param_callable
        self.assertRaises(ValueError, SafeDict, my_callable)

        # Check valid params args.
        args = [my_value]
        sd = SafeDict(my_callable, default_value_constructor_args=args)
        self.assertEqual(sd["key_1"], my_value)

        # Check too many args params
        args = [my_value, my_value]
        self.assertRaises(
            ValueError, SafeDict, my_callable, default_value_constructor_args=args
        )

        # Check too few params
        args = []
        self.assertRaises(
            ValueError, SafeDict, my_callable, default_value_constructor_args=args
        )

        # Check kwargs params
        kwargs = {"param_a": my_value}
        sd = SafeDict(my_callable, default_value_constructor_kwargs=kwargs)
        self.assertEqual(sd["key_1"], my_value)

        # Check kwargs too many params
        kwargs = {"param_a": my_value, "param_b": my_value}
        self.assertRaises(
            ValueError, SafeDict, my_callable, default_value_constructor_kwargs=kwargs
        )

        # Check kwargs too few params
        kwargs = {}
        self.assertRaises(
            ValueError, SafeDict, my_callable, default_value_constructor_kwargs=kwargs
        )

    def test_default_is_simple_constructor(self):
        my_value = "some_value"

        class MySimpleInnerClass:
            pass

        my_callable = MySimpleInnerClass
        sd = SafeDict(my_callable)

        # Object test
        self.assertIsInstance(sd["key_1"], MySimpleInnerClass, "Incorrect default.")

        # Param test 1: args
        self.assertRaises(
            ValueError,
            SafeDict,
            MySimpleInnerClass,
            default_value_constructor_args=[my_value],
        )

        # Param test 2: kwargs
        self.assertRaises(
            ValueError,
            SafeDict,
            MySimpleInnerClass,
            default_value_constructor_args={"param_a": my_value},
        )

    def test_default_is_parameterized_constructor(self):
        my_value = "some_value_34"

        class MyParameterizedInnerClass:
            def __init__(self, param_a) -> None:
                self.__param_a = param_a

            def get_param_a(self):
                return self.__param_a

        # Check invalid params
        my_callable = MyParameterizedInnerClass
        self.assertRaises(ValueError, SafeDict, my_callable)

        # Check valid params args.
        args = [my_value]
        sd = SafeDict(my_callable, default_value_constructor_args=args)
        self.assertEqual(sd["key_1"].get_param_a(), my_value)

        # Check too many args params
        args = [my_value, my_value]
        self.assertRaises(
            ValueError, SafeDict, my_callable, default_value_constructor_args=args
        )

        # Check too few params
        args = []
        self.assertRaises(
            ValueError, SafeDict, my_callable, default_value_constructor_args=args
        )

        # Check kwargs params
        kwargs = {"param_a": my_value}
        sd = SafeDict(my_callable, default_value_constructor_kwargs=kwargs)
        self.assertEqual(sd["key_1"].get_param_a(), my_value)

        # Check kwargs too many params
        kwargs = {"param_a": my_value, "param_b": my_value}
        self.assertRaises(
            ValueError, SafeDict, my_callable, default_value_constructor_kwargs=kwargs
        )

        # Check kwargs too few params
        kwargs = {}
        self.assertRaises(
            ValueError, SafeDict, my_callable, default_value_constructor_kwargs=kwargs
        )

        # Check data dependency
        my_value = 654
        self.assertNotEqual(sd["key_1"].get_param_a(), my_value)
