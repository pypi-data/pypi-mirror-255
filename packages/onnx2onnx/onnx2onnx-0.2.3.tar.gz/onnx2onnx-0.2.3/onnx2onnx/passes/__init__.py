"""
Copyright Wenyi Tang 2023

:Author: Wenyi Tang
:Email: wenyitang@outlook.com

"""

import inspect
from typing import Callable, Iterator, Optional

from tabulate import tabulate


class Registry:
    """A simple registry object to hold objects from others

    Samples::

        FOO = Registry("FOO")

        @FOO.register()
        def foo(): ...

        print(FOO)
        # ┌───────────────┐
        # │ Register: FOO │
        # ├───────────────┤
        # │ foo           │
        # └───────────────┘
    """

    def __init__(self, name=None) -> None:
        self._bucks = {}
        self._configs = {}
        self._name = name or "<Registry>"

    @staticmethod
    def _legal_name(name: str) -> str:
        words = [""]
        for a, b in zip(list(name), list(name.lower())):
            if a != b:
                words.append("")
            words[-1] += b
        return "_".join(words).strip("_")

    def register(self, name=None):
        """A decorator to register an object."""

        def wrapper(func):
            if not callable(func):
                raise TypeError(
                    "the object to be registered must be a function or Rewriter,"
                    f" got {type(func)}"
                )
            if inspect.isfunction(func):
                func.__name__ = name or func.__name__
                self._bucks[func.__name__] = func
                self._configs[func.__name__] = inspect.signature(func)
            else:
                obj = func()
                if not (hasattr(obj, "rewrite") and inspect.ismethod(obj.rewrite)):
                    raise TypeError(
                        f"the registered object {func} must be the subclass "
                        "of onnx2onnx.passes.rewriter.Rewriter, but its mro is "
                        f"{func.__mro__}"
                    )
                assert callable(obj), f"Wired! {func} is not callable!"

                obj.__name__ = name or self._legal_name(func.__name__)
                self._bucks[obj.__name__] = obj
                self._configs[obj.__name__] = inspect.signature(func.rewrite)
            return func

        return wrapper

    def get(self, name: str) -> Optional[Callable]:
        """Get a registered object by its name."""
        return self._bucks.get(name)

    def get_config(self, name: str):
        """Get the configuration of an object"""
        return self._configs.get(name)

    def __iter__(self) -> Iterator[Callable]:
        """Return an Iterator for all registered functions"""
        yield from self._bucks.keys()

    def __repr__(self) -> str:
        title = [f"Register: {self._name}", "Args"]
        members = [[i, self._configs[i]] for i in sorted(self._bucks.keys())]
        return tabulate(members, title, "simple_grid")


PASSES = Registry("PASS")

# pylint: disable=C0413
from .convert import *  # noqa: E402, F403
from .optimize import *  # noqa: E402, F403
from .transforms import *  # noqa: E402, F403

# pylint: enable=C0413

LEVEL1 = [
    "half_to_float",
    "initializer_to_constant",
    "shape_to_constant",
    "fold_constant",
    "prelu_to_leaky",
]

LEVEL2 = [
    "split_to_slice",
    "onnx_optimizer",
    "onnx_simplifier",
]
