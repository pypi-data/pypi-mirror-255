import google.protobuf.message
import modal.client
import modal.gpu
import modal.image
import modal.mount
import modal.network_file_system
import modal.object
import modal.s3mount
import modal.secret
import modal.volume
import modal_proto.api_pb2
import os
import typing
import typing_extensions

class _LogsReader:
    def __init__(self, file_descriptor: int, sandbox_id: str, client: modal.client._Client) -> None:
        ...

    async def read(self) -> str:
        ...


class LogsReader:
    def __init__(self, file_descriptor: int, sandbox_id: str, client: modal.client.Client) -> None:
        ...

    class __read_spec(typing_extensions.Protocol):
        def __call__(self) -> str:
            ...

        async def aio(self, *args, **kwargs) -> str:
            ...

    read: __read_spec


class _Sandbox(modal.object._Object):
    _result: typing.Union[modal_proto.api_pb2.GenericResult, None]
    _stdout: _LogsReader
    _stderr: _LogsReader

    @staticmethod
    def _new(entrypoint_args: typing.Sequence[str], image: modal.image._Image, mounts: typing.Sequence[modal.mount._Mount], secrets: typing.Sequence[modal.secret._Secret], timeout: typing.Union[int, None] = None, workdir: typing.Union[str, None] = None, gpu: typing.Union[None, bool, str, modal.gpu._GPUConfig] = None, cloud: typing.Union[str, None] = None, cpu: typing.Union[float, None] = None, memory: typing.Union[int, None] = None, network_file_systems: typing.Dict[typing.Union[str, os.PathLike], modal.network_file_system._NetworkFileSystem] = {}, block_network: bool = False, volumes: typing.Dict[typing.Union[str, os.PathLike], typing.Union[modal.volume._Volume, modal.s3mount._S3Mount]] = {}) -> _Sandbox:
        ...

    def _hydrate_metadata(self, handle_metadata: typing.Union[google.protobuf.message.Message, None]):
        ...

    async def wait(self, raise_on_termination: bool = True):
        ...

    async def terminate(self):
        ...

    async def poll(self) -> typing.Union[int, None]:
        ...

    @property
    def stdout(self) -> _LogsReader:
        ...

    @property
    def stderr(self) -> _LogsReader:
        ...

    @property
    def returncode(self) -> typing.Union[int, None]:
        ...


class Sandbox(modal.object.Object):
    _result: typing.Union[modal_proto.api_pb2.GenericResult, None]
    _stdout: LogsReader
    _stderr: LogsReader

    def __init__(self, *args, **kwargs):
        ...

    @staticmethod
    def _new(entrypoint_args: typing.Sequence[str], image: modal.image.Image, mounts: typing.Sequence[modal.mount.Mount], secrets: typing.Sequence[modal.secret.Secret], timeout: typing.Union[int, None] = None, workdir: typing.Union[str, None] = None, gpu: typing.Union[None, bool, str, modal.gpu._GPUConfig] = None, cloud: typing.Union[str, None] = None, cpu: typing.Union[float, None] = None, memory: typing.Union[int, None] = None, network_file_systems: typing.Dict[typing.Union[str, os.PathLike], modal.network_file_system.NetworkFileSystem] = {}, block_network: bool = False, volumes: typing.Dict[typing.Union[str, os.PathLike], typing.Union[modal.volume.Volume, modal.s3mount.S3Mount]] = {}) -> Sandbox:
        ...

    def _hydrate_metadata(self, handle_metadata: typing.Union[google.protobuf.message.Message, None]):
        ...

    class __wait_spec(typing_extensions.Protocol):
        def __call__(self, raise_on_termination: bool = True):
            ...

        async def aio(self, *args, **kwargs):
            ...

    wait: __wait_spec

    class __terminate_spec(typing_extensions.Protocol):
        def __call__(self):
            ...

        async def aio(self, *args, **kwargs):
            ...

    terminate: __terminate_spec

    class __poll_spec(typing_extensions.Protocol):
        def __call__(self) -> typing.Union[int, None]:
            ...

        async def aio(self, *args, **kwargs) -> typing.Union[int, None]:
            ...

    poll: __poll_spec

    @property
    def stdout(self) -> LogsReader:
        ...

    @property
    def stderr(self) -> LogsReader:
        ...

    @property
    def returncode(self) -> typing.Union[int, None]:
        ...
