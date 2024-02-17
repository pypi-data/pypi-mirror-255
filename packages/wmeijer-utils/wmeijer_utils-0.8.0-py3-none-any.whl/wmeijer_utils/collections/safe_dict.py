from typing import TypeVar, Generic, List, Any, Dict, Callable


_KT = TypeVar("_KT")
_VT = TypeVar("_VT")


class SafeDict(dict, Generic[_KT, _VT]):
    """
    Standard dictionary data structure that adds
    a default value to a key if it doesn't exist yet.
    This is greatly helpful when preventing boilerplate
    code that adds defaults.
    """

    def __init__(
        self,
        default_value,
        default_value_constructor_args: "List[Any] | None" = None,
        default_value_constructor_kwargs: "Dict[str, Any] | None" = None,
        initial_mapping: "Dict[_KT, _VT] | None" = None,
        delete_when_default: bool = False,
        *args,
        **kwargs,
    ):
        """
        :param default_value: the default value for entries.
        If this is a ``type``, it will call said type's constructor, and if it's callable, it will call it.
        :param default_value_constructor_args: The constructor arguments for the default value.
        Only relevant if its constructor is called or the default value is callable.
        :param default_value_constructor_kwargs: Named constructor arguments for the default value.
        Only relevant if its constructor is called.
        :param map: Can be set to come with a pre-filled mapping.
        :param *args, **kwargs: Constructor arguments for the inner datastructure of the dictionary.
        These can be anything that can be passed to the constructor of a ``dict``.
        :param delete_when_default: Deletes entries whenever they are equal to the default value to preserve memory.
        Only use this when you don't intend to use the len() as this might be misleading. This is only set when the
        default value is not a ``callable`` or a ``type``.
        """

        if not initial_mapping is None:
            super().__init__(initial_mapping)

        self.__default_value: Any = default_value
        self.__delete_when_default: bool = delete_when_default

        # Sets default constructor arguments.
        self.__default_value_constructor_args: List[Any] = (
            default_value_constructor_args or []
        )
        self.__default_value_constructor_kwargs: Dict[str, Any] = (
            default_value_constructor_kwargs or {}
        )

        # Builds default value method.
        self.__default_value_method: Callable = self.__build_default_value_method(
            self.__default_value
        )

        super().__init__(*args, **kwargs)

        # Tests the default value method to ensure this is yielded.
        try:
            self.__get_default_value()
        except Exception as ex:
            raise ValueError("Default is invalid.", ex)

    def __build_default_value_method(
        self, default_value: "type | Callable | Any"
    ) -> Callable:
        """Simple factory method for supported default value types."""
        if isinstance(default_value, type):
            self.__delete_when_default = False
            return _get_default_from_type
        elif isinstance(default_value, Callable):
            return _get_default_from_callable
        else:
            return _get_default_from_primitive

    def __get_default_value(self) -> Any:
        """Returns the default value."""
        return self.__default_value_method(
            self.__default_value,
            *self.__default_value_constructor_args,
            **self.__default_value_constructor_kwargs,
        )

    def __getitem__(self, __key: _KT) -> None:
        if not __key in self:
            value = self.__get_default_value()
            super().__setitem__(__key, value)
        return super().__getitem__(__key)

    def __setitem__(self, __key: _KT, __value: _VT) -> None:
        if self.__delete_when_default and __value == self.__default_value:
            if __key in self:
                super().__delitem__(__key)
        else:
            super().__setitem__(__key, __value)


def _get_default_from_primitive(default: Any, *args, **kwargs) -> Any:
    """Returns the value."""
    return default


def _get_default_from_callable(default: Callable, *args, **kwargs) -> Any:
    """Calls the value."""
    return default(*args, **kwargs)


def _get_default_from_type(default: type, *args, **kwargs) -> Any:
    """Creates new instance of the value."""
    return default(*args, **kwargs)
