# Copyright 2023 Inductor, Inc.
"""Types used by backend API that powers Inductor's client (CLI and library)."""

import datetime
from typing import Any, Dict, List, Literal, Optional, TypeVar, Union

import pydantic


# Field definitons
_RESTRICTED_NAME_FIELD = pydantic.Field(
    max_length=1000, pattern=r"^[a-zA-Z0-9_-]+$")
_SUBRESOURCE_NAME_FIELD = pydantic.Field(max_length=500)


class CreateApiKeyRequest(pydantic.BaseModel):
    """Request body type for create API key endpoint.

    Attributes:
        auth0_id: Auth0 ID of the API key.
    """
    auth0_id: str


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


class QualityMeasure(pydantic.BaseModel):
    """A quality measure.
    
    Attributes:
        name: Human-readable name of this quality measure.
        evaluator: Evaluator for this quality measure.  Determines whether
            this quality measure will be evaluated by running a function,
            or via human inspection.
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

    name: str = _SUBRESOURCE_NAME_FIELD
    evaluator: Literal["FUNCTION", "HUMAN", "LLM"]
    evaluation_type: Literal["BINARY", "RATING_INT"]
    spec: Union[str, Dict[str, str]]


class HparamSpec(pydantic.BaseModel):
    """Specification of set of hyperparameter values to use for test suite run.

    Attributes:
        hparam_name: Name of hyperparameter.
        hparam_type: Type of hyperparameter.
        values: List of hyperparameter values.
    """
    model_config = pydantic.ConfigDict(extra="forbid", populate_by_name=True)

    hparam_name: str = pydantic.Field(max_length=500, alias="name")
    hparam_type: Literal["SHORT_STRING", "TEXT", "NUMBER"] = pydantic.Field(
        alias="type")
    values: List[Any]


class ProgramDetails(pydantic.BaseModel):
    """Details of an LLM program.

    Attributes:
        fully_qualified_name: Fully qualified name of the LLM program.
        inputs_signature:  Map between input parameter names to strings
            indicating the corresponding parameter types (or to null for
            input parameters that do not have type annotations).
        program_type: Type of LLM program.
    """
    fully_qualified_name: str
    inputs_signature: Dict[str, Optional[str]]
    program_type: Literal["FUNCTION", "LANGCHAIN"]


class LoggedValue(pydantic.BaseModel):
    """A logged value associated with an LLM program execution.

    Attributes:
        value: The logged value.
        description: Description of the logged value (if any).
        after_complete: Whether the logged value was logged after the LLM
            program completed (as opposed to during its execution).
    """
    value: Any
    description: Optional[str] = None
    after_complete: bool


class DirectEvaluation(pydantic.BaseModel):
    """A direct evaluation of a quality measure.
    
    Attributes:
        quality_measure_id: ID of the quality measure that was evaluated.
        value_bool: The output of the quality measure, if boolean.
        value_int: The output of the quality measure, if an integer.
    """
    quality_measure_id: int
    value_bool: Optional[bool] = None
    value_int: Optional[int] = None


# TODO: This class is currently not used to transmit data to the backend, but
# instead is a placeholder until the backend supports recording quality measure
# execution details (i.e. errors, stdout, and stderr).
class QualityMeasureExecutionDetails(pydantic.BaseModel):
    """Details of a quality measure execution.

    Attributes:
        input: The input to the quality measure.
        output: The output of the quality measure, if available.  Should be
            None if the execution terminated with an error.
        error: If an error occurred during quality measure execution, this
            field should contain a specification of the error.
        stdout: The content printed to stdout during the quality measure's
            execution.
        stderr: The content printed to stderr during the quality measure's
            execution.
    """
    input: Any
    output: Optional[Any] = None
    error: Optional[str] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None


class ExecutionDetails(pydantic.BaseModel):
    """An LLM program execution.

    Attributes:
        mode: Mode in which this execution was performed (e.g., via CLI, or as
            part of a deployment), if known.
        inputs: JSON-serializable mapping from input argument name to input
            value.
        hparams: JSON-serializable mapping from hyperparameter name to
            hyperparameter value.
        output: The output of the LLM program, if available.  Should be None
            if the execution terminated with an error, without producing an
            output.
        error: If an error occurred during LLM program execution, this column
            should contain a specification of the error.
        stdout: The content printed to stdout during the LLM program's
            execution.
        stderr: The content printed to stderr during the LLM program's
            execution.
        execution_time_secs: The total wall clock time elapsed during this
            execution.
        started_at: The timestamp at which the execution started.
        ended_at: The timestamp at which the execution ended (whether
            successfully or due to an error).
        logged_values: The values logged during the LLM program's execution.
        direct_evaluations: The direct evaluations performed during the LLM
            program's execution.
    """
    mode: Literal["CLI", "DEPLOYED"]
    inputs: Dict[str, Any]
    hparams: Optional[Dict[str, Any]] = None
    output: Optional[Any] = None
    error: Optional[str] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    execution_time_secs: float
    started_at: datetime.datetime
    ended_at: datetime.datetime
    logged_values: Optional[List[LoggedValue]] = None
    direct_evaluations: Optional[List[DirectEvaluation]] = None


class CreateTestSuiteRequest(pydantic.BaseModel):
    """Request body for create test suite endpoint.

    Attributes:
        name: Name of test suite. Test suite names must be unique per user.
        description: Description of test suite.
    """
    name: str = _RESTRICTED_NAME_FIELD
    description: Optional[str] = None


class CreateTestSuiteResponse(pydantic.BaseModel):
    """Response for create test suite endpoint upon successful creation.
    
    Attributes:
        id: ID of the created test suite.
    """
    id: int


# Type variable for the CreateTestSuiteRunRequest class.
_T_CreateTestSuiteRunRequest = TypeVar(  # pylint: disable=invalid-name
    "_T_CreateTestSuiteRunRequest", bound="CreateTestSuiteRunRequest")


class CreateTestSuiteRunRequest(pydantic.BaseModel):
    """Request body for create test suite run endpoint.

    Attributes:
        test_suite_id: ID of test suite to run.
        test_suite_name: Name of test suite to run.
        test_cases: List of test cases.
        quality_measures: List of quality measures (if any).
        hparam_specs: List of hyperparameter specifications (if any).
        llm_program_details: Details of LLM program to run.
        replicas: Number of times that LLM program will be run on each pair of
            (test case, set of hyperparameters).
        parallelize: Degree of parallelism used for this run.
        started_at: The timestamp at which the test suite run started.
        test_suite_id_or_name: ID or name of test suite to run. This field is
            used for backwards compatibility with previous versions of the
            Inductor client. Use `test_suite_id` and `test_suite_name` instead.
    """
    test_suite_id: Optional[int] = None
    test_suite_name: Optional[str] = None
    test_cases: List[TestCase]
    quality_measures: Optional[List[QualityMeasure]] = None
    hparam_specs: Optional[List[HparamSpec]] = None
    llm_program_details: ProgramDetails
    replicas: int = 1
    parallelize: int = 1
    started_at: datetime.datetime = pydantic.Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
    test_suite_id_or_name: Optional[Union[int, str]] = None

    @pydantic.model_validator(mode="before")
    @classmethod
    def unpack_test_suite_id_or_name(
        cls: _T_CreateTestSuiteRunRequest, data: Any) -> Any:
        """Unpack test_suite_id_or_name into id or name fields."""
        if isinstance(data, dict):
            test_suite_id_or_name = data.get("test_suite_id_or_name")
            if test_suite_id_or_name is not None:
                if (isinstance(test_suite_id_or_name, int) and
                    "test_suite_id" not in data):
                    data["test_suite_id"] = test_suite_id_or_name
                elif (isinstance(test_suite_id_or_name, str) and
                      "test_suite_name" not in data):
                    data["test_suite_name"] = test_suite_id_or_name
        return data

    @pydantic.model_validator(mode="after")
    def check_test_suite_id_or_name(self):
        """Ensure that id or name is specified."""
        if self.test_suite_id is None and self.test_suite_name is None:
            raise ValueError(
                "Either test_suite_id or test_suite_name must be specified.")
        return self


class CreateTestSuiteRunResponse(pydantic.BaseModel):
    """Response for create test suite run endpoint upon successful creation.
    
    Attributes:
        test_suite_run_id: ID of the created test suite run.
        test_case_ids: IDs of the created test cases. The order of test case
            IDs is guaranteed to be the same as the order of test cases in the
            request.
        quality_measure_ids: IDs of the created quality measures. The order of
            quality measure IDs is guaranteed to be the same as the order of
            quality measures in the request.
        hparam_spec_ids: IDs of the created hyperparameter specifications. The
            order of hyperparameter specification IDs is guaranteed to be the
            same as the order of hyperparameter specifications in the request.
        url: URL at which the created test suite run can be accessed.
    """
    test_suite_run_id: int
    test_case_ids: List[int]
    quality_measure_ids: List[int]
    hparam_spec_ids: List[int]
    url: str


class LogTestCaseExecutionRequest(pydantic.BaseModel):
    """Request body for log test case execution endpoint.

    Attributes:
        test_suite_run_id: ID of test suite run as part of which this
            execution occurred (if any).
        test_case_id: ID of test case on which this execution occurred.
        test_case_replica_index: Index of execution replica on test case given
            by test_case_id. Replica indices should start at zero.
        execution_details: Details of the test case execution.
    """
    test_suite_run_id: int
    test_case_id: int
    test_case_replica_index: int
    execution_details: ExecutionDetails


class CompleteTestSuiteRunRequest(pydantic.BaseModel):
    """Request body for complete test suite run endpoint.

    Contains all remaining fields required by TestSuiteRun backend data model
    that have not already been logged.

    Attributes:
        test_suite_run_id: ID of the test suite run to complete.
        ended_at: The timestamp at which the test suite run ended.
    """
    test_suite_run_id: int
    ended_at: datetime.datetime


class LogLlmProgramExecutionRequest(pydantic.BaseModel):
    """Request body for log LLM program execution endpoint.

    Attributes:
        program_details: Details of the LLM program.
        execution_details: Details of the LLM program execution.
    """
    program_details: ProgramDetails
    execution_details: ExecutionDetails
