"""
client contains the actual client
"""

import asyncio
import json
import logging
from abc import ABC
from datetime import datetime, timedelta
from itertools import count
from typing import Optional, Type

import aiohttp
import jwt
from aioauth_client import OAuth2Client
from aiohttp import ClientResponse, ClientSession, TCPConnector
from maus.edifact import EdifactFormatVersion
from pydantic import BaseModel
from yarl import URL

from transformerbeeclient.models.boneycomb import BOneyComb
from transformerbeeclient.models.marktnachricht import Marktnachricht
from transformerbeeclient.models.transformerapi import (
    Bo4eTransactionToEdifactRequest,
    Bo4eTransactionToEdifactResponse,
    EdifactToBo4eRequest,
    EdifactToBo4eResponse,
)
from transformerbeeclient.protocols import TransformerBeeClient

_logger = logging.getLogger(__name__)


class _ClientSessionMixin:  # pylint:disable=too-few-public-methods
    """
    Mixin for classes which need a client session
    """

    def __init__(self):
        self._session_lock = asyncio.Lock()
        self._session: Optional[ClientSession] = None
        self._session_usage_counter = count()
        self._session_usage_threshold = 100_000
        self._semaphore: asyncio.Semaphore = asyncio.Semaphore(100)
        # Don't allow more than 100 uses of a session at a time.
        # This together with the session usage threshold should prevent memory leaks and too many usages of the same
        # session at the same time

    async def _get_session(
        self,
        raise_for_status: bool = True,
        max_connections: Optional[int] = None,
        own_response_class: Optional[Type[aiohttp.ClientResponse]] = None,
    ) -> ClientSession:
        """
        returns a client session (that may be reused or newly created)
        """

        def _create_new_session() -> ClientSession:
            if max_connections is not None:
                self._connector = TCPConnector(limit_per_host=max_connections)
                if own_response_class is None:
                    return ClientSession(connector=self._connector, raise_for_status=raise_for_status)
                return ClientSession(
                    connector=self._connector, raise_for_status=raise_for_status, response_class=own_response_class
                )
            if own_response_class is None:
                return ClientSession(raise_for_status=raise_for_status)
            return ClientSession(raise_for_status=raise_for_status, response_class=own_response_class)

        async with self._session_lock:
            number_of_times_this_session_has_been_used = next(self._session_usage_counter)
            if self._session is None:
                _logger.info("creating new session")
                self._session = _create_new_session()
            elif self._session.closed:
                _logger.info("aiohttp session was closed, re-opening it")
                self._session = _create_new_session()
            elif number_of_times_this_session_has_been_used >= self._session_usage_threshold:
                # there is an issue with aiohttp:
                # after _many_ requests the aiohttp session will start leaking memory:
                # https://github.com/aio-libs/aiohttp/issues/4833
                # our workaround is to re-create the session once in a while
                _logger.info(
                    "re-creating session of %s after %i requests to avoid memory leaks",
                    self.__class__.__name__,
                    self._session_usage_threshold,
                )
                for seconds_left in range(45, 0, -5):
                    # why the waiting? because we want to make sure the session is not in use anywhere anymore
                    _logger.info("Closing session of %s in %i seconds...", self.__class__.__name__, seconds_left)
                    await asyncio.sleep(5)
                _logger.warning("Closing session of %s _NOW_ (recreating afterwards)", self.__class__.__name__)
                await self._session.close()
                old_session = self._session
                _logger.info("Creating new session of %s after closing the old one", self.__class__.__name__)
                self._session = _create_new_session()
                del old_session
                self._session_usage_counter = count()
            else:
                _logger.debug("reusing aiohttp session (%i)", number_of_times_this_session_has_been_used)
        return self._session

    async def close_session(self):
        """
        closes the client session
        """
        async with self._session_lock:
            if self._session is not None and not self._session.closed:
                _logger.info("Closing aiohttp session")
                await self._session.close()
                self._session = None


class _ValidateTokenMixin:  # pylint:disable=too-few-public-methods
    """
    Mixin for classes which need to validate tokens
    """

    def __init__(self):
        self._session_lock = asyncio.Lock()

    def _token_is_valid(self, token) -> bool:
        """
        returns true iff the token expiration date is far enough in the future. By "enough" I mean:
        more than 1 minute (because the clients' request using the token shouldn't take longer than that)
        """
        try:
            decoded_token = jwt.decode(token, algorithms=["HS256"], options={"verify_signature": False})
            expiration_timestamp = decoded_token.get("exp")
            expiration_datetime = datetime.fromtimestamp(expiration_timestamp)
            _logger.debug("Token is valid until %s", expiration_datetime.isoformat())
            current_datetime = datetime.utcnow()
            token_is_valid_one_minute_into_the_future = expiration_datetime > current_datetime + timedelta(minutes=1)
            return token_is_valid_one_minute_into_the_future
        except jwt.ExpiredSignatureError:
            _logger.info("The token is expired", exc_info=True)
            return False
        except jwt.InvalidTokenError:
            _logger.info("The token is invalid", exc_info=True)
            return False


class _OAuthHttpClient(_ValidateTokenMixin, ABC):  # pylint:disable=too-few-public-methods
    """
    An abstract oauth based HTTP client
    """

    def __init__(self, base_url: URL, oauth_client_id: str, oauth_client_secret: str, oauth_token_url: URL | str):
        """
        instantiate by providing the basic information which is required to connect to the service.
        :param base_url: e.g. "https://transformerbee.utilibee.io/"
        :param oauth_client_id: e.g. "my-client-id"
        :param oauth_client_secret: e.g. "my-client-secret"
        :param oauth_token_url: e.g."https://transformerbee.utilibee.io/oauth/token"
        """
        super().__init__()
        if not isinstance(base_url, URL):
            # For the cases where type-check is not enough because we tend to ignore type-check warnings
            raise ValueError(f"Pass the base URL as yarl URL or bad things will happen. Got {base_url.__class__}")
        self._base_url = base_url
        self._oauth2client = OAuth2Client(
            client_id=oauth_client_id,
            client_secret=oauth_client_secret,
            access_token_url=str(oauth_token_url),
            logger=_logger,
        )
        self._token: Optional[str] = None  # the jwt token if we did an authenticated request before
        self._token_write_lock = asyncio.Lock()

    async def _get_new_token(self) -> str:
        """get a new JWT token from the oauth server"""
        _logger.debug("Retrieving a new token")
        token, _ = await self._oauth2client.get_access_token(
            "code",
            grant_type="client_credentials",
            audience="https://transformer.bee",
            # without the audience, you'll get an HTTP 403
        )
        return token

    async def _get_oauth_token(self) -> str:
        """
        encapsulates the oauth part, such that it's e.g. easily mockable in tests
        :returns the oauth token
        """
        async with self._token_write_lock:
            if self._token is None:
                _logger.info("Initially retrieving a new token")
                self._token = await self._get_new_token()
            elif not self._token_is_valid(self._token):
                _logger.info("Token is not valid anymore, retrieving a new token")
                self._token = await self._get_new_token()
            else:
                _logger.debug("Token is still valid, reusing it")
        return self._token


class _TransformerBeeClientBaseMixin:  # pylint:disable=too-few-public-methods
    """
    the stateless base functionality of both the authenticated and unauthenticated client
    """

    async def _send_request(self, session: ClientSession, request_body: BaseModel, url: URL) -> ClientResponse:
        if hasattr(self, "_get_oauth_token"):
            token = await self._get_oauth_token()
            headers = {"Authorization": f"Bearer {token}"}
            response = await session.post(json=request_body.model_dump(by_alias=True), url=url, headers=headers)
        else:
            response = await session.post(json=request_body.model_dump(by_alias=True), url=url)
        return response

    async def _convert_to_bo4e(
        self, session: ClientSession, base_url: URL, edifact: str, edifact_format_version: EdifactFormatVersion
    ) -> list[Marktnachricht]:
        """
        converts the given edifact to a list of marktnachrichten
        """
        if not edifact:
            raise ValueError("edifact must not be empty")
        edi_to_bo4e_url = base_url / "v1" / "transformer" / "EdiToBo4E"
        request = EdifactToBo4eRequest(edifact=edifact, format_version=edifact_format_version)  # type:ignore[call-arg]
        response = await self._send_request(session, request, edi_to_bo4e_url)
        response_json = await response.json()
        response_model = EdifactToBo4eResponse.model_validate(response_json)
        result = [Marktnachricht.model_validate(x) for x in json.loads(response_model.bo4e_json.replace("\\n", "\n"))]
        return result

    async def _convert_to_edifact(
        self, session: ClientSession, base_url: URL, boney_comb: BOneyComb, edifact_format_version: EdifactFormatVersion
    ) -> str:
        """
        converts the given boneycomb to an edifact
        """
        bo4e_to_edi_url = base_url / "v1" / "transformer" / "Bo4ETransactionToEdi"
        request = Bo4eTransactionToEdifactRequest(  # type:ignore[call-arg]
            bo4e_json_string=boney_comb.model_dump_json(), format_version=edifact_format_version
        )
        response = await self._send_request(session, request, bo4e_to_edi_url)
        response_json = await response.json()
        response_model = Bo4eTransactionToEdifactResponse.model_validate(response_json)
        return response_model.edifact


class UnauthenticatedTransformerBeeClient(
    TransformerBeeClient, _ClientSessionMixin, _TransformerBeeClientBaseMixin
):  # pylint:disable=too-few-public-methods
    """
    A client for the transformer.bee API (without authentication)
    """

    def __init__(self, base_url: URL | str):
        """
        instantiate by providing the base URL of the transformer.bee service
        :param base_url: e.g. https://transformerbee.utilibee.io/ or https://localhost:5021
        """
        _ClientSessionMixin.__init__(self)
        TransformerBeeClient.__init__(self)
        self._base_url = URL(base_url)

    async def convert_to_bo4e(self, edifact: str, edifact_format_version: EdifactFormatVersion) -> list[Marktnachricht]:
        """
        converts the given edifact to a list of marktnachrichten
        """
        session = await self._get_session()
        result = await self._convert_to_bo4e(session, self._base_url, edifact, edifact_format_version)
        return result

    async def convert_to_edifact(self, boney_comb: BOneyComb, edifact_format_version: EdifactFormatVersion) -> str:
        """
        converts the given boneycomb to an edifact
        """
        session = await self._get_session()
        result = await self._convert_to_edifact(session, self._base_url, boney_comb, edifact_format_version)
        return result


_hochfrequenz_token_url = URL("https://hochfrequenz.eu.auth0.com/oauth/token")


class AuthenticatedTransformerBeeClient(
    _OAuthHttpClient, _ClientSessionMixin, _TransformerBeeClientBaseMixin
):  # pylint:disable=too-few-public-methods
    """
    A client for the transformer.bee API (with OAuth2 authentication)
    """

    def __init__(self, base_url: URL | str, oauth_client_id: str, oauth_client_secret: str, **kwargs):
        if isinstance(base_url, str):
            _base_url = URL(base_url)
        else:
            _base_url = base_url
        super().__init__(
            base_url=_base_url,
            oauth_client_id=oauth_client_id,
            oauth_client_secret=oauth_client_secret,
            oauth_token_url=_hochfrequenz_token_url,
            **kwargs,
        )
        _ClientSessionMixin.__init__(self)

    async def convert_to_bo4e(self, edifact: str, edifact_format_version: EdifactFormatVersion) -> list[Marktnachricht]:
        """
        converts the given edifact to a list of marktnachrichten
        """
        session = await self._get_session()
        result = await self._convert_to_bo4e(session, self._base_url, edifact, edifact_format_version)
        return result

    async def convert_to_edifact(self, boney_comb: BOneyComb, edifact_format_version: EdifactFormatVersion) -> str:
        """
        converts the given boneycomb to an edifact
        """
        session = await self._get_session()
        result = await self._convert_to_edifact(session, self._base_url, boney_comb, edifact_format_version)
        return result
