import datetime
from typing import Optional

import aioboto3
import aiobotocore.config
import aiobotocore.session
import typing_extensions
from typing_extensions import Protocol


DEFAULT_SESSION_EXPIRATION_THRESHOLD = datetime.timedelta(minutes=3)


@typing_extensions.runtime_checkable
class TokenProvider(Protocol):
    """Defines the interface of the token provider.

    Token provider is used to obtain access token that is exchanged for the session
    token.
    """

    async def __call__(self) -> str:
        """Returns fresh access token for the access to H2O Drive server."""


class StaticTokenProvider:
    """Implements TokenProvider interface and always returns static token passed."""

    def __init__(self, token: str) -> None:
        self._token = token

    async def __call__(self) -> str:
        return self._token


@typing_extensions.runtime_checkable
class SessionProvider(Protocol):
    """Defines the interface of the session provider.

    Session provider is used by the core components to get access to the H2O Drive
    server.
    """

    async def __call__(self) -> aioboto3.Session:
        pass


class StaticSessionProvider:
    """Implements SessionProvider interface and always returns the session passed
    to the constructor.
    """

    def __init__(self, session: aioboto3.Session) -> None:
        self._session = session

    async def __call__(self) -> aioboto3.Session:
        return self._session


class RefreshingWebIdentitySessionProvider:
    """Uses token provider passed to the constructor to obtain fresh session credentials
    when needed.
    """

    def __init__(
        self,
        token_provider: TokenProvider,
        sts_endpoint_url: str,
        *,
        session_ttl_seconds: int = 3600,
        expiration_threshold: datetime.timedelta = DEFAULT_SESSION_EXPIRATION_THRESHOLD,
        read_timeout_seconds: int = 60,
    ) -> None:
        self._token_provider = token_provider
        self._sts_endpoint_url = sts_endpoint_url
        self._expiration_threshold = expiration_threshold
        self._session_ttl_seconds = session_ttl_seconds
        self._read_timeout_seconds = read_timeout_seconds

        self._session: Optional[aioboto3.Session] = None
        self._credentials_expiration: Optional[datetime.datetime] = None

    async def __call__(self) -> aioboto3.Session:
        if self.refresh_required():
            await self._do_refresh()
        return self._session

    def refresh_required(self) -> bool:
        """Returns True when there's no access token set or the current one requires
        refresh.
        """
        if self._session is None or self._credentials_expiration is None:
            return True

        now = datetime.datetime.now(datetime.timezone.utc)
        return self._credentials_expiration <= (now + self._expiration_threshold)

    async def _do_refresh(self) -> aioboto3.Session:
        credentials = await self._get_credentials()
        self._credentials_expiration = credentials.get("Expiration")
        self._session = aioboto3.Session(
            aws_access_key_id=credentials.get("AccessKeyId"),
            aws_secret_access_key=credentials.get("SecretAccessKey"),
            aws_session_token=credentials.get("SessionToken"),
        )

    async def _get_credentials(self):
        boto_session = aiobotocore.session.get_session()
        async with boto_session.create_client(
            "sts",
            endpoint_url=self._sts_endpoint_url,
            config=aiobotocore.config.AioConfig(
                read_timeout=self._read_timeout_seconds
            ),
        ) as sts:
            assume_role = await sts.assume_role_with_web_identity(
                # RoleArn is an arbitrary string from 20 to 2048 characters long.
                RoleArn="h2odriveh2odriveh2odrive",
                RoleSessionName="h2odrive",
                WebIdentityToken=await self._token_provider(),
                DurationSeconds=self._session_ttl_seconds,
            )
        return assume_role.get("Credentials", dict())
