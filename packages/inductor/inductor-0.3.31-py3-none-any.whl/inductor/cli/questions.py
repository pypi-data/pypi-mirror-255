# Copyright 2023 Inductor, Inc.
"""Collection of Questions / User Prompts for the Inductor CLI.

This module is intended to include questions that require non-trivial
validation or other complex logic. It does not need to include simple
questions.
"""

import pathlib
import re
from typing import Any, Dict, Optional
import inquirer
import rich

from inductor import util


def get_new_test_suite_file_path() -> pathlib.Path:
    """Prompt user for a path to a new test suite file.

    Prompt the user to enter a path for a new test suite file. Validate the
    path (see `validate_path` function below). If the path is valid, return
    it. If the path is invalid, continue prompting the user until a valid
    path is entered.

    Returns:
        Path to the test suite file.
    """
    default_path = pathlib.Path("test_suite.yaml")
    i = 1
    while default_path.exists():
        default_path = pathlib.Path(f"test_suite_{i}.yaml")
        i += 1
        if i > 100:
            # If we've tried 100 times, something is wrong.
            # Use the initial default path.
            default_path = pathlib.Path("test_suite.yaml")
            break

    # TODO (https://github.com/inductor-hq/saas/issues/18): Add autocomplete
    # for paths.
    def validate_path(_: Dict[str, Any], current: str) -> bool:
        """Validate a given path.

        A path is valid if it:
        1. Has a .yaml or .yml extension.
        2. Does not already exist.
        3. Can be touched.

        Given a path to a file, validate it. If the path is valid and gets
        created, delete it.

        Args:
            _: Dictionary containing the answers from previous questions
                (not including the current question). This will be an empty
                dictionary because the `test_suite_file_path` question is not
                part of a collection of questions.
            current: The current answer, which is a path to validate.
        
        Returns:
            True if the path is valid, False otherwise.
        
        Raises:
            inquirer.errors.ValidationError: If the path is invalid.
        """
        try:
            path = pathlib.Path(current).resolve()
            if path.suffix not in [".yml", ".yaml"]:
                # NOTE: This will also catch empty paths.
                raise inquirer.errors.ValidationError(
                    "",
                    reason="File requires a .yaml or .yml extension.")

            # Permissions: rw-rw-rw- (0o666)
            path.touch(mode=0o666, exist_ok=False)
            if path.exists():
                path.unlink()
        except FileExistsError:
            raise inquirer.errors.ValidationError(  # pylint: disable=raise-missing-from
                "", reason="File already exists.")
        except PermissionError:
            raise inquirer.errors.ValidationError(  # pylint: disable=raise-missing-from
                "", reason="Missing permissions to create this file.")
        except FileNotFoundError:
            # The path specified by current does not exist.
            raise inquirer.errors.ValidationError(  # pylint: disable=raise-missing-from
                "", reason="Invalid path.")
        return True

    rich.print("\n[[yellow]1/4[/yellow]] Enter the file path for the new test "
               "suite, ensuring it has a .yaml or .yml extension and does "
               "not already exist.")
    test_suite_file_path = inquirer.text(
        message="Test suite file path",
        validate=validate_path,
        default=default_path)
    return pathlib.Path(test_suite_file_path).resolve()


def get_test_suite_name() -> str:
    """Prompt user for a test suite name.

    Prompt the user to enter a test suite name. Validate the name (see
    `validate_test_suite_name` function below). If the name is valid,
    return it. If the name is invalid, continue prompting the user until a
    valid name is entered.

    Returns:
        Test suite name.
    """
    def validate_test_suite_name(_: Dict[str, Any], current: str) -> bool:
        """Validate test suite name.

        A test suite name is valid if it:
        1. Is non-empty.
        2. Includes only alphanumeric characters, underscores, or dashes.

        Args:
            _: Dictionary containing the answers from previous questions
                (not including the current question). This will be an empty
                dictionary because the `test_suite_name` question is not
                part of a collection of questions.
            current: The current answer, which is a test suite name to
                validate.

        Returns:
            True if the test suite name is valid, False otherwise.
        
        Raises:
            inquirer.errors.ValidationError: If the test suite name is
                invalid.
        """
        name = current

        if not re.match(r"^[a-zA-Z0-9_-]+$", name):
            raise inquirer.errors.ValidationError(
                "", reason="Invalid test suite name.")
        return True

    rich.print("\n[[yellow]2/4[/yellow]] Enter a name for the new test suite, "
               "ensuring that it is non-empty and includes only alphanumeric "
               "characters, underscores, or dashes. Your test suites must "
               "have unique names.")
    return inquirer.text(
        message="Test suite name",
        validate=validate_test_suite_name)


def get_test_suite_description() -> Optional[str]:
    """Prompt user for a test suite description.
    
    Returns:
        Test suite description, or None if the user skipped this question.
    """
    rich.print("\n[[yellow]3/4[/yellow]] Optionally enter a description for "
               "the new test suite. Press enter to skip.")
    description = inquirer.text(message="Test suite description")
    if not description:
        return None
    return description


def get_llm_program_fully_qualified_name() -> str:
    """Prompt user for a LLM program fully qualified name.

    Prompt the user to enter a LLM program fully qualified name. Validate the
    name (see `validate_llm_program` function below). If the name is valid,
    return it. If the name is invalid, continue prompting the user until a
    valid name is entered.

    Returns:
        LLM program fully qualified name.
    """
    def validate_llm_program(_: Dict[str, Any], current: str) -> bool:
        """Validate LLM program fully qualified name.

        A LLM program fully qualified name is valid if it:
        1. Is in the format <fully qualified module name>:<fully qualified
            object name>.
        2. Can instantiate a `util.LazyCallable` object.
        3. The instantiated object can import the underlying LLM program
            and get its parameter keys with `get_parameter_keys`.

        Args:
            _: Dictionary containing the answers from previous questions
                (not including the current question). This will be an empty
                dictionary because the `llm_program_fully_qualified_name`
                question is not part of a collection of questions.
            current: The current answer, which is a LLM program fully
                qualified name to validate.

        Returns:
            True if the LLM program fully qualified name is valid, False
            otherwise.

        Raises:
            inquirer.errors.ValidationError: If the LLM program fully
                qualified name is invalid.
        """
        try:
            if not re.match(r".+:.+", current):
                raise inquirer.errors.ValidationError(
                    "",
                    reason="Invalid format.")

            # A valid LLM program fully qualified name should be able to
            # instantiate a `util.LazyCallable` object, which will
            # attempt to access the underlying callable object of the LLM
            # program. If it is unable to do so, it will raise an exception.
            util.LazyCallable(current)
        except inquirer.errors.ValidationError as error:
            raise error
        except Exception as error:
            # It is not trival identify the relevant Exception subtypes that
            # should be considered actual validation errors, so we catch all
            # exceptions and raise a generic validation error with the
            # exception message appended. The issue with this method is that
            # the validation error message is limited to a single line. If
            # the exception message is too long, it will be truncated. In
            # testing, exception messages seem to be able to fit on a single
            # line, but this should be revisited if we are encountering
            # exceptions with long messages.
            raise inquirer.errors.ValidationError(  # pylint: disable=raise-missing-from
                "", reason=f"Invalid object: {str(error)}")
        return True

    rich.print("\n[[yellow]4/4[/yellow]] Enter the fully qualified name (FQN) "
               "of the LLM program to test. The LLM program can be a Python "
               "function or a LangChain chain. The FQN should be in the "
               "format `path.to.python.module:function_or_object_name`.")
    return inquirer.text(
        message=("LLM program FQN"),
        validate=validate_llm_program)


def choose_new_test_suite() -> bool:
    """Prompt user to create a new test suite or use an existing one.

    Returns:
        True if the user wants to create a new test suite, False if the user
        wants to use an existing test suite.
    """
    create_new, use_existing = ("Create new", "Use existing")
    answer = inquirer.list_input(
        "Create new or use existing test suite?",
        choices=[create_new, use_existing])
    if answer == create_new:
        return True
    return False
