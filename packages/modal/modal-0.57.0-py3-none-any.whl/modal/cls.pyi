import google.protobuf.message
import modal._output
import modal.client
import modal.functions
import modal.gpu
import modal.object
import modal.partial_function
import modal.retries
import modal.secret
import modal.volume
import modal_proto.api_pb2
import os
import typing
import typing_extensions

T = typing.TypeVar("T")

class ClsMixin:
    @classmethod
    def __init_subclass__(cls):
        ...


def check_picklability(key, arg):
    ...


class _Obj:
    _functions: typing.Dict[str, modal.functions._Function]
    _inited: bool
    _entered: bool
    _local_obj: typing.Any
    _local_obj_constr: typing.Union[typing.Callable[[], typing.Any], None]

    def __init__(self, user_cls: type, output_mgr: typing.Union[modal._output.OutputManager, None], base_functions: typing.Dict[str, modal.functions._Function], from_other_workspace: bool, options: typing.Union[modal_proto.api_pb2.FunctionOptions, None], args, kwargs):
        ...

    def get_obj(self):
        ...

    def get_local_obj(self):
        ...

    def enter(self):
        ...

    @property
    def entered(self):
        ...

    async def aenter(self):
        ...

    def __getattr__(self, k):
        ...


class Obj:
    _functions: typing.Dict[str, modal.functions.Function]
    _inited: bool
    _entered: bool
    _local_obj: typing.Any
    _local_obj_constr: typing.Union[typing.Callable[[], typing.Any], None]

    def __init__(self, user_cls: type, output_mgr: typing.Union[modal._output.OutputManager, None], base_functions: typing.Dict[str, modal.functions.Function], from_other_workspace: bool, options: typing.Union[modal_proto.api_pb2.FunctionOptions, None], args, kwargs):
        ...

    def get_obj(self):
        ...

    def get_local_obj(self):
        ...

    def enter(self):
        ...

    @property
    def entered(self):
        ...

    async def aenter(self):
        ...

    def __getattr__(self, k):
        ...


class _Cls(modal.object._Object):
    _user_cls: typing.Union[type, None]
    _functions: typing.Dict[str, modal.functions._Function]
    _options: typing.Union[modal_proto.api_pb2.FunctionOptions, None]
    _callables: typing.Dict[str, typing.Callable]
    _from_other_workspace: typing.Union[bool, None]

    def _initialize_from_empty(self):
        ...

    def _initialize_from_other(self, other: _Cls):
        ...

    def _set_output_mgr(self, output_mgr: modal._output.OutputManager):
        ...

    def _hydrate_metadata(self, metadata: google.protobuf.message.Message):
        ...

    def _get_metadata(self) -> modal_proto.api_pb2.ClassHandleMetadata:
        ...

    @staticmethod
    def from_local(user_cls, stub, decorator: typing.Callable[[modal.partial_function.PartialFunction, type], modal.functions._Function]) -> _Cls:
        ...

    @classmethod
    def from_name(cls: typing.Type[_Cls], app_name: str, tag: typing.Union[str, None] = None, namespace=1, environment_name: typing.Union[str, None] = None, workspace: typing.Union[str, None] = None) -> _Cls:
        ...

    def with_options(self: _Cls, gpu: typing.Union[None, bool, str, modal.gpu._GPUConfig] = None, secrets: typing.Collection[modal.secret._Secret] = (), volumes: typing.Dict[typing.Union[str, os.PathLike], modal.volume._Volume] = {}, retries: typing.Union[int, modal.retries.Retries, None] = None, timeout: typing.Union[int, None] = None, concurrency_limit: typing.Union[int, None] = None, allow_concurrent_inputs: typing.Union[int, None] = None, container_idle_timeout: typing.Union[int, None] = None, keep_warm: typing.Union[int, None] = None, allow_background_volume_commits: bool = False) -> _Cls:
        ...

    @staticmethod
    async def lookup(app_name: str, tag: typing.Union[str, None] = None, namespace=1, client: typing.Union[modal.client._Client, None] = None, environment_name: typing.Union[str, None] = None, workspace: typing.Union[str, None] = None) -> _Cls:
        ...

    def __call__(self, *args, **kwargs) -> _Obj:
        ...

    async def remote(self, *args, **kwargs):
        ...

    def __getattr__(self, k):
        ...


class Cls(modal.object.Object):
    _user_cls: typing.Union[type, None]
    _functions: typing.Dict[str, modal.functions.Function]
    _options: typing.Union[modal_proto.api_pb2.FunctionOptions, None]
    _callables: typing.Dict[str, typing.Callable]
    _from_other_workspace: typing.Union[bool, None]

    def __init__(self, *args, **kwargs):
        ...

    def _initialize_from_empty(self):
        ...

    def _initialize_from_other(self, other: Cls):
        ...

    def _set_output_mgr(self, output_mgr: modal._output.OutputManager):
        ...

    def _hydrate_metadata(self, metadata: google.protobuf.message.Message):
        ...

    def _get_metadata(self) -> modal_proto.api_pb2.ClassHandleMetadata:
        ...

    @staticmethod
    def from_local(user_cls, stub, decorator: typing.Callable[[modal.partial_function.PartialFunction, type], modal.functions.Function]) -> Cls:
        ...

    @classmethod
    def from_name(cls: typing.Type[Cls], app_name: str, tag: typing.Union[str, None] = None, namespace=1, environment_name: typing.Union[str, None] = None, workspace: typing.Union[str, None] = None) -> Cls:
        ...

    def with_options(self: Cls, gpu: typing.Union[None, bool, str, modal.gpu._GPUConfig] = None, secrets: typing.Collection[modal.secret.Secret] = (), volumes: typing.Dict[typing.Union[str, os.PathLike], modal.volume.Volume] = {}, retries: typing.Union[int, modal.retries.Retries, None] = None, timeout: typing.Union[int, None] = None, concurrency_limit: typing.Union[int, None] = None, allow_concurrent_inputs: typing.Union[int, None] = None, container_idle_timeout: typing.Union[int, None] = None, keep_warm: typing.Union[int, None] = None, allow_background_volume_commits: bool = False) -> Cls:
        ...

    class __lookup_spec(typing_extensions.Protocol):
        def __call__(self, app_name: str, tag: typing.Union[str, None] = None, namespace=1, client: typing.Union[modal.client.Client, None] = None, environment_name: typing.Union[str, None] = None, workspace: typing.Union[str, None] = None) -> Cls:
            ...

        async def aio(self, *args, **kwargs) -> Cls:
            ...

    lookup: __lookup_spec

    def __call__(self, *args, **kwargs) -> Obj:
        ...

    class __remote_spec(typing_extensions.Protocol):
        def __call__(self, *args, **kwargs):
            ...

        async def aio(self, *args, **kwargs):
            ...

    remote: __remote_spec

    def __getattr__(self, k):
        ...
