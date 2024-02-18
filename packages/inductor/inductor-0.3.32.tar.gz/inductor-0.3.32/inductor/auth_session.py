# Copyright 2023 Inductor, Inc.
"""Authentication session management for Inductor client."""

import dataclasses
import datetime
import json
import os
import pathlib
import time
from typing import Any, Optional, Union
from urllib import parse
import uuid

import auth0
from auth0 import rest
import requests
import typer

from inductor import backend_client, config, util, wire_model


_settings = config.Settings()


class AuthError(Exception):
    """An authentication error."""

    def __init__(self, message: str):
        """Initialize an authentication error.

        Args:
            message: The error message.
        """
        super().__init__(message)


class AuthSession:
    """An auth session object that stores the access token and its expiration.

    The AuthSession can be initiated from a secret key.  If a secret key is
    not set or not inside `~/.inductor/credentials` it tries to get it from the
    environment variable `INDUCTOR_SECRET_KEY`.  If the session is expired, it
    renews automatically when the access token is requested.
    """

    def __init__(self):
        """Initialize an AuthSession object."""
        self._access_token = None
        self._expiration = None
        self._initialized = False
        self._file_path = pathlib.Path(
            pathlib.Path.home(), ".inductor", "credentials"
        )

        self.init()

    @property
    def access_token(self):
        """The access token."""
        self._renew_expired()
        return self._access_token

    @property
    def initialized(self):
        """The initialization status of the session."""
        return self._initialized

    def _set_expiration(self, value: Union[str, datetime.datetime]):
        """Sets the expiration datetime of the access token.
        
        Args:
            value: The expiration datetime of the access token.  If str is
                given, it should be in ISO format.

        Raises:
            ValueError: If the value is not str or datetime.
        """
        if isinstance(value, str):
            self._expiration = datetime.datetime.fromisoformat(value)
        elif isinstance(value, datetime.datetime):
            self._expiration = value
        else:
            raise ValueError("Invalid expiration value.")

    def is_expired(self):
        """Checks if the session is expired."""
        if self._expiration is None:
            return True
        # Buffer the expiration time by 2 seconds.
        expiration = self._expiration - datetime.timedelta(seconds=2)
        return expiration < datetime.datetime.now(datetime.timezone.utc)

    def init(
        self,
        secret_key: Optional[str] = None,
        access_token: Optional[str] = None,
        expires_in: Optional[str] = None,
    ) -> bool:
        """Initiates the session.

        It can be initiated from a secret key or from a secret key, an access
        token and its expiration.  If secret key is not set, this method tries
        to get it from the environment variable `INDUCTOR_SECRET_KEY`, or
        otherwise from the credentials file `~/.inductor/credentials` if it
        exists.  It uses the secret key to get a new access token from the
        server.

        It stores the new session in a file if `INDUCTOR_SECRET_KEY` is not set
        and the credentials file `~/.inductor/credentials` does not exist.

        Args:
            secret_key: The secret key.
            access_token: The access token.
            expires_in: The number of seconds in which the access token will
                expire.
        
        Returns:
            True if the session was initiated, False otherwise.

        Raises:
            AuthError: If an error occurs during the authentication with
                the Inductor server endpoint.
        """
        if secret_key is None:
            if _settings.inductor_secret_key is None:
                self._initialized = self._load_session()
                return self._initialized
            secret_key = _settings.inductor_secret_key
        if access_token is None:
            headers = {"content-type": "application/x-www-form-urlencoded"}
            inductor_token_url = parse.urljoin(
                _settings.inductor_api_url, "/oauth/token")
            response = requests.post(
                inductor_token_url,
                data={"secret_key": secret_key},
                headers=headers,
                timeout=5.0,
            )
            if response.ok:
                parsed = _response_content(response)
                access_token = parsed.get("access_token")
                expires_in = parsed.get("expires_in")
            else:
                error = response.json()
                raise AuthError(error.get("detail"))
        expiration = datetime.datetime.now(
            datetime.timezone.utc
        ) + datetime.timedelta(seconds=expires_in)
        self._set_expiration(expiration)
        self._access_token = access_token
        self._initialized = True
        # If the secret key is not set in _settings,
        # save the session to the file.
        if _settings.inductor_secret_key is None:
            self._save_session(secret_key)
        return True

    def _renew_expired(self, secret_key: Optional[str] = None):
        """Renews the session if it is expired.

        Checks if the session is expired and renews it if necessary.

        Args:
            secret_key: The secret key.

        Raises:
            AuthError: If failed to renew the session.
        """
        if self.is_expired():
            if not self.init(secret_key):
                raise AuthError("Failed to renew expired session.")

    def _save_session(self, secret_key: str):
        """Saves the session to `~/.inductor/credentials`.

        If the file does not exist, creates it.  If the file exists, overwrites
        it with the new session.  If the secret key does not start with the
        secret key prefix, prepends the prefix before saving.

        Args:
            secret_key: The secret key used to encrypt the session.
        """
        if not secret_key.startswith(_settings.secret_key_prefix):
            secret_key = _settings.secret_key_prefix + secret_key
        # Create directory if it does not exist.
        self._file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._file_path, "w") as file:
            content = {
                "secret_key": secret_key,
                "access_token": self.access_token,
                "expiration": self._expiration.isoformat(),
            }
            json.dump(content, file, indent=4)

    def _load_session(self) -> bool:
        """Loads the session from `~/.inductor/credentials`.

        If the file does not exist, returns False.  If the file exists, loads
        the session from it.  If the session is expired and the secret key is
        present, renews the session.

        Raises:
            ValueError: If the credentials file is invalid or if the secret
                key is invalid.

        Returns:
            True if the session was loaded, False otherwise.
        """
        if not self._file_path.exists():
            return False
        with open(self._file_path, "r") as file:
            content = json.load(file)
            self._access_token = content.get("access_token")
            self._set_expiration(content.get("expiration"))
            secret_key: Optional[str] = content.get("secret_key")
            if (
                self._access_token is None
                or self._expiration is None
                or secret_key is None
            ):
                raise ValueError("Invalid credentials file.")
            if not secret_key.startswith(_settings.secret_key_prefix):
                raise ValueError("Invalid secret key.")
            self._renew_expired(secret_key)
        return True


def _to_auth0_response(response: requests.Response) -> rest.Response:
    """Converts a response from an Auth0 endpoint to an Auth0 response.

    Args:
        response: The response from an Auth0 endpoint.

    Returns:
        An Auth0 response object.
    """
    if not response.text:
        return rest.EmptyResponse(response.status_code)
    try:
        return rest.JsonResponse(response)
    except ValueError:
        return rest.PlainResponse(response)


def _response_content(response: requests.Response) -> Any:
    """Extracts and returns response's content.

    Args:
        response: The response from an Auth0 endpoint.

    Returns:
        The content of the response.
    """
    return _to_auth0_response(response).content()


@dataclasses.dataclass
class _DeviceCodeResponse:
    """A response from the Auth0 device code endpoint."""

    device_code: str
    user_code: str
    verification_uri: str
    verification_uri_complete: str
    expires_in: int
    interval: int


@dataclasses.dataclass
class _TokenResponse:
    """A response from the Auth0 token endpoint."""

    access_token: str
    refresh_token: str
    id_token: str
    scope: str
    expires_in: int
    token_type: str


def get_device_code() -> _DeviceCodeResponse:
    """Gets a device code from Auth0.

    Returns:
        A device code response.
    """
    data = {
        "client_id": _settings.auth0_client_id,
        "audience": _settings.inductor_hosted_api_url,
        "scope": "profile email openid offline_access",
    }
    headers = {"content-type": "application/x-www-form-urlencoded"}
    device_code_url = parse.urljoin(
        f"https://{_settings.auth0_domain}", "/oauth/device/code")
    response = requests.post(
        device_code_url,
        data=data,
        headers=headers,
        timeout=5.0,
    )
    try:
        parsed = _response_content(response)
        return _DeviceCodeResponse(**parsed)
    except auth0.Auth0Error as e:
        raise AuthError(e.message) from e


def poll_tokens(
    auth0_device_id: str,
    device_code: str,
    interval: int
) -> _TokenResponse:
    """Polls Auth0 /oauth/token endpoint.

    Poll the Auth0 /oauth/token endpoint using device_code grant type until
    the tokens (refresh_token and access_token) are ready.

    Args:
        auth0_device_id: The ID to be used to identify the device to Auth0.
        device_code: The device code.
        interval: The polling interval (seconds).

    Returns:
        A token response.

    Raises:
        AuthError: If an error that is not "authorization_pending" or
            "slow_down" occurs during the polling.
    """
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        # The user-agent is used to identify the device.
        "user-agent": auth0_device_id
    }
    data = {
        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
        "device_code": device_code,
        "client_id": _settings.auth0_client_id,
    }
    while True:
        try:
            token_url = parse.urljoin(
                f"https://{_settings.auth0_domain}", "/oauth/token")
            response = requests.post(
                token_url,
                data=data,
                headers=headers,
                timeout=5.0,
            )
            if response.ok:
                parsed = _response_content(response)
                return _TokenResponse(**parsed)
        except auth0.Auth0Error as e:
            if e.error_code == "authorization_pending":
                time.sleep(interval)
            elif e.error_code == "slow_down":
                time.sleep(interval)
            elif e.error_code == "expired_token":
                raise AuthError("Authentication failed: login page timed out. "  # pylint: disable=raise-missing-from
                                "Please try again.")
            else:
                raise AuthError("Authentication failed.")  # pylint: disable=raise-missing-from


def get_auth_session() -> AuthSession:
    """Returns a valid and not expired authenticated session.

    If the session is expired, the user is prompted to authenticate.  If
    the authentication fails, the program is aborted.
    
    Returns:
        An AuthSession object.
    """
    try:
        session = AuthSession()
        if not session.initialized:
            auth0_device_id = str(uuid.uuid4())
            device_code = get_device_code()
            typer.echo(f"Please go to {device_code.verification_uri_complete} "
                        "and log in, in order to securely authenticate the "
                        "Inductor CLI.")
            typer.echo("After you have logged in, please return here.")
            # If the user is running the CLI in VS Code, then we do not display
            # a prompt in the terminal to gate opening the authentication page
            # in the browser, as VS Code's interface will automatically display
            # such a prompt.  We also do not display such a prompt if the user
            # is running in Google Colab.
            if os.environ.get("TERM_PROGRAM") == "vscode":
                open_browser = True
            elif util.in_google_colab():
                open_browser = False
            else:
                open_browser = typer.confirm("Open in browser?")
            if open_browser:
                typer.launch(device_code.verification_uri_complete)
            typer.echo("Waiting for login ...")
            tokens = poll_tokens(
                auth0_device_id, device_code.device_code, device_code.interval)
            backend_client.create_api_key(
                wire_model.CreateApiKeyRequest(auth0_id=auth0_device_id),
                tokens.access_token)
            session.init(
                tokens.refresh_token,
                tokens.access_token,
                tokens.expires_in)
            typer.echo("You've successfully logged in and authenticated the "
                       "Inductor CLI!")
        return session
    except AuthError as e:
        typer.echo(e)
        raise typer.Abort() from e
    except ValueError as e:
        typer.echo(e)
        raise typer.Abort() from e
