import asyncio.locks
import modal._blob_utils
import modal.client
import modal.object
import modal_proto.api_pb2
import pathlib
import typing
import typing_extensions

class _Volume(modal.object._StatefulObject):
    _lock: asyncio.locks.Lock

    def _initialize_from_empty(self):
        ...

    @staticmethod
    def new() -> _Volume:
        ...

    @staticmethod
    def persisted(label: str, namespace=1, environment_name: typing.Union[str, None] = None) -> _Volume:
        ...

    async def _do_reload(self, lock=True):
        ...

    async def commit(self):
        ...

    async def reload(self):
        ...

    def iterdir(self, path: str) -> typing.AsyncIterator[modal_proto.api_pb2.VolumeListFilesEntry]:
        ...

    async def listdir(self, path: str) -> typing.List[modal_proto.api_pb2.VolumeListFilesEntry]:
        ...

    def read_file(self, path: typing.Union[str, bytes]) -> typing.AsyncIterator[bytes]:
        ...

    async def read_file_into_fileobj(self, path: typing.Union[str, bytes], fileobj: typing.IO[bytes], progress: bool = False) -> int:
        ...

    async def remove_file(self, path: typing.Union[str, bytes], recursive: bool = False) -> None:
        ...

    async def copy_files(self, src_paths: typing.Sequence[typing.Union[str, bytes]], dst_path: typing.Union[str, bytes]) -> None:
        ...

    async def batch_upload(self, force: bool = False) -> _VolumeUploadContextManager:
        ...


class _VolumeUploadContextManager:
    _volume_id: str
    _client: modal.client._Client
    _force: bool
    _upload_generators: typing.List[typing.Generator[typing.Callable[[], modal._blob_utils.FileUploadSpec], None, None]]

    def __init__(self, volume_id: str, client: modal.client._Client, force: bool = False):
        ...

    async def __aenter__(self):
        ...

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        ...

    def put_file(self, local_file: typing.Union[pathlib.Path, str, typing.BinaryIO], remote_path: typing.Union[pathlib.PurePosixPath, str], mode: typing.Union[int, None] = None):
        ...

    def put_directory(self, local_path: typing.Union[pathlib.Path, str], remote_path: typing.Union[pathlib.PurePosixPath, str], recursive: bool = True):
        ...

    async def _upload_file(self, file_spec: modal._blob_utils.FileUploadSpec) -> modal_proto.api_pb2.MountFile:
        ...


class Volume(modal.object.StatefulObject):
    _lock: asyncio.locks.Lock

    def __init__(self, *args, **kwargs):
        ...

    def _initialize_from_empty(self):
        ...

    @staticmethod
    def new() -> Volume:
        ...

    @staticmethod
    def persisted(label: str, namespace=1, environment_name: typing.Union[str, None] = None) -> Volume:
        ...

    class ___do_reload_spec(typing_extensions.Protocol):
        def __call__(self, lock=True):
            ...

        async def aio(self, *args, **kwargs):
            ...

    _do_reload: ___do_reload_spec

    class __commit_spec(typing_extensions.Protocol):
        def __call__(self):
            ...

        async def aio(self, *args, **kwargs):
            ...

    commit: __commit_spec

    class __reload_spec(typing_extensions.Protocol):
        def __call__(self):
            ...

        async def aio(self, *args, **kwargs):
            ...

    reload: __reload_spec

    class __iterdir_spec(typing_extensions.Protocol):
        def __call__(self, path: str) -> typing.Iterator[modal_proto.api_pb2.VolumeListFilesEntry]:
            ...

        def aio(self, path: str) -> typing.AsyncIterator[modal_proto.api_pb2.VolumeListFilesEntry]:
            ...

    iterdir: __iterdir_spec

    class __listdir_spec(typing_extensions.Protocol):
        def __call__(self, path: str) -> typing.List[modal_proto.api_pb2.VolumeListFilesEntry]:
            ...

        async def aio(self, *args, **kwargs) -> typing.List[modal_proto.api_pb2.VolumeListFilesEntry]:
            ...

    listdir: __listdir_spec

    class __read_file_spec(typing_extensions.Protocol):
        def __call__(self, path: typing.Union[str, bytes]) -> typing.Iterator[bytes]:
            ...

        def aio(self, path: typing.Union[str, bytes]) -> typing.AsyncIterator[bytes]:
            ...

    read_file: __read_file_spec

    class __read_file_into_fileobj_spec(typing_extensions.Protocol):
        def __call__(self, path: typing.Union[str, bytes], fileobj: typing.IO[bytes], progress: bool = False) -> int:
            ...

        async def aio(self, *args, **kwargs) -> int:
            ...

    read_file_into_fileobj: __read_file_into_fileobj_spec

    class __remove_file_spec(typing_extensions.Protocol):
        def __call__(self, path: typing.Union[str, bytes], recursive: bool = False) -> None:
            ...

        async def aio(self, *args, **kwargs) -> None:
            ...

    remove_file: __remove_file_spec

    class __copy_files_spec(typing_extensions.Protocol):
        def __call__(self, src_paths: typing.Sequence[typing.Union[str, bytes]], dst_path: typing.Union[str, bytes]) -> None:
            ...

        async def aio(self, *args, **kwargs) -> None:
            ...

    copy_files: __copy_files_spec

    class __batch_upload_spec(typing_extensions.Protocol):
        def __call__(self, force: bool = False) -> VolumeUploadContextManager:
            ...

        async def aio(self, *args, **kwargs) -> VolumeUploadContextManager:
            ...

    batch_upload: __batch_upload_spec


class VolumeUploadContextManager:
    _volume_id: str
    _client: modal.client.Client
    _force: bool
    _upload_generators: typing.List[typing.Generator[typing.Callable[[], modal._blob_utils.FileUploadSpec], None, None]]

    def __init__(self, volume_id: str, client: modal.client.Client, force: bool = False):
        ...

    def __enter__(self):
        ...

    async def __aenter__(self, *args, **kwargs):
        ...

    def __exit__(self, exc_type, exc_val, exc_tb):
        ...

    async def __aexit__(self, *args, **kwargs):
        ...

    def put_file(self, local_file: typing.Union[pathlib.Path, str, typing.BinaryIO], remote_path: typing.Union[pathlib.PurePosixPath, str], mode: typing.Union[int, None] = None):
        ...

    def put_directory(self, local_path: typing.Union[pathlib.Path, str], remote_path: typing.Union[pathlib.PurePosixPath, str], recursive: bool = True):
        ...

    class ___upload_file_spec(typing_extensions.Protocol):
        def __call__(self, file_spec: modal._blob_utils.FileUploadSpec) -> modal_proto.api_pb2.MountFile:
            ...

        async def aio(self, *args, **kwargs) -> modal_proto.api_pb2.MountFile:
            ...

    _upload_file: ___upload_file_spec
