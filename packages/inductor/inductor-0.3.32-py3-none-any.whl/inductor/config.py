# Copyright 2023 Inductor, Inc.
"""Inductor client configuration."""

from typing import Optional

import pydantic_settings


# TODO: Add levels of verbosity and possibly integrate it with a logger.
verbose = False


class Settings(pydantic_settings.BaseSettings):
    """Settings for the Inductor client.
    
    Settings are loaded from the following sources, in order of increasing
    precedence:
    1. Initialized values in this class
    2. Environment variables
    
    Attributes:
        auth0_domain: The Auth0 domain.
        auth0_client_id: The Auth0 client ID.
        inductor_api_url: The Inductor API URL.
        inductor_hosted_api_url: The Inductor-hosted API URL.
        inductor_secret_key: The user's Inductor secret key.  If this is set,
            the client will use this secret key for authentication instead of
            prompting the user to authenticate.
        secret_key_prefix: The prefix for the secret key.
    """

    auth0_domain: str = "login.inductor.ai"
    auth0_client_id: str = "YFeXBAUixEVB3e9sM5e7XDZr4FEHH5XX"
    inductor_api_url: str = "https://app.inductor.ai"
    inductor_hosted_api_url: str = "https://app.inductor.ai"
    inductor_secret_key: Optional[str] = None
    secret_key_prefix: str = "isk_"

    model_config = pydantic_settings.SettingsConfigDict(extra="ignore")
