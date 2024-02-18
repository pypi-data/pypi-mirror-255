import os
from typing import Optional
from typing import Union

import h2o_authn.discovery
import h2o_discovery
from h2o_drive import auth
from h2o_drive import core

CLOUD_DISCOVERY_SERVICE_NAME = "drive"

Workspace = core.Workspace
MY_BUCKET = core.MY_BUCKET


async def MyHome(
    token: Union[auth.TokenProvider, str],
    *,
    endpoint_url: Optional[str] = None,
    sts_endpoint_url: Optional[str] = None,
    environment: Optional[str] = None,
    config_path: Optional[str] = None,
    session_ttl_seconds: int = 3600,
    read_timeout_seconds: int = 60,
) -> core.PrefixClient:
    """Returns new client connected to the user's personal bucket and the HOME
    workspace.

    When the personal bucket does not exist, it's created.

    When not specified, certain parameters are determined automatically by
    either environment variables or via the H2O Cloud Discovery Client.  While
    the Cloud Discovery Client may apply multiple strategies, the following
    rules generally apply:
    - environment, if specified, will be used instead of searching for that
        value in config_path.
    - The H2O Cloud Discovery Client will fall back to common H2O environment
        variables and configuration paths, but will only supersede values
        specified here if a more specific environment variable,
        H2O_CLOUD_DISCOVERY, is found. This value is often set in H2O cloud
        applications.

    Args:
        token: Token or token provider to use. If not specified, it's determined
            automatically.
        endpoint_url: URL of the Drive endpoint. If not specified, it's
            determined automatically.
        sts_endpoint_url: URL of the STS endpoint. If not specified, it's
            determined automatically.
        environment: URL of the H2O.ai cloud environment. Used only when
            determining a missing token or URL.
        config_path: Path to the H2O.ai CLI config. Used only when determining a
            missing token or URL.
        session_ttl_seconds: The duration, in seconds, of the role session.
        read_timeout_seconds: The time in seconds until a timeout exception is
            thrown when reading from Drive.

    Returns:
        A Drive client connected to the user's personal bucket and the HOME
            workspace.
    """

    my_bucket = await MyBucket(
        token=token,
        endpoint_url=endpoint_url,
        sts_endpoint_url=sts_endpoint_url,
        environment=environment,
        config_path=config_path,
        session_ttl_seconds=session_ttl_seconds,
        read_timeout_seconds=read_timeout_seconds,
    )
    return my_bucket.home()


async def MyBucket(
    token: Union[auth.TokenProvider, str],
    *,
    endpoint_url: Optional[str] = None,
    sts_endpoint_url: Optional[str] = None,
    environment: Optional[str] = None,
    config_path: Optional[str] = None,
    session_ttl_seconds: int = 3600,
    read_timeout_seconds: int = 60,
) -> core.Bucket:
    """Returns new client connected to the user's personal bucket.

    When the personal bucket does not exist, it's created.

    When not specified, certain parameters are determined automatically by
    either environment variables or via the H2O Cloud Discovery Client.  While
    the Cloud Discovery Client may apply multiple strategies, the following
    rules generally apply:
    - environment, if specified, will be used instead of searching for that
        value in config_path.
    - The H2O Cloud Discovery Client will fall back to common H2O environment
        variables and configuration paths, but will only supersede values
        specified here if a more specific environment variable,
        H2O_CLOUD_DISCOVERY, is found. This value is often set in H2O cloud
        applications.

    Args:
        token: Token or token provider to use. If not specified, it's determined
            automatically.
        endpoint_url: URL of the Drive endpoint. If not specified, it's
            determined automatically.
        sts_endpoint_url: URL of the STS endpoint. If not specified, it's
            determined automatically.
        environment: URL of the H2O.ai cloud environment. Used only when
            determining a missing token or URL.
        config_path: Path to the H2O.ai CLI config. Used only when determining a
            missing token or URL.
        session_ttl_seconds: The duration, in seconds, of the role session.
        read_timeout_seconds: The time in seconds until a timeout exception is
            thrown when reading from Drive.

    Returns:
        A Drive client connected to the user's personal bucket.
    """
    client = await Drive(
        token=token,
        endpoint_url=endpoint_url,
        sts_endpoint_url=sts_endpoint_url,
        environment=environment,
        config_path=config_path,
        session_ttl_seconds=session_ttl_seconds,
        read_timeout_seconds=read_timeout_seconds,
    )
    bucket = client.my_bucket()
    await bucket.ensure_created()
    return bucket


async def Drive(
    token: Union[auth.TokenProvider, str, None] = None,
    *,
    endpoint_url: Optional[str] = None,
    sts_endpoint_url: Optional[str] = None,
    environment: Optional[str] = None,
    config_path: Optional[str] = None,
    session_ttl_seconds: int = 3600,
    read_timeout_seconds: int = 60,
) -> core.Client:
    """Returns a new instance of the Drive client.

    When not specified, certain parameters are determined automatically by
    either environment variables or via the H2O Cloud Discovery Client.  While
    the Cloud Discovery Client may apply multiple strategies, the following
    rules generally apply:
    - environment, if specified, will be used instead of searching for that
        value in config_path.
    - The H2O Cloud Discovery Client will fall back to common H2O environment
        variables and configuration paths, but will only supersede values
        specified here if a more specific environment variable,
        H2O_CLOUD_DISCOVERY, is found. This value is often set in H2O cloud
        applications.

    Args:
        token: Token or token provider to use. If not specified, it's determined
            automatically.
        endpoint_url: URL of the Drive endpoint. If not specified, it's
            determined automatically.
        sts_endpoint_url: URL of the STS endpoint. If not specified, it's
            determined automatically.
        environment: URL of the H2O.ai cloud environment. Used only when
            determining a missing token or URL.
        config_path: Path to the H2O.ai CLI config. Used only when determining a
            missing token or URL.
        session_ttl_seconds: The duration, in seconds, of the role session.
        read_timeout_seconds: The time in seconds until a timeout exception is
            thrown when reading from Drive.

    Returns:
        A Drive client.
    """
    if token is None or endpoint_url is None:
        discovery = h2o_discovery.discover(
            environment=environment, config_path=config_path
        )

    if token is None:
        token_provider = discover_token_provider(discovery)
        await token_provider()
    elif isinstance(token, auth.TokenProvider):
        token_provider = token
        await token_provider()
    else:
        token_provider = auth.StaticTokenProvider(token)

    if endpoint_url is None:
        endpoint_url = os.getenv("H2O_DRIVE_ENDPOINT")
    if endpoint_url is None:
        service = discovery.services.get(CLOUD_DISCOVERY_SERVICE_NAME)
        if service is not None:
            endpoint_url = service.uri
    if endpoint_url is None:
        raise LookupError(
            "Failed to automatically determine the endpoint URL. "
            "Drive entry missing from Cloud Discovery service."
        )

    if sts_endpoint_url is None:
        sts_endpoint_url = os.getenv("H2O_DRIVE_STS_ENDPOINT")
    if sts_endpoint_url is None:
        sts_endpoint_url = f'{endpoint_url.rstrip("/")}/sts/'

    return await connect(
        token_provider=token_provider,
        sts_endpoint_url=sts_endpoint_url,
        endpoint_url=endpoint_url,
        session_ttl_seconds=session_ttl_seconds,
        read_timeout_seconds=read_timeout_seconds,
    )


async def connect(
    token_provider: auth.TokenProvider,
    *,
    endpoint_url: str,
    sts_endpoint_url: str,
    session_ttl_seconds: int = 3600,
    read_timeout_seconds: int = 60,
) -> core.Client:
    """Returns a new instance of the Client with session created against the
    token returned by the token provider.
    """

    session_provider = auth.RefreshingWebIdentitySessionProvider(
        token_provider=token_provider,
        sts_endpoint_url=sts_endpoint_url,
        session_ttl_seconds=session_ttl_seconds,
        read_timeout_seconds=read_timeout_seconds,
    )
    return core.Client(session=session_provider, endpoint_url=endpoint_url)


def discover_token_provider(discovery: h2o_discovery.Discovery) -> auth.TokenProvider:
    """Returns a new instance of an async TokenProvider configured from the
    given Discovery object.
    """
    try:
        return h2o_authn.discovery.create_async(discovery)
    except KeyError:
        raise LookupError(
            "Failed to automatically determine the token provider from "
            "information available in the environment."
        )
