import os
from typing import AsyncGenerator

import pytest
from yarl import URL

from transformerbeeclient import (
    AuthenticatedTransformerBeeClient,
    TransformerBeeClient,
    UnauthenticatedTransformerBeeClient,
)

_local_docker_url = URL("http://localhost:5021")


@pytest.fixture
async def unauthenticated_client() -> AsyncGenerator[TransformerBeeClient, None]:
    """
    A fixture that yields an unauthenticated client for the transformer.bee API running in a docker container
    on localhost.
    """
    client = UnauthenticatedTransformerBeeClient(base_url=_local_docker_url)
    yield client
    await client.close_session()


_test_system_url = URL("https://transformer.utilibee.io")


@pytest.fixture
async def oauthenticated_client() -> AsyncGenerator[TransformerBeeClient, None]:
    """
    A fixture that yields an OAuth client ID / client secret authenticated client for the transformer.bee API
    running in our online test system
    """
    # Those env variables shall be set by the Integration Test GitHub Action
    client_id = os.environ.get("AUTH0_TEST_CLIENT_ID")
    client_secret = os.environ.get("AUTH0_TEST_CLIENT_SECRET")
    assert client_id is not None
    assert client_secret is not None  # <-- use pytest.skip instead of assert for local tests
    client = AuthenticatedTransformerBeeClient(
        base_url=_test_system_url, oauth_client_id=client_id, oauth_client_secret=client_secret
    )
    yield client  # type:ignore[misc]
    await client.close_session()
