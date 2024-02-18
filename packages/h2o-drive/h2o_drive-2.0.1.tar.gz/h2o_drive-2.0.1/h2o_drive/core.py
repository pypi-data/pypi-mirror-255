import contextlib
import datetime
import enum
import os
import pathlib
from typing import List
from typing import NamedTuple
from typing import Optional

import boto3.s3.transfer
import botocore.exceptions

from h2o_drive import auth

MY_BUCKET = "_my"
_HOME_PREFIX = "home/"
_DEFAULT_PRESIGNED_URL_TTL_SECONDS = 24 * 60 * 60  # 1 day.


class Workspace(enum.Enum):
    """Defines sopported predefined workspaces."""

    HOME = enum.auto()
    APP = enum.auto()
    APP_VERSION = enum.auto()
    APP_INSTANCE = enum.auto()


class PresignedURL(str):
    """Defines presigned URL as it's own type so it can be extended for integration with
    other service clients (e.g. H2O-3)
    """


class ObjectSummary(NamedTuple):
    """Represents basic information about object."""

    key: str
    size: int
    last_modified: datetime.datetime


class PrefixClient:
    """Implements standard object operations but all keys are automatically prefixed
    with configured prefix.

    Simulates behavior of the bucket within the bucket.
    """

    def __init__(self, *, bucket: "Bucket", prefix: str) -> None:
        self._bucket = bucket
        self._prefix = prefix
        self._prefix_length = len(prefix)

    async def upload_file(self, file_name: os.PathLike, object_name: str):
        """Uploads local file to the H2O Drive as object."""
        await self._bucket.upload_file(file_name, self._key_with_prefix(object_name))

    async def download_file(self, object_name: str, file_name: os.PathLike):
        """Download H2O Drive object to local file."""
        await self._bucket.download_file(self._key_with_prefix(object_name), file_name)

    async def list_objects(self, prefix: Optional[str] = None) -> List[ObjectSummary]:
        """Returns list of available objects.

        Only the objects with the prefix associated with the instance are returned and
        the prefix is stripped. Objects can be additionally filtered by further prefix.
        """
        filter_prefix = self._prefix
        if prefix is not None:
            filter_prefix = self._key_with_prefix(prefix)

        objects = await self._bucket.list_objects(prefix=filter_prefix)

        result: List[ObjectSummary] = []
        for o in objects:
            obj_name = o.key
            if obj_name.startswith(self._prefix):
                obj_name = obj_name[self._prefix_length :]
            result.append(
                ObjectSummary(key=obj_name, size=o.size, last_modified=o.last_modified)
            )

        return result

    async def delete_object(self, object_name: str):
        """Deletes H2O Drive object."""
        await self._bucket.delete_object(self._key_with_prefix(object_name))

    async def generate_presigned_url(
        self, object_name: str, *, ttl_seconds: int = _DEFAULT_PRESIGNED_URL_TTL_SECONDS
    ) -> PresignedURL:
        """Generates pre-signed URL for the H2O Drive object.

        Generated URL might not be accessible externally.
        """
        return await self._bucket.generate_presigned_url(
            object_name=self._key_with_prefix(object_name), ttl_seconds=ttl_seconds
        )

    def _key_with_prefix(self, key: str) -> str:
        return str(pathlib.Path(self._prefix) / key)


class Bucket:
    def __init__(
        self, name: str, *, session: auth.SessionProvider, endpoint_url: str
    ) -> None:
        self._name = name
        self._session = session
        self._endpoint_url = endpoint_url

    async def upload_file(self, file_name: os.PathLike, object_name: str):
        """Uploads local file to the H2O Drive as object in the bucket."""
        async with self._s3_client() as s3:
            await s3.upload_file(
                file_name,
                self._name,
                object_name,
                Config=boto3.s3.transfer.TransferConfig(max_io_queue=5),
            )

    async def download_file(self, object_name: str, file_name: os.PathLike):
        """Download H2O Drive object in the bucket to local file."""
        async with self._s3_client() as s3:
            await s3.download_file(self._name, object_name, file_name)

    async def list_objects(self, prefix: Optional[str] = None) -> List[ObjectSummary]:
        """Returns list of objects available in the bucket.

        Files can be filtered by the prefix.
        """
        async with self._s3_resource() as s3:
            bucket = await s3.Bucket(self._name)
            if prefix is not None:
                objects = bucket.objects.filter(Prefix=prefix)
            else:
                objects = bucket.objects.all()
            result: List[ObjectSummary] = []
            async for o in objects:
                result.append(
                    ObjectSummary(
                        key=o.key,
                        size=await o.size,
                        last_modified=await o.last_modified,
                    )
                )
            return result

    async def delete_object(self, object_name: str):
        """Deletes H2O Drive object in the bucket."""
        async with self._s3_resource() as s3:
            bucket = await s3.Bucket(self._name)
            obj = await bucket.Object(object_name)
            await obj.delete()

    async def generate_presigned_url(
        self, object_name: str, *, ttl_seconds: int = _DEFAULT_PRESIGNED_URL_TTL_SECONDS
    ) -> PresignedURL:
        """Generates pre-signed URL for the H2O Drive object in the bucket.

        Generated URL might not be accessible externally.
        """

        async with self._s3_client() as s3:
            url_str = await s3.generate_presigned_url(
                ClientMethod="get_object",
                Params={"Bucket": self._name, "Key": object_name},
                ExpiresIn=ttl_seconds,
            )
            return PresignedURL(url_str)

    async def create(self) -> "Bucket":
        """Creates the bucket."""
        async with self._s3_resource() as s3:
            bucket = await s3.Bucket(self._name)
            await bucket.create()
        return self

    async def ensure_created(self) -> "Bucket":
        """Creates the bucket if it does not exist."""
        try:
            await self.create()
        except botocore.exceptions.ClientError as error:
            if error.response["Error"]["Code"] != "BucketAlreadyExists":
                raise

        return self

    def with_prefix(self, prefix: str) -> PrefixClient:
        """Returns a new instance of the Drive client operating within the bucket but
        with all object operations prefixed with the prefix.
        """
        return PrefixClient(bucket=self, prefix=prefix)

    def workspace(self, workspace: Workspace) -> PrefixClient:
        """Returns new instance og Drive client operating withing the bucket but
        with all object operations prefixed with prefix pre-defined by workspace.
        """
        if workspace == Workspace.HOME:
            prefix = _HOME_PREFIX
        elif workspace == Workspace.APP:
            prefix = _get_app_workspace_prefix()
        elif workspace == Workspace.APP_VERSION:
            prefix = _get_app_version_workspace_prefix()
        elif workspace == Workspace.APP_INSTANCE:
            prefix = _get_app_instance_workspace_prefix()
        else:
            raise ValueError(f"Unsupported workspace: {workspace}.")

        return self.with_prefix(prefix=prefix)

    def home(self) -> PrefixClient:
        """Returns new instance og Drive client operating withing the bucket but
        with all object operations prefixed with prefix pre-defined by HOME workspace.
        """
        return self.workspace(workspace=Workspace.HOME)

    @contextlib.asynccontextmanager
    async def _s3_client(self):
        session = await self._session()
        async with session.client(
            "s3",
            endpoint_url=self._endpoint_url,
            config=botocore.client.Config(signature_version="s3v4"),
        ) as s3:
            yield s3

    @contextlib.asynccontextmanager
    async def _s3_resource(self):
        session = await self._session()
        async with session.resource(
            "s3",
            endpoint_url=self._endpoint_url,
            config=botocore.client.Config(signature_version="s3v4"),
        ) as s3:
            yield s3


class Client:
    def __init__(self, session: auth.SessionProvider, endpoint_url: str) -> None:
        self._session = session
        self._endpoint_url = endpoint_url

    def bucket(self, name) -> Bucket:
        """Returns a new instance of the Bucket client."""
        return Bucket(name=name, session=self._session, endpoint_url=self._endpoint_url)

    def my_bucket(self) -> Bucket:
        """Returns a new instance of the Bucket client for the user's personal
        bucket."""
        return Bucket(
            name=MY_BUCKET, session=self._session, endpoint_url=self._endpoint_url
        )


def _get_app_workspace_prefix():
    app = _get_app_name()
    return f"{app}/workspace/"


def _get_app_version_workspace_prefix():
    app_version_prefix = _get_app_version_prefix()
    return f"{app_version_prefix}/workspace/"


def _get_app_version_prefix():
    app, version, app_id = _get_app_name(), _get_app_version(), _get_app_id()
    return f"{app}/{app_id}-{version}"


def _get_app_instance_workspace_prefix():
    app_version_prefix = _get_app_version_prefix()
    app_instance_id = _get_app_instance_id()
    return f"{app_version_prefix}/{app_instance_id}/workspace/"


def _get_app_name() -> str:
    app = os.getenv("H2O_CLOUD_APP_NAME")
    if not app:
        raise LookupError(
            "Unable to determine app name. "
            "H2O_CLOUD_APP_NAME environment variable not set."
        )
    return app


def _get_app_version() -> str:
    version = os.getenv("H2O_CLOUD_APP_VERSION")
    if not version:
        raise LookupError(
            "Unable to determine app version. "
            "H2O_CLOUD_APP_VERSION environment variable not set."
        )
    return version


def _get_app_id() -> str:
    app_id = os.getenv("H2O_CLOUD_APP_ID")
    if not app_id:
        raise LookupError(
            "Unable to determine app ID. "
            "H2O_CLOUD_APP_ID environment variable not set."
        )
    return app_id


def _get_app_instance_id() -> str:
    instance_id = os.getenv("H2O_CLOUD_INSTANCE_ID")
    if not instance_id:
        raise LookupError(
            "Unable to determine app instance ID. "
            "H2O_CLOUD_INSTANCE_ID environment variable not set."
        )
    return instance_id
