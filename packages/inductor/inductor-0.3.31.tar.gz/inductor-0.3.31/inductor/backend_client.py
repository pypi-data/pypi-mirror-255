# Copyright 2023 Inductor, Inc.
"""Functions for interfacing with the Inductor backend."""
# TODO: Add --verbose mode for printing out the request and response.

import json
import os
from typing import Any, Dict

import httpx

from inductor import config, wire_model


# TODO: Cleanup these globals.
_MOCK_ENDPOINTS = False
_settings = config.Settings()
# _settings.inductor_api_url = "http://127.0.0.1:8000"
# Optional custom headers to include in all requests.
_custom_headers = None


def _get_custom_headers() -> Dict[str, Any]:
    """Get custom headers from the environment to include in all requests.

    Returns:
        A dictionary of custom headers, if any. Otherwise, an empty dictionary.
    """
    global _custom_headers
    if _custom_headers is not None:
        return _custom_headers
    custom_headers_tmp = {}
    custom_headers_env = os.environ.get("CUSTOM_REQUEST_HEADERS")
    if custom_headers_env:
        try:
            custom_headers_tmp = json.loads(custom_headers_env)
            if not isinstance(custom_headers_tmp, dict):
                raise ValueError(
                    "Environment variable, CUSTOM_REQUEST_HEADERS, is valid "
                    "JSON, but is not a JSON object.")
        except (json.JSONDecodeError, ValueError) as error:
            raise ValueError(
                f"Environment variable, CUSTOM_REQUEST_HEADERS, is defined, "
                f"but is not a valid JSON object. CUSTOM_REQUEST_HEADERS: "
                f"{custom_headers_env}"
            ) from error
    _custom_headers = custom_headers_tmp
    return _custom_headers


def _post_request(
    endpoint: str, request_body: Dict[str, Any], auth_access_token: str
) -> httpx.Response:
    """POST request to the backend.

    Args:
        endpoint: The endpoint to POST to. Should not begin with a slash.
        request: The request to POST.
        auth_access_token: Auth0 access token.

    Returns:
        The response from the backend.

    Raises:
        RuntimeError: If the response status code is not a successful response
            (i.e., if the response status code is not in the range (200 – 299)).
    """
    response = httpx.post(
        f"{_settings.inductor_api_url}/api/client/v1/{endpoint}",
        headers={
            "Authorization": f"Bearer {auth_access_token}",
            **_get_custom_headers(),
        },
        json=json.loads(request_body.model_dump_json()),
    )
    # TODO: These print statements should be avaialbe in --verbose mode.
    # print(f"Response: {response.text}")
    # print(f"Status code: {response.status_code}")
    # print(f"JSON: {response.json()}")
    if response.status_code < 200 or response.status_code >= 300:
        raise RuntimeError(
            f"POST request to `{endpoint}` failed with status code "
            f"{response.status_code} and response text: {response.text}."
        )
    return response


def create_api_key(
    request: wire_model.CreateApiKeyRequest,
    auth_access_token: str):
    """POST request to create an API key.
    
    Args:
        request: CreateApiKeyRequest object
        auth_access_token: Auth0 access token.
    """
    if _MOCK_ENDPOINTS:
        return
    _post_request("create-api-key", request, auth_access_token)


def create_test_suite(
    request: wire_model.CreateTestSuiteRequest,
    auth_access_token: str
) -> wire_model.CreateTestSuiteResponse:
    """POST request to create a test suite.

    Args:
        request: CreateTestSuiteRequest object
        auth_access_token: Auth0 access token.
    
    Returns:
        CreateTestSuiteResponse object
    """
    if _MOCK_ENDPOINTS:
        return wire_model.CreateTestSuiteResponse(id=123)
    response = _post_request("create-test-suite", request, auth_access_token)
    return wire_model.CreateTestSuiteResponse(**response.json())


def create_test_suite_run(
    request: wire_model.CreateTestSuiteRunRequest,
    auth_access_token: str
) -> wire_model.CreateTestSuiteRunResponse:
    """POST request to create a test suite run.
    
    Args:
        request: CreateTestSuiteRunRequest object
        auth_access_token: Auth0 access token.
    
    Returns:
        CreateTestSuiteRunResponse object
    """
    if _MOCK_ENDPOINTS:
        return wire_model.CreateTestSuiteRunResponse(
            test_suite_run_id=123,
            test_case_ids=[1, 2, 3, 4, 5, 6],
            quality_measure_ids=[7, 8, 9, 10, 11, 12],
            hparam_spec_ids=[13, 14, 15, 16, 17, 18],
            url="http://localhost:5000/MOCK_URL",
        )
    response = _post_request(
        "create-test-suite-run", request, auth_access_token)
    return wire_model.CreateTestSuiteRunResponse(**response.json())


def log_test_case_execution(
    request: wire_model.LogTestCaseExecutionRequest,
    auth_access_token: str):
    """POST request to log test case execution.

    Args:
        request: LogTestCaseExecutionRequest object
        auth_access_token: Auth0 access token.
    """
    if _MOCK_ENDPOINTS:
        return
    _post_request("log-test-case-execution", request, auth_access_token)


def complete_test_suite_run(
    request: wire_model.CompleteTestSuiteRunRequest,
    auth_access_token: str):
    """POST request to complete test suite run.

    Args:
        request: CompleteTestSuiteRunRequest object
        auth_access_token: Auth0 access token.
    """
    if _MOCK_ENDPOINTS:
        return
    _post_request("complete-test-suite-run", request, auth_access_token)


def log_llm_program_execution_request(
    request: wire_model.LogLlmProgramExecutionRequest,
    auth_access_token: str):
    """POST request to log LLM program execution.

    Args:
        request: LogLlmProgramExecutionRequest object
        auth_access_token: Auth0 access token.
    """
    if _MOCK_ENDPOINTS:
        return
    _post_request("log-llm-program-execution", request, auth_access_token)


# def get_existing_test_suites() -> List[str]:
#     """TODO"""
#     existing_test_suites = ["test_suite_1", "test_suite_2"]
#     return existing_test_suites
