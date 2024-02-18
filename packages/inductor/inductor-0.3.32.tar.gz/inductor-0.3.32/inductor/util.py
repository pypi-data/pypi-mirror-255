# Copyright 2023 Inductor, Inc.
"""Inductor utility functions."""

import importlib
import inspect
import os
import sys
import types
from typing import Any, Callable, Dict, Optional, Union

from inductor import wire_model


def in_google_colab() -> bool:
    """Return True if currently running in Google Colab, and False otherwise."""
    try:
        import google.colab  # pylint: disable=import-outside-toplevel,unused-import
        return True
    except ImportError:
        return False


def get_module_qualname(f: Callable) -> str:
    """Return the fully qualified name of the module in which f is defined.

    Args:
        f: A function, class, or method.

    Returns:
        The fully qualified name of the module in which f is defined. If f is
        defined in the __main__ module, then the name of the file containing f
        (without its ".py" extension) is returned as the fully qualified module
        name. If f is defined in a Google Colab notebook, then "google_colab" is
        returned as the fully qualified module name.

    Raises:
        RuntimeError if f is defined in the __main__ module, the current
        environment is not Google Colab, and the name of the file
        containing f does not end with ".py".
    """
    qualname = f.__module__
    if qualname == "__main__":
        # Special case for Google Colab.
        if in_google_colab():
            return "google_colab"

        qualname, ext = os.path.splitext(
            os.path.basename(f.__globals__["__file__"]))
        if ext != ".py":
            raise RuntimeError(
                f"f ({f.__qualname__}) is defined in the __main__ module but "
                f"is contained in a file ({f.__globals__['__file__']}) that "
                "does not have extension '.py'.")
    return qualname


class LazyCallable:
    """Container for a function or LangChain object that is lazily imported.
    
    Represents a function or LangChain object that is provided by the user as
    part of a test suite. Objects of this class are callable, and calling them
    will import the required module if necessary to call the object.

    Attributes:
        fully_qualified_name (str): Fully qualified name of the callable
            object, in the format "<fully qualified module name>:<fully
            qualified object name>". (e.g. "my.module:my_function")
        path_to_module_dir (str): Path to the directory that contains the
            module that contains the callable object.
        input_signature (Dict[str, Optional[str]]): Inputs signature of the
            callable object. Inputs signature is a map between input parameter
            names to strings indicating the corresponding parameter types (or to
            None for input parameters that do not have type annotations).
    """
    def __init__(
        self,
        callable_or_fully_qualified_name: Union[Callable, str],
        path_to_module_dir: str = os.getcwd()):
        """Initialize a LazyCallable object.

        Args:
            callable_or_fully_qualified_name: Callable object or fully
                qualified name of the callable object, in the format
                "<fully qualified module name>:<fully qualified object name>".
                (e.g. "my.module:my_function")
            path_to_module_dir: Path to the directory that contains the module
                that contains the callable object. If not provided, the
                current working directory is used. This argument is ignored if
                `callable_or_fully_qualified_name` is a callable object.
        """
        if isinstance(callable_or_fully_qualified_name, Callable):
            callable_object = callable_or_fully_qualified_name
            module_qualname = get_module_qualname(callable_object)
            object_qualname = callable_object.__qualname__

            self.fully_qualified_name = f"{module_qualname}:{object_qualname}"
            self.path_to_module_dir = os.path.dirname(
                inspect.getfile(callable_object))
        elif isinstance(callable_or_fully_qualified_name, str):
            self.fully_qualified_name = callable_or_fully_qualified_name
            self.path_to_module_dir = path_to_module_dir

            callable_object = self.get_callable()
        else:
            raise ValueError(
                "callable_or_fully_qualified_name must be a callable or a "
                "string.")

        if callable_object.__class__.__name__ == "LLMChain":
            self._program_type = "LANGCHAIN"
        elif inspect.isfunction(callable_object):
            self._program_type = "FUNCTION"
        else:
            raise ValueError(
                f"Object {self.fully_qualified_name} is not a function or "
                "LangChain object.")

        self.inputs_signature = self._get_inputs_signature()

    def get_program_details(self) -> wire_model.ProgramDetails:
        """Return a `wire_model.ProgramDetails` object.
        
        Returns:
            `wire_model.ProgramDetails` object.
        """
        return wire_model.ProgramDetails(
            fully_qualified_name=self.fully_qualified_name,
            program_type=self._program_type,
            inputs_signature=self.inputs_signature)

    def _import_module(self, module_qualname: str) -> types.ModuleType:
        """Import the module given by module_qualname.

        Args:
            module_qualname: Fully qualified name of the module to import.

        Returns:
            The imported module.
        """
        orig_sys_path = sys.path.copy()
        sys.path[0] = self.path_to_module_dir
        module = importlib.import_module(module_qualname)
        sys.path = orig_sys_path
        return module

    def get_callable(self) -> Callable:
        """Import the callable object and return it.
        
        Returns:
            Callable object.
        """
        module_qualname, object_qualname = (
            self.fully_qualified_name.split(":"))
        module_qualname = module_qualname.replace(
            "/", ".")
        # Note: we do not use removesuffix() here in order to enable
        # compatibility with Python 3.8.
        if module_qualname.endswith(".py"):
            module_qualname = module_qualname[:-len(".py")]

        module_is_main = (module_qualname == "google_colab") or (
            # To prevent re-importing the __main__ module under the name
            # given by its filename (in order to prevent inadvertently
            # re-executing the __main__ module's contents).
            "__main__" in sys.modules and
            hasattr(sys.modules["__main__"], "__file__") and
            module_qualname == os.path.splitext(
                os.path.basename(sys.modules["__main__"].__file__))[0])  # pylint: disable=no-member
        if module_is_main:
            module_qualname = "__main__"

        module = self._import_module(module_qualname)
        callable_object = module
        for name in object_qualname.split("."):
            callable_object = getattr(callable_object, name)
        return callable_object

    def __call__(self, *args, **kwargs) -> Any:
        """Call the callable object.
        
        Args:
            *args: Positional arguments to pass to the callable object.
            **kwargs: Keyword arguments to pass to the callable object.
        
        Returns:
            The return value of the callable object.
        """
        callable_object = self.get_callable()
        if self._program_type == "LANGCHAIN":
            return callable_object.run(*args, **kwargs)
        else:
            return callable_object(*args, **kwargs)

    def _get_inputs_signature(self) -> Dict[str, Optional[str]]:
        """Return the inputs signature of the callable object.
        
        Inputs signature is a map between input parameter names to
        strings indicating the corresponding parameter types (or to None for
        input parameters that do not have type annotations).
        """
        callable_object = self.get_callable()
        if self._program_type == "LANGCHAIN":
            return {key: None for key in callable_object.input_keys}
        else:
            signature = inspect.signature(callable_object)
            return {
                name: (
                    str(param.annotation)
                    if param.annotation != inspect._empty  # pylint: disable=protected-access
                    else None)
                for name, param in signature.parameters.items()
            }
