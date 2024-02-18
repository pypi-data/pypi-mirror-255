# Copyright 2023 Inductor, Inc.
"""Functionality for executing a test suite run."""

from __future__ import annotations
from concurrent import futures
import contextlib
import datetime
import itertools
import sys
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple, TYPE_CHECKING, Union

import inquirer
import rich
from rich import progress
import typer

import inductor
from inductor import backend_client, config, quality_measures, util, wire_model

if TYPE_CHECKING:
    from inductor.cli import data_model


def _execute_quality_measure_function(
    llm_program_output: Any,
    quality_measure: data_model.QualityMeasure,
    test_case: data_model.TestCase,
) -> Union[str, bool, int]:
    """Execute a function powered quality measure on the LLM program output.

    The function signature of the quality measure determines which arguments
    are passed to the function. The list of arguments is truncated to match
    the length of the function signature. Potential arguments in the order
    they are passed to the function are:
        - Output of the LLM program.
        - Test case inputs.
        - Test case itself.
        - quality_measure
    
    Args:
        llm_program_output: Output of the LLM program.
        quality_measure: Quality measure to be executed.
        test_case: Test case on which the LLM program was executed to
            produce llm_program_output.

    Returns:
        Output of the function specified in quality_measure's spec field.
    """
    callable_object = util.LazyCallable(quality_measure.spec)
    args = [
        llm_program_output,
        quality_measures.Inputs(test_case.inputs),
        test_case,
        quality_measure,
    ]
    inputs_signature = callable_object.inputs_signature
    quality_measure_output = callable_object(*args[:len(inputs_signature)])
    return quality_measure_output


def _execute_quality_measure_llm(
    llm_program_output: Any,
    quality_measure: data_model.QualityMeasure,
    test_case: data_model.TestCase,
) -> Union[str, bool, int]:
    """Execute a LLM powered quality measure on the LLM program output.

    Args:
        llm_program_output: Output of the LLM program.
        quality_measure: Quality measure.  Must have evaluator field equal
            to "LLM".
        test_case: Test case on which the LLM program was executed to
            produce llm_program_output.
    
    Raises:
        ValueError: If quality measure evaluator is not "LLM".

    Returns:
        Output of the quality measure.
    """
    if quality_measure.evaluator != "LLM":
        raise ValueError("Quality measure evaluator must be 'LLM'.")

    evaluation_type = quality_measure.evaluation_type
    if isinstance(quality_measure.spec, str):
        quality_measure_output = _execute_quality_measure_function(
            llm_program_output, quality_measure, test_case)

    elif isinstance(quality_measure.spec, dict):
        model = quality_measure.spec.get("model", "gpt-3.5-turbo")
        prompt = quality_measure.spec.get("prompt")
        if prompt is None:
            raise ValueError(
                "Quality measure spec must contain a 'prompt' key.")
        quality_measure_output = quality_measures.openai_llm_quality_measure(
            llm_program_output,
            model=model,
            prompt=prompt,
            inputs=quality_measures.Inputs(test_case.inputs),
            quality_measure=quality_measure,
            test_case=test_case)

    if isinstance(quality_measure_output, str):
        if evaluation_type == "BINARY":
            if quality_measure_output.strip().upper() in ("YES", "Y"):
                quality_measure_output = True
            elif quality_measure_output.strip().upper() in ("NO", "N"):
                quality_measure_output = False

        elif evaluation_type == "RATING_INT":
            quality_measure_output = int(quality_measure_output)

    return quality_measure_output


def _execute_test_case(
    test_suite_run_id: int,
    llm_program_fully_qualified_name: str,
    test_case: data_model.TestCase,
    test_case_id: int,
    test_case_replica_index: int,
    quality_measures: List[data_model.QualityMeasure],  # pylint: disable=redefined-outer-name
    quality_measure_ids: List[int],
    hparams: Dict[str, Any],
    auth_access_token: str,
    callables_in_main: List[Callable],
) -> Tuple[
    wire_model.LogTestCaseExecutionRequest,
    List[Dict[str, Union[
        int, str, wire_model.QualityMeasureExecutionDetails]]]]:
    """Run a test case and evaluate its quality measures.

    Sends the output of the test case and the outputs of the quality measures
    to the backend server.

    Args:
        test_suite_run_id: ID of test suite run.
        llm_program_fully_qualified_name: Fully qualified name of LLM program.
        test_case: Test case.
        test_case_id: ID of test case.
        test_case_replica_index: Index of test case replica.
        quality_measures: List of quality measures.
        quality_measure_ids: IDs of quality measures.
        hparams: Mapping from hyperparameter names to values.
        auth_access_token: Auth0 access token.
        callables_in_main: List of callables defined in __main__ that
            should be available when running the test case and
            evaluating its quality measures.  This function will add
            these callables to the __main__ module.  See TODO in
            execute_test_suite() for more details.
    
    Returns:
        A tuple of the LogTestCaseExecutionRequest and a list of invalid
            quality measures if any. Each invalid quality measure is a
            Dictionary with the following keys:
                "id": ID of quality measure.
                "name": Name of quality measure.
                "execution_details": wire_model.QualityMeasureExecutionDetails
                    object.
    """
    # See TODO in execute_test_suite() for more details.
    if callables_in_main:
        main_module = sys.modules["__main__"]
        for main_func in callables_in_main:
            setattr(main_module, main_func.__name__, main_func)

    started_at = datetime.datetime.now(datetime.timezone.utc)

    llm_program_stdout = None
    llm_program_stderr = None
    llm_program_error = None
    llm_program_output = None
    # Note: we use backslashes to split the `with` clause immediately below,
    # rather than enclosing in parentheses, because enclosing in parentheses
    # apparently causes a SyntaxError when running in Python 3.8.
    # pylint: disable=protected-access
    with inductor._capture_stdout_stderr(suppress=True) as (stdout, stderr), \
        inductor._capture_logged_values() as logged_values, \
        inductor._configure_for_test(hparams):
        # pylint: enable=protected-access

        try:
            # Run the LLM program.
            llm_program = util.LazyCallable(
                llm_program_fully_qualified_name)
            llm_program_output = llm_program(**test_case.inputs)
            if isinstance(llm_program_output, Iterator):
                llm_program_output = list(llm_program_output)
                if all(isinstance(value, str) for value in llm_program_output):
                    llm_program_output = "".join(llm_program_output)

        except Exception as error:  # pylint: disable=broad-except
            llm_program_error = str(error)

        llm_program_stdout = stdout.getvalue()
        llm_program_stderr = stderr.getvalue()

    ended_at = datetime.datetime.now(datetime.timezone.utc)

    # If the LLM program completed without error, run the executable quality
    # measures to generate a list of direct evaluations.
    direct_evaluations = []
    # For any executable quality measures that raises an error, or returns a
    # non-integer, non-boolean output, add it to the list of invalid quality
    # measures. TODO: Log quality measure errors on the backend.
    invalid_quality_measures = []
    if llm_program_error is None:

        # Run the executable quality measures.
        quality_measures_outputs = []
        for quality_measure, quality_measure_id in zip(
            quality_measures, quality_measure_ids):
            if quality_measure.evaluator in ("FUNCTION", "LLM"):
                # TODO: Record quality measure errors, stdout, and stderr on
                # the backend. See wire_model.QualityMeasureExecutionDetails
                # for the additional TODO of how these should be recorded.
                quality_measure_stdout = None
                quality_measure_stderr = None
                quality_measure_error = None
                quality_measure_output = None
                with inductor._capture_stdout_stderr(  # pylint: disable=protected-access
                    suppress=True) as (stdout, stderr):
                    try:
                        if quality_measure.evaluator == "FUNCTION":
                            quality_measure_output = (
                                _execute_quality_measure_function(
                                    llm_program_output,
                                    quality_measure,
                                    test_case))

                        elif quality_measure.evaluator == "LLM":
                            quality_measure_output = (
                                _execute_quality_measure_llm(
                                    llm_program_output,
                                    quality_measure,
                                    test_case))

                    except Exception as error:  # pylint: disable=broad-except
                        quality_measure_error = str(error)

                    quality_measure_stdout = stdout.getvalue()
                    quality_measure_stderr = stderr.getvalue()

                quality_measure_execution_details = (
                    wire_model.QualityMeasureExecutionDetails(
                        input=llm_program_output,
                        output=quality_measure_output,
                        error=quality_measure_error,
                        stdout=quality_measure_stdout,
                        stderr=quality_measure_stderr,
                    )
                )

                if quality_measure_error is not None:
                    invalid_quality_measures.append({
                        "id": quality_measure_id,
                        "name": quality_measure.name,
                        "execution_details": quality_measure_execution_details,
                    })

                else:
                    quality_measures_outputs.append((
                        quality_measure_id,
                        quality_measure,
                        quality_measure_execution_details,
                    ))


        # Create direct evaluations for the quality measures that are
        # executable and valid. If a quality measure that is executable
        # returns an output type that does not match the quality measure's
        # evaluation type, then add it to the list of invalid quality
        # measures and do not create a direct evaluation for it.
        for (
            quality_measure_id,
            quality_measure,
            quality_measure_execution_details,
        ) in quality_measures_outputs:
            quality_measure_output = quality_measure_execution_details.output
            if quality_measure.evaluation_type == "BINARY" and isinstance(
                quality_measure_output, bool):
                direct_evaluations.append(
                    wire_model.DirectEvaluation(
                        quality_measure_id=quality_measure_id,
                        value_bool=quality_measure_output))
            elif (quality_measure.evaluation_type == "RATING_INT" and
                    isinstance(quality_measure_output, int) and
                    # Required to prevent `bool` from being interpreted as
                    # `int`, since `bool` is a subclass of `int`.
                    not isinstance(quality_measure_output, bool)):
                direct_evaluations.append(
                    wire_model.DirectEvaluation(
                        quality_measure_id=quality_measure_id,
                        value_int=quality_measure_output))
            else:
                expected_output_type = (
                    type(True) if quality_measure.evaluation_type == "BINARY"
                    else type(5))
                quality_measure_execution_details.error = (
                    f"Invalid output type. Expected output type: "
                    f"{expected_output_type}. Actual output type: "
                    f"{type(quality_measure_output)}")
                invalid_quality_measures.append({
                    "id": quality_measure_id,
                    "name": quality_measure.name,
                    "execution_details": quality_measure_execution_details,
                })

    request_object = wire_model.LogTestCaseExecutionRequest(
        test_suite_run_id=test_suite_run_id,
        test_case_id=test_case_id,
        test_case_replica_index=test_case_replica_index,
        execution_details=wire_model.ExecutionDetails(
            mode="CLI",
            inputs=test_case.inputs,
            hparams=hparams or None,
            output=llm_program_output,
            error=llm_program_error,
            stdout=llm_program_stdout,
            stderr=llm_program_stderr,
            execution_time_secs=(ended_at - started_at).total_seconds(),
            started_at=started_at,
            ended_at=ended_at,
            logged_values=logged_values or None,
            direct_evaluations=direct_evaluations or None,
        )
    )

    backend_client.log_test_case_execution(request_object, auth_access_token)
    return request_object, invalid_quality_measures

def _get_hparams_combinations(
    hparam_specs: Optional[List[data_model.HparamSpec]] = None
    ) -> List[Dict[str, Any]]:
    """Get all combinations of hyperparameters.

    Given a list of hyperparameters and their possible values, return a list of
    dictionaries, where each dictionary represents a unique combination of
    hyperparameters.

    For example, if the given hyperparameters are:
    [
        data_model.HparamSpec(
            hparam_name="a",
            values=[1, 2],
        ),
        data_model.HparamSpec(
            hparam_name="b",
            values=[3, 4],
        ),
    ]
    then the returned list will be:
    [
        {"a": 1, "b": 3},
        {"a": 1, "b": 4},
        {"a": 2, "b": 3},
        {"a": 2, "b": 4},
    ]

    Args:
        hparam_specs: List of hyperparameters specs, where all hyperparameter
            specs have distinct names.

    Returns:
        A list of dictionaries, where each dictionary represents a unique
            combination of hyperparameters.

    Raises:
        ValueError: If hyperparameter names are not distinct.
    """
    if hparam_specs is None:
        return [{}]

    # Convert list of HparamSpec to dictionary
    hparams_dict = {
        hparam.name: hparam.values for hparam in hparam_specs}

    # Ensure that all hyperparameter names in hparam_specs are distinct.
    if len(hparams_dict) != len(hparam_specs):
        raise ValueError(
            "Hyperparameter names in hparam_specs must be distinct.")

    keys = list(hparams_dict.keys())
    value_lists = [hparams_dict[key] for key in keys]

    # Generate combinations.
    value_combinations = list(itertools.product(*value_lists))

    # Convert to dictionaries.
    hparam_combinations = []
    for value_combination in value_combinations:
        hparam_combinations.append(dict(zip(keys, value_combination)))

    return hparam_combinations


@contextlib.contextmanager
def _manage_test_suite_run(
    test_suite: data_model.TestSuite,
    auth_access_token: str) -> wire_model.CreateTestSuiteRunResponse:
    """Send requests to the server to manage the creation/completion of a run.
    
    Send a request to the server to create a test suite run. Then, yield the
    response, which contains test suite run metadata. On exit, send a request
    to the server to mark the test suite run as complete.

    Args:
        test_suite: Test suite.
        auth_access_token: Auth0 access token.

    Yields:
        CreateTestSuiteRunResponse object.
    """
    test_suite_run = test_suite._get_run_request()  # pylint: disable=protected-access
    test_suite_run_metadata = backend_client.create_test_suite_run(
        test_suite_run, auth_access_token)
    try:
        yield test_suite_run_metadata
    finally:
        backend_client.complete_test_suite_run(
            wire_model.CompleteTestSuiteRunRequest(
                test_suite_run_id=
                    test_suite_run_metadata.test_suite_run_id,
                ended_at=
                    datetime.datetime.now(datetime.timezone.utc)),
            auth_access_token)


def execute_test_suite(
    test_suite: data_model.TestSuite,
    auth_access_token: str,
    *,
    prompt_open_results: bool = False):
    """Execute a test suite.
    
    Execute a test suite while displaying relevant information to the user,
    including a progress bar.
    
    Args:
        test_suite: Test suite to execute.
        auth_access_token: Auth0 access token.
        prompt_open_results: Whether to prompt the user to open the test
            suite run results in a browser.
    """
    # TODO: #333 - This is a temporary workaround for an issue in Google Colab
    # where the process that executes each test case does not have references to
    # the callables defined in the `__main__` module. This workaround
    # attaches the callables defined in the `__main__` module to the `__main__`
    # module of the process that executes each test case. The future solution
    # is to use callables in the data_model instead of fully qualified names.
    callables_in_main = []
    def filter_and_append_callable(func_fqn: str):
        if func_fqn.startswith(("google_colab", "__main__")):
            callables_in_main.append(
                util.LazyCallable(func_fqn).get_callable())
    filter_and_append_callable(test_suite.config.llm_program)
    for quality_measure in test_suite.quality_measures:
        if quality_measure.evaluator == "FUNCTION":
            filter_and_append_callable(quality_measure.spec)
        elif (quality_measure.evaluator == "LLM"
              and isinstance(quality_measure.spec, str)):
            filter_and_append_callable(quality_measure.spec)

    # Note: we use backslashes to split the `with` clause immediately below,
    # rather than enclosing in parentheses, because enclosing in parentheses
    # apparently causes a SyntaxError when running in Python 3.8.
    with futures.ProcessPoolExecutor(
            max_workers=test_suite.config.parallelize) as executor, \
        _manage_test_suite_run(
            test_suite, auth_access_token) as test_suite_run_metadata:

        test_case_futures = []
        hparam_combinations = _get_hparams_combinations(test_suite.hparam_specs)
        for test_case_replica_index in range(test_suite.config.replicas):
            for hparams in hparam_combinations:
                for test_case, test_case_id in zip(
                    test_suite.test_cases,
                    test_suite_run_metadata.test_case_ids):
                    test_case_futures.append(executor.submit(
                        _execute_test_case,
                        test_suite_run_id=
                            test_suite_run_metadata.test_suite_run_id,
                        llm_program_fully_qualified_name=
                            test_suite.config.llm_program,
                        test_case=test_case,
                        test_case_id=test_case_id,
                        test_case_replica_index=test_case_replica_index,
                        quality_measures=test_suite.quality_measures,
                        quality_measure_ids=
                            test_suite_run_metadata.quality_measure_ids,
                        hparams=hparams,
                        auth_access_token=auth_access_token,
                        callables_in_main=callables_in_main,
                    ))

        typer.echo(f"Go to {test_suite_run_metadata.url} to view results.")
        if prompt_open_results:
            open_url = inquirer.confirm(
                message="Open in browser?", default=True)
            if open_url:
                typer.launch(test_suite_run_metadata.url)

        # Display progress bar and optionally print test outputs.
        with progress.Progress() as progress_bar:
            progress_task = progress_bar.add_task(
                "Test Cases",
                total=(test_suite.config.replicas *
                        len(test_suite.test_cases) *
                        len(hparam_combinations)))

            for future in futures.as_completed(test_case_futures):
                progress_bar.advance(progress_task)
                test_output, invalid_quality_measures = future.result()
                if test_output.execution_details.error is not None:
                    progress_bar.console.print(
                        "\n[red][bold][ERROR] Test case execution "
                        "raised an exception.[/bold] The following "
                        "execution will be recorded as FAILED and "
                        "quality measures will not be evaluated:[/red]")
                    progress_bar.console.print(test_output)
                elif config.verbose:
                    progress_bar.console.print(test_output)
                if invalid_quality_measures:
                    progress_bar.console.print(
                        "\n[red][bold][ERROR] One or more quality "
                        "measures raised an exception or returned an "
                        "invalid value.[/bold] The following quality "
                        "measures will not be recorded as part of this "
                        "test case execution:[/red]")
                    progress_bar.console.print(invalid_quality_measures)

        rich.print("Run complete.")
