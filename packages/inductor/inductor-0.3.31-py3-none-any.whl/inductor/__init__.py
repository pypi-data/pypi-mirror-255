# Copyright 2023 Inductor, Inc.
"""Inductor client library."""

import contextlib
import contextvars
import copy
import datetime
import functools
import inspect
import io
import sys
import traceback
from typing import Any, Callable, Dict, Iterator, List, Optional, TextIO, Tuple, TypeVar

from inductor import auth_session, backend_client, util, wire_model
from inductor.quality_measures import Inputs
from inductor.cli.data_model import HparamSpec, QualityMeasure, TestCase, TestSuite


# The following module-private variables are used by the functions in
# the rest of this module to transmit information to and from LLM program
# executions.
# Whether the logger decorator (inductor.logger) is enabled. This is set to
# False when running tests to prevent the logger from sending duplicate data to
# the backend, in the case that the LLM program being tested uses the logger
# decorator.
_logger_decorator_enabled = True
# Context variable used to store the logged values for the current LLM program
# execution. This is a context variable instead of a global variable so that
# the logger will work correctly when running mutliple threads that each use
# the logger decorator. However, an exception will be raised if the logger
# decorated function itself uses multiple threads that each call inductor.log.
_logged_values = contextvars.ContextVar("logged_values", default=None)
# Dictionary of hyperparameter values for the current LLM program execution.
_hparams = {}
# Context variable used to store whether the current LLM program execution is
# the primary execution.
_primary_execution = contextvars.ContextVar("active_execution", default=True)


def hparam(name: str, default_value: Any) -> Any:
    """Return the value of the hyperparameter having the given name.

    Args:
        name: Name of hyperparameter value to be returned.
        default_value: Value that will be returned if a value has not
            been specified for the given name.
    """
    return _hparams.get(name, default_value)


def _log(
    value: Any, *, after_complete: bool, description: Optional[str] = None):
    """Log a value and associate it with the current LLM program execution.

    Args:
        value: The value to be logged.
        after_complete: Whether the value was logged after the LLM
            program execution completed.
        description: An optional human-readable description of the logged
            value.
    
    Raises:
        RuntimeError: If the LLM program execution was not initiated via the
            Inductor CLI, and the LLM program is not decorated with
            @inductor.logger.
    """
    logged_values = _logged_values.get()
    if logged_values is None:
        # We can not distinguish between the below two cases described in the
        # exception message, so we raise the same exception in both cases.
        raise RuntimeError(
            "Cannot call inductor.log outside of a function decorated with "
            "@inductor.logger, unless you are running `inductor test`. "
            "Also note that invoking inductor.log from a thread different "
            "from the one that initialized the logger (via the decorator or "
            "the CLI tool) is currently unsupported. If you require support "
            "for this, please contact Inductor support to submit a feature "
            "request.")
    logged_values.append(
        wire_model.LoggedValue(
            value=copy.deepcopy(value),
            description=description,
            after_complete=after_complete))


def log(value: Any, *, name: Optional[str] = None):
    """Log a value and associate it with the current LLM program execution.

    Args:
        value: The value to be logged.
        name: An optional human-readable name for the logged value.
    
    Raises:
        RuntimeError: If the LLM program execution was not initiated via the
            Inductor CLI, and the LLM program is not decorated with
            @inductor.logger.
    """
    _log(value, description=name, after_complete=False)


@contextlib.contextmanager
def _configure_for_test(hparams: Dict[str, Any]):
    """Configure the Inductor library for a test suite run.
    
    Disable the inductor.logger decorator by setting
    `inductor._logger_decorator_enabled` to False and set the inductor._hparams
    to the given hyperparameters. On exit, restore the original value of
    `inductor._logger_decorator_enabled` and set `inductor._hparams` to an
    empty dictionary.

    Args:
        hparams: A dictionary mapping hyperparameter names to values.
    """
    global _hparams
    global _logger_decorator_enabled
    orig_logger_decorator_enabled = _logger_decorator_enabled
    try:
        _hparams = hparams
        _logger_decorator_enabled = False
        yield
    finally:
        _hparams = {}
        _logger_decorator_enabled = orig_logger_decorator_enabled


@contextlib.contextmanager
def _capture_logged_values():
    """Capture values logged via log() calls.
    
    If logging has not already been initialized, initialize logging by setting
    the logged values context variable (`_logged_values`) to an empty list,
    and, on exit, set `_logged_values` to `None`.
    If logging has already been initialized, do nothing.
    In either case, yield the list of logged values.

    The purpose of this context manager is to manage the state of the
    logged values context variable, which should only be initialized
    once per LLM program execution.

    Yields:
        The list of logged values.
    """
    logged_values = _logged_values.get()
    initializing_logged_values = logged_values is None
    try:
        if initializing_logged_values:
            _logged_values.set([])
        yield _logged_values.get()
    finally:
        if initializing_logged_values:
            _logged_values.set(None)


@contextlib.contextmanager
def _capture_stdout_stderr(
    suppress: bool = False) -> Tuple[io.StringIO, io.StringIO]:
    """Capture stdout and stderr.
    
    On exit, restore the original stdout and stderr and close the yielded
    StringIO buffers (i.e., the yielded buffers' contents will be discarded
    when context manager exits).
    
    Args:
        suppress: Whether to suppress stdout and stderr. If True, the
            contents of stdout and stderr will be suppressed after being
            captured. If False, stdout and stderr will behave as normal,
            but their contents will still be captured.

    Yields:
        A tuple of streams used to capture stdout and stderr.
    """
    class Tee(io.StringIO):
        """A StringIO buffer that optionally writes to a file in addition to
        capturing the written string."""
        def __init__(self, file: Optional[TextIO]):
            """Override the constructor to store the file to which to write."""
            self.file = file
            super().__init__()

        def write(self, s: str):
            """Override the write method to write to the file (as merited)
            in addition to capturing the written string."""
            if self.file is not None:
                self.file.write(s)
            return super().write(s)

    stdout_capture = Tee(
        sys.stdout if not suppress else None)
    stderr_capture = Tee(
        sys.stderr if not suppress else None)

    # Save the original stdout and stderr.
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    # Redirect stdout and stderr to the Tee objects.
    sys.stdout = stdout_capture
    sys.stderr = stderr_capture
    try:
        yield (stdout_capture, stderr_capture)
    finally:
        # Restore the original stdout and stderr.
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        # Close the StringIO buffers.
        stdout_capture.close()
        stderr_capture.close()


@contextlib.contextmanager
def _manage_executions():
    """Manage the state of the primary execution context variable.

    Manage the state of the primary execution context variable
    (_primary_execution). If the variable is initially True, it is set to
    False and True is yielded. If the variable is initially False, False is
    yielded. On exit, the variable is restored to its original value.

    The purpose of this context manager is to allow the logger decorator to
    determine whether it is the primary (top-level) execution. This is
    necessary because the logger decorator should only send data to the
    backend if it is the primary execution. For example, when the logger
    decorator decorates a function that is called by another function also
    decorated with the logger decorator, the logger decorator should not send
    data to the backend during the inner function call.

    Yields:
        True if the primary execution context variable was True, False
        otherwise.
    """
    primary_execution = _primary_execution.get()
    if primary_execution:
        _primary_execution.set(False)
    try:
        yield primary_execution
    finally:
        _primary_execution.set(primary_execution)


def _log_completed_execution(
    *,
    output: Any,
    primary_execution: bool,
    llm_program: util.LazyCallable,
    input_args: Dict[str, Any],
    error: Optional[str] = None,
    stdout: Optional[str] = None,
    stderr: Optional[str] = None,
    logged_values: Optional[List[wire_model.LoggedValue]] = None,
    started_at: datetime.datetime,
    auth_access_token: str) -> Any:
    """Log the completion of an LLM program execution.

    If the LLM program execution is the primary execution, send the execution
    data to the backend. Otherwise, call the Inductor client's `log()`
    function to log this execution as part of the current overarching
    primary execution.

    Args:
        output: Result of the LLM program execution.
        primary_execution: Whether the LLM program execution is the primary
            execution.
        llm_program: LLM program that was executed.
        input_args: Input arguments to the LLM program.
        error: Error message, if any, that occurred during the LLM program
            execution.
        stdout: Captured stdout from the LLM program execution.
        stderr: Captured stderr from the LLM program execution.
        logged_values: Values logged during the LLM program execution.
        started_at: Time at which the LLM program execution started.
        auth_access_token: Access token used to authenticate the request to
            the backend.
    """
    ended_at = datetime.datetime.now(datetime.timezone.utc)

    if primary_execution:
        backend_client.log_llm_program_execution_request(
            wire_model.LogLlmProgramExecutionRequest(
                program_details=llm_program.get_program_details(),
                execution_details=wire_model.ExecutionDetails(
                    mode="DEPLOYED",
                    inputs=input_args,
                    hparams=_hparams or None,
                    output=output,
                    error=error,
                    stdout=stdout,
                    stderr=stderr,
                    logged_values=logged_values or None,
                    execution_time_secs=(
                        ended_at - started_at).total_seconds(),
                    started_at=started_at,
                    ended_at=ended_at,)),
            auth_access_token)

    else:
        log(
            {
                "llm_program":
                llm_program.fully_qualified_name,
                "inputs": input_args,
                "output": output
            },
            name="Nested LLM program execution")


def logger(func: Callable) -> Callable:
    """Log the inputs, outputs, and inductor.log calls of func.

    Use `logger` as a decorator to automatically log the arguments and return
    value of, as well as calls to inductor.log within, the decorated function.
    For example:
        @inductor.logger
        def hello_world(name: str) -> str:
            inductor.log(len(name), description="name length")
            return f"Hello {name}!"

    Args:
        func: The decorated function.
    
    Returns:
        Wrapped function.
    """
    try:
        auth_access_token = auth_session.get_auth_session().access_token
    except Exception as error:  # pylint: disable=broad-except
        traceback.print_exc()
        print(
            f"[ERROR] Exception occurred during setup of inductor.logger. "
            f"No data will be sent to Inductor through the logger decorator "
            f"for this session. {error}")
        # If an Exception occurs before defining the wrapper function, there
        # is no need to wrap the function.
        return func

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        if _logger_decorator_enabled:
            func_result = None
            func_error = None
            func_completed = False
            try:
                # Notes regarding the `with` clause immediately below:
                # - We use backslashes to split the clause, rather than
                # enclosing in parentheses, because enclosing in parentheses
                # apparently causes a SyntaxError when running in Python 3.8.
                # - We actually don't need to capture stdout and stderr if we
                # are not in the primary execution. However, since stdout and
                # stderr are not suppressed, the user will not be impacted, and
                # we allow stdout and stdout to be captured nonetheless to
                # simplify the code.
                with _capture_logged_values() as logged_values, \
                    _manage_executions() as primary_execution, \
                    _capture_stdout_stderr(suppress=False) as (stdout, stderr):

                    llm_program = util.LazyCallable(func)

                    # Get input arguments using the function's signature.
                    signature = inspect.signature(func)
                    bound_arguments = signature.bind(*args, **kwargs)
                    bound_arguments.apply_defaults()
                    input_args = copy.deepcopy(bound_arguments.arguments)

                    started_at = datetime.datetime.now(datetime.timezone.utc)

                    try:
                        func_result = func(*args, **kwargs)
                    except Exception as e:  # pylint: disable=broad-except
                        func_error = e
                    finally:
                        func_completed = True

                    # If the result is an iterator, we cannot make the
                    # assumption that the iterator can be re-used.
                    # Therefore we return a wrapper for the iterator that
                    # captures returned values and logs them when the
                    # iterator is exhausted.
                    if isinstance(func_result, Iterator):
                        _T_IteratorWrapper = TypeVar(
                            "_T_IteratorWrapper", bound="_IteratorWrapper")  # pylint: disable=invalid-name
                        class _IteratorWrapper:
                            """Iterator wrapper that captures yielded values.

                            When the iterator is exhausted, the wrapper logs
                            the completion of the LLM program execution to
                            Inductor.
                            """
                            def __init__(
                                self,
                                iterator: Iterator,
                                stdout: Optional[str] = None,
                                stderr: Optional[str] = None):
                                """Create an _IteratorWrapper.
                                
                                Args:
                                    iterator: The iterator to wrap.
                                    stdout: Captured stdout from the LLM
                                        program execution.
                                    stderr: Captured stderr from the LLM
                                        program execution.
                                """
                                self._iterator = iterator
                                self._completed_values = []
                                self._stdout = stdout
                                self._stderr = stderr
                                self._skip_logging = False

                            def __iter__(self) -> _T_IteratorWrapper:
                                return self

                            def __next__(self) -> Any:
                                """Get the next value from the iterator.

                                Add the returned value to the list of completed
                                values. If the iterator is exhausted or an
                                error occurs during iteration, log the
                                completion of the LLM program execution.

                                Returns:
                                    The next value from the iterator.
                                """
                                stop_signal_occurred = False
                                iteration_error = None
                                try:
                                    value = next(self._iterator)
                                except StopIteration as stop_signal:
                                    stop_signal_occurred = True
                                    raise stop_signal
                                except Exception as error:  # pylint: disable=broad-except
                                    iteration_error = error
                                    raise error
                                finally:
                                    if not self._skip_logging:
                                        try:
                                            if (stop_signal_occurred or
                                                iteration_error is not None):
                                                if all(
                                                    isinstance(value, str)
                                                    for value in self._completed_values  # pylint: disable=line-too-long
                                                ):
                                                    self._completed_values = "".join(  # pylint: disable=line-too-long
                                                        self._completed_values)
                                                _log_completed_execution(
                                                    output=self._completed_values,  # pylint: disable=line-too-long
                                                    primary_execution=primary_execution,  # pylint: disable=line-too-long
                                                    llm_program=llm_program,
                                                    input_args=input_args,
                                                    error=(str(iteration_error)
                                                        if iteration_error is not None else None),  # pylint: disable=line-too-long
                                                    started_at=started_at,
                                                    stdout=self._stdout,
                                                    stderr=self._stderr,
                                                    logged_values=logged_values,  # pylint: disable=line-too-long
                                                    auth_access_token=auth_access_token,  # pylint: disable=line-too-long
                                                )
                                                self._skip_logging = True
                                            else:
                                                self._completed_values.append(
                                                    copy.deepcopy(value))
                                        except Exception as wrapper_error:  # pylint: disable=broad-except
                                            self._skip_logging = True  # pylint: disable=line-too-long
                                            traceback.print_exc()
                                            print(
                                                f"[ERROR] Exception occurred "
                                                f"during iteration of the LLM "
                                                f"program result. No data will "  # pylint: disable=line-too-long
                                                f"be sent to Inductor as part of "  # pylint: disable=line-too-long
                                                f"this LLM program execution. "
                                                f"{wrapper_error}")
                                return value

                            def __getattr__(self, name: str) -> Any:
                                """Forward unknown attributes to the iterator.
                                
                                This allows the iterator wrapper to be used
                                as if it were the underlying iterator.

                                Args:
                                    name: Name of attribute to get.
                                
                                Returns:
                                    The requested attribute.
                                """
                                return getattr(self._iterator, name)

                        return _IteratorWrapper(
                            func_result,
                            stdout.getvalue(),
                            stderr.getvalue())

                    _log_completed_execution(
                        output=copy.deepcopy(func_result),
                        primary_execution=primary_execution,
                        llm_program=llm_program,
                        input_args=input_args,
                        started_at=started_at,
                        error=(str(func_error)
                               if func_error is not None else None),
                        stdout=stdout.getvalue(),
                        stderr=stderr.getvalue(),
                        logged_values=logged_values,
                        auth_access_token=auth_access_token,
                    )

                    if func_error is not None:
                        # If the LLM program execution failed, we re-raise the
                        # exception so that the user's program can handle it
                        # as desired.
                        raise func_error
                    return func_result

            except Exception as decorator_error:  # pylint: disable=broad-except
                traceback.print_exc()
                print(
                    f"[ERROR] Exception occurred in inductor.logger. No data "
                    f"will be sent to Inductor as part of this LLM program "
                    f"execution. {decorator_error}")
                if func_completed:
                    # If the LLM program execution completed, there is no
                    # need to rerun the LLM program. Rerunning the LLM program
                    # could significantly hurt performance or could cause
                    # wider issues if the LLM program has side effects.
                    if func_error is not None:
                        raise func_error  # pylint: disable=raise-missing-from
                    return func_result
                return func(*args, **kwargs)

        else:
            return func(*args, **kwargs)
    return wrapper
