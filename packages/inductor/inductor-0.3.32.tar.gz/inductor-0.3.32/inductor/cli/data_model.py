# Copyright 2023 Inductor, Inc.
"""Abstractions for the Inductor CLI."""

import copy
import inspect
import os
from typing import Any, Callable, Dict, List, Literal, Optional, TypeVar, Union

import pydantic
import yaml

from inductor import auth_session, util, wire_model
from inductor.cli import execute


class TestSuiteValueError(ValueError):
    """Error raised when a test suite is invalid.

    Attributes:
        message: Error message.
        path: Optional path to the test suite file that caused the error.
    """
    def __init__(self, message: str, path: Optional[str] = None):
        """Error raised when a test suite is invalid.

        Args:
            message: Error message.
            path: Optional path to the test suite file that caused the error.
        """
        self.message = message
        self.path = path
        # TODO: Add the line and line number from the test suite file that
        # caused the error, if applicable.
        super().__init__(self.message)


def _extract_fully_qualified_name(value: Any) -> Any:
    """Return the fully qualified name from a Callable, if applicable.
    
    Args:
        value: Object from which to extract the fully qualified name.
    
    Returns:
        The fully qualified name of the given object, if it is a Callable.
        Otherwise, the given object.
    """
    if callable(value):
        return f"{util.get_module_qualname(value)}:{value.__qualname__}"
    return value


# Type variable for the TestCase class.
_T_TestCase = TypeVar("_T_TestCase", bound="TestCase")  # pylint: disable=invalid-name


class TestCase(pydantic.BaseModel):
    """A test case.

    Attributes:
        inputs: Mapping from input parameter name to input value.
        output: Optionally, an example of a desired high-quality output, or
            the output that is to be considered correct, for this test case.
        description: Optionally, a description of this test case.
    """
    model_config = pydantic.ConfigDict(extra="forbid")

    inputs: Dict[str, Any]
    output: Optional[Any] = None
    description: Optional[str] = None

    # Define a custom constructor to enable taking `inputs` as a positional,
    # rather than keyword-only, argument.
    def __init__(
        self,
        inputs: Dict[str, Any],
        *,
        output: Optional[Any] = None,
        description: Optional[str] = None):
        """Constructs a new test case.

        Args:
            inputs: Mapping from input parameter name to input value.
            output: Optionally, an example of a desired high-quality output, or
                the output that is to be considered correct, for this test case.
            description: Optionally, a description of this test case.
        """
        super().__init__(
            inputs=inputs, output=output, description=description)

    @classmethod
    def _from_test_suite_file_syntax(
        cls: _T_TestCase,
        params: Dict[str, Union[str, Dict[str, str]]]) -> _T_TestCase:
        """Constructs a new test case using the test suite file syntax.

        Test cases defined in a test suite file can either use the `inputs`
        keyword to specify the inputs, or all the keyword arguments will be
        treated as inputs.

        Args:
            cls: Test case class.
            params: Parameters to construct the test case.

        Returns:
            A new test case.
        
        Raises:
            TestSuiteValueError: If the test case cannot be constructed from
                the given keyword arguments.
        """
        try:
            if "inputs" not in params:
                return cls(inputs=params)
            return cls(**params)
        except TypeError as error:
            raise TestSuiteValueError(
                f"Incorrect syntax for test case: {error}."
                f"\n[yellow]Test case parameters defined in test suite file:"
                f"[/yellow] {params}") from error

    def _validate_inputs_with_signature(
        self, inputs_signature: inspect.Signature):
        """Validate that the inputs are compatible with the given signature.

        Args:
            inputs_signature: Inputs signature to validate against.

        Raises:
            TestSuiteValueError: If the inputs are not compatible with the
                signature.
        """
        try:
            inputs_signature.bind(**self.inputs)
        except TypeError as error:
            raise TestSuiteValueError(
                f"Test case inputs cannot be bound to the LLM program "
                f"signature: {error}."
                f"\n[yellow]Test case inputs:[/yellow] "
                f"{self.inputs}"
                f"\n[yellow]LLM program signature:[/yellow] "
                f"{inputs_signature}") from error


# Type variable for the QualityMeasure class.
_T_QualityMeasure = TypeVar("_T_QualityMeasure", bound="QualityMeasure")  # pylint: disable=invalid-name


class QualityMeasure(pydantic.BaseModel):
    """A quality measure.
    
    Attributes:
        name: Human-readable name of this quality measure.
        evaluator: Evaluator for this quality measure.  Determines whether
            this quality measure will be evaluated by running a function,
            via human inspection, or via an LLM.
        evaluation_type: The type of value produced by evaluation of this
            quality measure.
        spec: Specification of the details of how to execute this quality
            measure.
            - If evaluator is "FUNCTION", then spec should give the fully
            qualified name of the function (in the format
            "my.module:my_function").
            - If evaluator is "HUMAN", then spec should give the instructions
            or question that should be displayed to human evaluators.
            - If evaluator is "LLM", then spec should either give a dictionary
            with "model" and "prompt" fields, or the fully qualified name of an
            LLM program that implements the quality measure (in the format
            "my.module:my_function").
    """
    model_config = pydantic.ConfigDict(extra="forbid")

    name: str
    evaluator: Literal["FUNCTION", "HUMAN", "LLM"]
    evaluation_type: Literal["BINARY", "RATING_INT"]
    spec: Union[str, Dict[str, str]]

    @pydantic.field_validator("spec", mode="before")
    @classmethod
    def _extract_fully_qualified_spec_name(
        cls: _T_QualityMeasure, v: Any) -> Any:
        """Return the fully qualified name from the spec, if applicable."""
        return _extract_fully_qualified_name(v)


class HparamSpec(pydantic.BaseModel):
    """Specification of set of hyperparameter values to use for test suite run.

    Attributes:
        name: Name of hyperparameter.
        type: Type of hyperparameter.
        values: List of hyperparameter values.
    """
    model_config = pydantic.ConfigDict(extra="forbid", populate_by_name=True)

    name: str = pydantic.Field(alias="hparam_name")
    type: Literal["SHORT_STRING", "TEXT", "NUMBER"] = pydantic.Field(
        alias="hparam_type")
    values: List[Any]


# Type variable for the Config class.
_T_Config = TypeVar("_T_Config", bound="Config")  # pylint: disable=invalid-name


class Config(pydantic.BaseModel):
    """Config for a test suite.

    Attributes:
        id: ID of test suite.
        name: Name of test suite.
        llm_program: Fully qualified name of LLM program.
        replicas: Number of times that LLM program will be run on each pair of
            (test case, set of hyperparameters).
        parallelize: Degree of parallelism used when running the LLM program.
        autolog: Whether to automatically log select function calls that occur
            during the execution of the LLM program.
    """
    model_config = pydantic.ConfigDict(extra="forbid", populate_by_name=True)

    id: Optional[int] = None
    name: Optional[str] = None
    llm_program: str = pydantic.Field(alias="llm_program_fully_qualified_name")
    replicas: int = 1
    parallelize: int = 1
    autolog: bool = True

    @pydantic.model_validator(mode="after")
    def _check_id_and_name(self):
        """Ensure that either id or name is specified.
        
        Raises:
            TestSuiteValueError: If neither id nor name is specified.
        """
        if self.id is None and self.name is None:
            raise TestSuiteValueError("Either id or name must be specified.")
        return self

    @pydantic.field_validator("llm_program", mode="before")
    @classmethod
    def _extract_fully_qualified_llm_program_name(
        cls: _T_Config, v: Any) -> Any:
        """Return the fully qualified name for the program, if applicable."""
        return _extract_fully_qualified_name(v)


# A test suite file path is either a string or a path-like object.
_TestSuiteFilePath = Union[str, os.PathLike]


def _get_components_from_file(
    path: _TestSuiteFilePath
) -> Dict[
    str,
    Union[List[TestCase], List[QualityMeasure], List[HparamSpec], Config]]:
    """Return a dictionary of test suite components from a YAML file.
    
    Args:
        path: Path to the YAML file.
    
    Returns:
        Dictionary of test suite components, with keys:
        - test_cases: List of test cases.
        - quality_measures: List of quality measures.
        - hparam_specs: List of hyperparameter specifications.
        - config: Test suite config.
    """
    with open(path, "r", encoding="utf-8") as f:
        yaml_content = yaml.safe_load(f)

    is_list_of_dicts = (
        isinstance(yaml_content, list) and
        all(isinstance(entry, dict) for entry in yaml_content))
    if not is_list_of_dicts:
        raise TestSuiteValueError(
            "Test suite file must contain a list/sequence of "
            "dictionaries/maps.")

    test_cases = []
    quality_measures = []
    hparam_specs = []
    config = None

    for entry in yaml_content:
        for key, value in entry.items():
            try:
                if key in ["test", "test case", "test_case"]:
                    test_cases.append(
                        TestCase._from_test_suite_file_syntax(value))  # pylint: disable=protected-access
                elif key in [
                    "quality",
                    "quality measure",
                    "quality_measure",
                    "measure"]:
                    quality_measures.append(QualityMeasure(**value))
                elif key in ["hparam", "hparam spec", "hparam_spec"]:
                    hparam_specs.append(HparamSpec(**value))
                elif key in ["config", "configuration"]:
                    if config is not None:
                        raise TestSuiteValueError(
                            "Test suite file must contain at most one config "
                            "block.")
                    config = Config(**value)
                else:
                    raise TestSuiteValueError(
                        f"Invalid entry in test suite file: {key}",
                        path)

            except pydantic.ValidationError as error:
                error_messages = []
                for error_content in error.errors():
                    error_messages.append(
                        f"{error_content['msg']}: "
                        f"{', '.join(map(str, error_content['loc']))}"
                    )
                error_message = "\n".join(error_messages)
                raise TestSuiteValueError(
                    error_message,
                    path) from error

    return {
        "test_cases": test_cases,
        "quality_measures": quality_measures,
        "hparam_specs": hparam_specs,
        "config": config,
    }


# Test suite components are classes that can be added to a test suite
# (e.g., test cases, quality measures, and hyperparameter specifications)
# or files that contain test suite components (e.g., paths to YAML files).
_TestSuiteComponent = Union[
    Config, TestCase, QualityMeasure, HparamSpec, _TestSuiteFilePath]


class TestSuite:
    """Test suite.
    
    A collection of test cases, quality measures, and hyperparameter
    specifications that can be run together.
    
    Attributes:
        config: Config for this test suite.
        test_cases: List of test cases to run.
        quality_measures: List of quality measures to compute.
        hparam_specs: List of hyperparameter specifications.
    """
    def __init__(
        self,
        id_or_name: Union[int, str],
        llm_program: Union[Callable, str]):
        """Create a test suite.
        
        Args:
            id_or_name: ID or name of the test suite.
            llm_program: LLM program to test. Either a Python object or a
                string containing the fully qualified name of the Python
                object. The Python object can be either a Python function or
                LangChain chain. If a string is passed, it must be in the
                format:
                `<fully qualified module name>:<fully qualified object name>`.
        """
        id, name = None, None  # pylint: disable=redefined-builtin
        if isinstance(id_or_name, int):
            id = id_or_name
        elif isinstance(id_or_name, str):
            name = id_or_name
        else:
            raise TypeError(
                "Invalid type for id_or_name. Expected int or str, "
                f"but got {type(id_or_name)}.")

        self.config = Config(
            id=id,
            name=name,
            llm_program=llm_program)
        self.test_cases: List[TestCase] = []
        self.quality_measures: List[QualityMeasure] = []
        self.hparam_specs: List[HparamSpec] = []

    def add(
        self,
        *args: Union[_TestSuiteComponent, List[_TestSuiteComponent]]):
        """Add test cases, quality measures, or hyperparameter specifications.

        Args:
            *args: One or more test cases, quality measures, hyperparameter
                specifications, or path to a YAML file containing test suite
                components to add to the test suite. If a list is passed,
                each item in the list is added to the test suite. Any Config
                objects passed are ignored.
        
        Raises:
            TypeError: If an invalid type is passed.
        """
        for arg in args:
            if isinstance(arg, list):
                for item in arg:
                    self.add(item)
            elif isinstance(arg, TestCase):
                self.test_cases.append(arg)
            elif isinstance(arg, QualityMeasure):
                self.quality_measures.append(arg)
            elif isinstance(arg, HparamSpec):
                self.hparam_specs.append(arg)
            elif isinstance(arg, Config):
                # Ignore config blocks.
                continue
            elif isinstance(arg, (str, os.PathLike)):
                self.add(list(_get_components_from_file(arg).values()))
            else:
                raise TypeError(
                    "Invalid type. Expected TestCase, QualityMeasure, "
                    f"HparamSpec, Config, or path to yaml file, but got "
                    f"{type(arg)}.")

    def _validate(self):
        """Validate the test suite.
        
        Perform the following checks to ensure that the test suite is valid:
        - LLM program is callable.
        - Test cases inputs can be bound to the LLM program signature.

        Raises:
            TestSuiteValueError: If the test suite is invalid.
        """
        # Check that the LLM program is callable.
        llm_program = self.config.llm_program
        try:
            llm_program_callable = util.LazyCallable(
                llm_program).get_callable()
        except Exception as error:
            # It is not trival identify the relevant Exception subtypes that
            # should be considered actual validation errors, so we catch all
            # exceptions and raise a generic validation error with the
            # exception message appended.
            raise TestSuiteValueError(
                f"LLM program {llm_program} is not callable. "
                f"{error}") from error

        # Check that the test cases inputs can be bound to the LLM program
        # signature.
        # TODO(#323): Include validation for LangChain objects.
        if inspect.isfunction(llm_program_callable):
            llm_program_signature = inspect.signature(llm_program_callable)
            for test_case in self.test_cases:
                test_case._validate_inputs_with_signature(llm_program_signature)  # pylint: disable=protected-access

        # TODO(#324): Remove any duplicate test suite components.

    def run(
        self,
        *,
        replicas: Optional[int] = None,
        parallelize: Optional[int] = None):
        """Run the test suite.

        Args:
            replicas: Number of replicated executions to perform for each
                (test case, unique set of hyperparameter values) pair. Defaults
                to 1.
            parallelize: Number of LLM program executions to run in parallel.
                Defaults to 1.
        """
        auth_access_token = auth_session.get_auth_session().access_token

        if replicas is None and parallelize is None:
            self._run(auth_access_token)
        else:
            # Test suites are run using the settings in their own config. In
            # order to functionally modify the config for only this run, we
            # create a shallow copy of the test suite and its config.
            test_suite_to_run = copy.copy(self)
            test_suite_to_run.config = copy.copy(self.config)
            if replicas is not None:
                test_suite_to_run.config.replicas = replicas
            if parallelize is not None:
                test_suite_to_run.config.parallelize = parallelize

            test_suite_to_run._run(auth_access_token)  # pylint: disable=protected-access

    def _run(
        self,
        auth_access_token: str,
        *,
        prompt_open_results: bool = False):
        """Run the test suite using its current config.
        
        Args:
            auth_access_token: Access token for authentication.
            prompt_open_results: Whether to prompt the user to open the
                results in the browser.
        """
        self._validate()
        execute.execute_test_suite(
            test_suite=self,
            auth_access_token=auth_access_token,
            prompt_open_results=prompt_open_results)

    def _get_run_request(self) -> wire_model.CreateTestSuiteRunRequest:
        """Return a CreateTestSuiteRunRequest for this test suite.
        
        Returns:
            A CreateTestSuiteRunRequest for this test suite.
        """
        return wire_model.CreateTestSuiteRunRequest(
            test_suite_id_or_name=(
                self.config.id or self.config.name),
            test_cases=[
                test_case.model_dump()
                for test_case in self.test_cases],
            quality_measures=[
                quality_measure.model_dump()
                for quality_measure in self.quality_measures],
            hparam_specs=[
                hparam_spec.model_dump()
                for hparam_spec in self.hparam_specs],
            llm_program_details=util.LazyCallable(
                self.config.llm_program).get_program_details(),
            replicas=self.config.replicas,
            parallelize=self.config.parallelize,
        )


def get_test_suites(cli_args: Dict[str, Any]) -> List[TestSuite]:
    """Return a list of test suites.

    Parse the relevant arguments from the given command line arguments.
    Use a combination of the command line arguments and the test suite file
    contents (where the test suite file is specified by the required
    `test_suite_file_paths` command line argument) to construct the test
    suites. The config for each test suite is constructed based on the
    following hierarchy of configuration sources:
    1. Command line arguments.
    2. Test suite file arguments.
    3. Default arguments.
    In the case of a conflict, the lower-numbered item in the list takes
    precedence.
    
    Args:
        cli_args: Dictionary of command line arguments. Note that not all the
            command line arguments are used in this function.

    Returns:
        A list of `TestSuite` objects.

    Raises:
        TestSuiteValueError: If any test suite is invalid.
    """
    test_suite_file_paths = cli_args.get("test_suite_file_paths")
    if test_suite_file_paths is None:
        raise ValueError("`test_suite_file_paths` must be defined.")

    test_suites = []
    for test_suite_file_path in test_suite_file_paths:
        try:
            # Get the test suite components from the test suite file.
            test_suite_components = _get_components_from_file(
                test_suite_file_path)
            test_suite_config: Optional[Config] = test_suite_components[
                "config"]
            if test_suite_config is None:
                raise TestSuiteValueError(
                    "Test suite file must contain a config.")

            # Update the test suite config with the command line arguments.
            for key, value in cli_args.items():
                if key in Config.model_fields and value is not None:
                    setattr(test_suite_config, key, value)

            # Create the test suite.
            test_suite = TestSuite(
                id_or_name=test_suite_config.id or test_suite_config.name,
                llm_program=test_suite_config.llm_program)
            test_suite.config = test_suite_config
            test_suite.add(list(test_suite_components.values()))
            test_suites.append(test_suite)

        except TestSuiteValueError as error:
            # Add details about the source of the error.
            error.path = test_suite_file_path
            raise error

    return test_suites
