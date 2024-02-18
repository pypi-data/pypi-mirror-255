import google.protobuf.message
import modal._function_utils
import modal._output
import modal.call_graph
import modal.client
import modal.gpu
import modal.image
import modal.mount
import modal.network_file_system
import modal.object
import modal.proxy
import modal.retries
import modal.s3mount
import modal.schedule
import modal.secret
import modal.stub
import modal.volume
import modal_proto.api_pb2
import os
import pathlib
import typing
import typing_extensions

def exc_with_hints(exc: BaseException):
    ...


async def _process_result(result: modal_proto.api_pb2.GenericResult, data_format: int, stub, client=None):
    ...


async def _create_input(args, kwargs, client, idx=None) -> modal_proto.api_pb2.FunctionPutInputsItem:
    ...


def _stream_function_call_data(client, function_call_id: str, variant: typing.Literal['data_in', 'data_out']) -> typing.AsyncIterator[typing.Any]:
    ...


class _OutputValue:
    value: typing.Any

    def __init__(self, value: typing.Any) -> None:
        ...

    def __repr__(self):
        ...

    def __eq__(self, other):
        ...


class _Invocation:
    def __init__(self, stub, function_call_id, client=None):
        ...

    @staticmethod
    async def create(function_id: str, args, kwargs, client: modal.client._Client):
        ...

    def pop_function_call_outputs(self, timeout: typing.Union[float, None], clear_on_success: bool) -> typing.AsyncIterator[modal_proto.api_pb2.FunctionGetOutputsItem]:
        ...

    async def run_function(self):
        ...

    async def poll_function(self, timeout: typing.Union[float, None] = None):
        ...

    def run_generator(self):
        ...


def _map_invocation(function_id: str, input_stream: typing.AsyncIterable[typing.Any], kwargs: typing.Dict[str, typing.Any], client: modal.client._Client, order_outputs: bool, return_exceptions: bool, count_update_callback: typing.Union[typing.Callable[[int, int], None], None]):
    ...


class FunctionStats:
    backlog: int
    num_active_runners: int
    num_total_runners: int

    def __init__(self, backlog: int, num_active_runners: int, num_total_runners: int) -> None:
        ...

    def __repr__(self):
        ...

    def __eq__(self, other):
        ...

    def __setattr__(self, name, value):
        ...

    def __delattr__(self, name):
        ...

    def __hash__(self):
        ...


def _parse_retries(retries: typing.Union[int, modal.retries.Retries, None], raw_f: typing.Union[typing.Callable, None] = None) -> typing.Union[modal_proto.api_pb2.FunctionRetryPolicy, None]:
    ...


class FunctionEnv:
    image: typing.Union[modal.image._Image, None]
    mounts: typing.Sequence[modal.mount._Mount]
    secrets: typing.Sequence[modal.secret._Secret]
    network_file_systems: typing.Dict[typing.Union[str, pathlib.PurePosixPath], modal.network_file_system._NetworkFileSystem]
    volumes: typing.Dict[typing.Union[str, os.PathLike], typing.Union[modal.volume._Volume, modal.s3mount._S3Mount]]
    gpu: typing.Union[None, bool, str, modal.gpu._GPUConfig]
    cloud: typing.Union[str, None]
    cpu: typing.Union[float, None]
    memory: typing.Union[int, None]

    def __init__(self, image: typing.Union[modal.image._Image, None], mounts: typing.Sequence[modal.mount._Mount], secrets: typing.Sequence[modal.secret._Secret], network_file_systems: typing.Dict[typing.Union[str, pathlib.PurePosixPath], modal.network_file_system._NetworkFileSystem], volumes: typing.Dict[typing.Union[str, os.PathLike], typing.Union[modal.volume._Volume, modal.s3mount._S3Mount]], gpu: typing.Union[None, bool, str, modal.gpu._GPUConfig], cloud: typing.Union[str, None], cpu: typing.Union[float, None], memory: typing.Union[int, None]) -> None:
        ...

    def __repr__(self):
        ...

    def __eq__(self, other):
        ...


class _Function(modal.object._Object):
    _info: modal._function_utils.FunctionInfo
    _all_mounts: typing.Collection[modal.mount._Mount]
    _stub: modal.stub._Stub
    _obj: typing.Any
    _web_url: typing.Union[str, None]
    _is_remote_cls_method: bool
    _function_name: typing.Union[str, None]
    _is_method: bool
    _env: FunctionEnv

    @staticmethod
    def from_args(info: modal._function_utils.FunctionInfo, stub, image=None, secret: typing.Union[modal.secret._Secret, None] = None, secrets: typing.Collection[modal.secret._Secret] = (), schedule: typing.Union[modal.schedule.Schedule, None] = None, is_generator=False, gpu: typing.Union[None, bool, str, modal.gpu._GPUConfig] = None, mounts: typing.Collection[modal.mount._Mount] = (), network_file_systems: typing.Dict[typing.Union[str, os.PathLike], modal.network_file_system._NetworkFileSystem] = {}, allow_cross_region_volumes: bool = False, volumes: typing.Dict[typing.Union[str, os.PathLike], typing.Union[modal.volume._Volume, modal.s3mount._S3Mount]] = {}, webhook_config: typing.Union[modal_proto.api_pb2.WebhookConfig, None] = None, memory: typing.Union[int, None] = None, proxy: typing.Union[modal.proxy._Proxy, None] = None, retries: typing.Union[int, modal.retries.Retries, None] = None, timeout: typing.Union[int, None] = None, concurrency_limit: typing.Union[int, None] = None, allow_concurrent_inputs: typing.Union[int, None] = None, container_idle_timeout: typing.Union[int, None] = None, cpu: typing.Union[float, None] = None, keep_warm: typing.Union[int, None] = None, interactive: bool = False, cloud: typing.Union[str, None] = None, is_builder_function: bool = False, cls: typing.Union[type, None] = None, is_auto_snapshot: bool = False, checkpointing_enabled: bool = False, allow_background_volume_commits: bool = False, block_network: bool = False, max_inputs: typing.Union[int, None] = None) -> None:
        ...

    def from_parametrized(self, obj, from_other_workspace: bool, options: typing.Union[modal_proto.api_pb2.FunctionOptions, None], args: typing.Iterable[typing.Any], kwargs: typing.Dict[str, typing.Any]) -> _Function:
        ...

    @classmethod
    def from_name(cls: typing.Type[_Function], app_name: str, tag: typing.Union[str, None] = None, namespace=1, environment_name: typing.Union[str, None] = None) -> _Function:
        ...

    @staticmethod
    async def lookup(app_name: str, tag: typing.Union[str, None] = None, namespace=1, client: typing.Union[modal.client._Client, None] = None, environment_name: typing.Union[str, None] = None) -> _Function:
        ...

    @property
    def tag(self):
        ...

    @property
    def stub(self) -> modal.stub._Stub:
        ...

    @property
    def info(self) -> modal._function_utils.FunctionInfo:
        ...

    @property
    def env(self) -> FunctionEnv:
        ...

    def get_build_def(self) -> str:
        ...

    def _initialize_from_empty(self):
        ...

    def _hydrate_metadata(self, metadata: google.protobuf.message.Message):
        ...

    def _get_metadata(self):
        ...

    def _set_mute_cancellation(self, value: bool = True):
        ...

    def _set_output_mgr(self, output_mgr: modal._output.OutputManager):
        ...

    @property
    def web_url(self) -> str:
        ...

    @property
    def is_generator(self) -> bool:
        ...

    def _map(self, input_stream: typing.AsyncIterable[typing.Any], order_outputs: bool, return_exceptions: bool, kwargs={}):
        ...

    async def _call_function(self, args, kwargs):
        ...

    async def _call_function_nowait(self, args, kwargs):
        ...

    def _call_generator(self, args, kwargs):
        ...

    async def _call_generator_nowait(self, args, kwargs):
        ...

    def map(self, *input_iterators, kwargs={}, order_outputs: bool = True, return_exceptions: bool = False) -> typing.AsyncGenerator[typing.Any, None]:
        ...

    async def for_each(self, *input_iterators, kwargs={}, ignore_exceptions: bool = False):
        ...

    def starmap(self, input_iterator, kwargs={}, order_outputs: bool = True, return_exceptions: bool = False) -> typing.AsyncGenerator[typing.Any, None]:
        ...

    async def remote(self, *args, **kwargs) -> typing.Any:
        ...

    def remote_gen(self, *args, **kwargs) -> typing.AsyncGenerator[typing.Any, None]:
        ...

    def call(self, *args, **kwargs) -> typing.Awaitable[typing.Any]:
        ...

    async def shell(self, *args, **kwargs) -> None:
        ...

    def _get_is_remote_cls_method(self):
        ...

    def _get_info(self):
        ...

    def _get_obj(self):
        ...

    def local(self, *args, **kwargs) -> typing.Any:
        ...

    def __call__(self, *args, **kwargs) -> typing.Any:
        ...

    async def spawn(self, *args, **kwargs) -> typing.Union[_FunctionCall, None]:
        ...

    def get_raw_f(self) -> typing.Callable[..., typing.Any]:
        ...

    async def get_current_stats(self) -> FunctionStats:
        ...


class Function(modal.object.Object):
    _info: modal._function_utils.FunctionInfo
    _all_mounts: typing.Collection[modal.mount.Mount]
    _stub: modal.stub.Stub
    _obj: typing.Any
    _web_url: typing.Union[str, None]
    _is_remote_cls_method: bool
    _function_name: typing.Union[str, None]
    _is_method: bool
    _env: FunctionEnv

    def __init__(self, *args, **kwargs):
        ...

    @staticmethod
    def from_args(info: modal._function_utils.FunctionInfo, stub, image=None, secret: typing.Union[modal.secret.Secret, None] = None, secrets: typing.Collection[modal.secret.Secret] = (), schedule: typing.Union[modal.schedule.Schedule, None] = None, is_generator=False, gpu: typing.Union[None, bool, str, modal.gpu._GPUConfig] = None, mounts: typing.Collection[modal.mount.Mount] = (), network_file_systems: typing.Dict[typing.Union[str, os.PathLike], modal.network_file_system.NetworkFileSystem] = {}, allow_cross_region_volumes: bool = False, volumes: typing.Dict[typing.Union[str, os.PathLike], typing.Union[modal.volume.Volume, modal.s3mount.S3Mount]] = {}, webhook_config: typing.Union[modal_proto.api_pb2.WebhookConfig, None] = None, memory: typing.Union[int, None] = None, proxy: typing.Union[modal.proxy.Proxy, None] = None, retries: typing.Union[int, modal.retries.Retries, None] = None, timeout: typing.Union[int, None] = None, concurrency_limit: typing.Union[int, None] = None, allow_concurrent_inputs: typing.Union[int, None] = None, container_idle_timeout: typing.Union[int, None] = None, cpu: typing.Union[float, None] = None, keep_warm: typing.Union[int, None] = None, interactive: bool = False, cloud: typing.Union[str, None] = None, is_builder_function: bool = False, cls: typing.Union[type, None] = None, is_auto_snapshot: bool = False, checkpointing_enabled: bool = False, allow_background_volume_commits: bool = False, block_network: bool = False, max_inputs: typing.Union[int, None] = None) -> None:
        ...

    def from_parametrized(self, obj, from_other_workspace: bool, options: typing.Union[modal_proto.api_pb2.FunctionOptions, None], args: typing.Iterable[typing.Any], kwargs: typing.Dict[str, typing.Any]) -> Function:
        ...

    @classmethod
    def from_name(cls: typing.Type[Function], app_name: str, tag: typing.Union[str, None] = None, namespace=1, environment_name: typing.Union[str, None] = None) -> Function:
        ...

    class __lookup_spec(typing_extensions.Protocol):
        def __call__(self, app_name: str, tag: typing.Union[str, None] = None, namespace=1, client: typing.Union[modal.client.Client, None] = None, environment_name: typing.Union[str, None] = None) -> Function:
            ...

        async def aio(self, *args, **kwargs) -> Function:
            ...

    lookup: __lookup_spec

    @property
    def tag(self):
        ...

    @property
    def stub(self) -> modal.stub.Stub:
        ...

    @property
    def info(self) -> modal._function_utils.FunctionInfo:
        ...

    @property
    def env(self) -> FunctionEnv:
        ...

    def get_build_def(self) -> str:
        ...

    def _initialize_from_empty(self):
        ...

    def _hydrate_metadata(self, metadata: google.protobuf.message.Message):
        ...

    def _get_metadata(self):
        ...

    def _set_mute_cancellation(self, value: bool = True):
        ...

    def _set_output_mgr(self, output_mgr: modal._output.OutputManager):
        ...

    @property
    def web_url(self) -> str:
        ...

    @property
    def is_generator(self) -> bool:
        ...

    class ___map_spec(typing_extensions.Protocol):
        def __call__(self, input_stream: typing.Iterable[typing.Any], order_outputs: bool, return_exceptions: bool, kwargs={}):
            ...

        def aio(self, input_stream: typing.AsyncIterable[typing.Any], order_outputs: bool, return_exceptions: bool, kwargs={}):
            ...

    _map: ___map_spec

    class ___call_function_spec(typing_extensions.Protocol):
        def __call__(self, args, kwargs):
            ...

        async def aio(self, *args, **kwargs):
            ...

    _call_function: ___call_function_spec

    class ___call_function_nowait_spec(typing_extensions.Protocol):
        def __call__(self, args, kwargs):
            ...

        async def aio(self, *args, **kwargs):
            ...

    _call_function_nowait: ___call_function_nowait_spec

    def _call_generator(self, args, kwargs):
        ...

    class ___call_generator_nowait_spec(typing_extensions.Protocol):
        def __call__(self, args, kwargs):
            ...

        async def aio(self, *args, **kwargs):
            ...

    _call_generator_nowait: ___call_generator_nowait_spec

    class __map_spec(typing_extensions.Protocol):
        def __call__(self, *input_iterators, kwargs={}, order_outputs: bool = True, return_exceptions: bool = False) -> typing.Generator[typing.Any, None, None]:
            ...

        def aio(self, *input_iterators, kwargs={}, order_outputs: bool = True, return_exceptions: bool = False) -> typing.AsyncGenerator[typing.Any, None]:
            ...

    map: __map_spec

    class __for_each_spec(typing_extensions.Protocol):
        def __call__(self, *input_iterators, kwargs={}, ignore_exceptions: bool = False):
            ...

        async def aio(self, *args, **kwargs):
            ...

    for_each: __for_each_spec

    class __starmap_spec(typing_extensions.Protocol):
        def __call__(self, input_iterator, kwargs={}, order_outputs: bool = True, return_exceptions: bool = False) -> typing.Generator[typing.Any, None, None]:
            ...

        def aio(self, input_iterator, kwargs={}, order_outputs: bool = True, return_exceptions: bool = False) -> typing.AsyncGenerator[typing.Any, None]:
            ...

    starmap: __starmap_spec

    class __remote_spec(typing_extensions.Protocol):
        def __call__(self, *args, **kwargs) -> typing.Any:
            ...

        async def aio(self, *args, **kwargs) -> typing.Any:
            ...

    remote: __remote_spec

    class __remote_gen_spec(typing_extensions.Protocol):
        def __call__(self, *args, **kwargs) -> typing.Generator[typing.Any, None, None]:
            ...

        def aio(self, *args, **kwargs) -> typing.AsyncGenerator[typing.Any, None]:
            ...

    remote_gen: __remote_gen_spec

    class __call_spec(typing_extensions.Protocol):
        def __call__(self, *args, **kwargs) -> typing.Any:
            ...

        def aio(self, *args, **kwargs) -> typing.Awaitable[typing.Any]:
            ...

    call: __call_spec

    class __shell_spec(typing_extensions.Protocol):
        def __call__(self, *args, **kwargs) -> None:
            ...

        async def aio(self, *args, **kwargs) -> None:
            ...

    shell: __shell_spec

    def _get_is_remote_cls_method(self):
        ...

    def _get_info(self):
        ...

    def _get_obj(self):
        ...

    def local(self, *args, **kwargs) -> typing.Any:
        ...

    def __call__(self, *args, **kwargs) -> typing.Any:
        ...

    class __spawn_spec(typing_extensions.Protocol):
        def __call__(self, *args, **kwargs) -> typing.Union[FunctionCall, None]:
            ...

        async def aio(self, *args, **kwargs) -> typing.Union[FunctionCall, None]:
            ...

    spawn: __spawn_spec

    def get_raw_f(self) -> typing.Callable[..., typing.Any]:
        ...

    class __get_current_stats_spec(typing_extensions.Protocol):
        def __call__(self) -> FunctionStats:
            ...

        async def aio(self, *args, **kwargs) -> FunctionStats:
            ...

    get_current_stats: __get_current_stats_spec


class _FunctionCall(modal.object._Object):
    def _invocation(self):
        ...

    async def get(self, timeout: typing.Union[float, None] = None):
        ...

    async def get_call_graph(self) -> typing.List[modal.call_graph.InputInfo]:
        ...

    async def cancel(self):
        ...


class FunctionCall(modal.object.Object):
    def __init__(self, *args, **kwargs):
        ...

    def _invocation(self):
        ...

    class __get_spec(typing_extensions.Protocol):
        def __call__(self, timeout: typing.Union[float, None] = None):
            ...

        async def aio(self, *args, **kwargs):
            ...

    get: __get_spec

    class __get_call_graph_spec(typing_extensions.Protocol):
        def __call__(self) -> typing.List[modal.call_graph.InputInfo]:
            ...

        async def aio(self, *args, **kwargs) -> typing.List[modal.call_graph.InputInfo]:
            ...

    get_call_graph: __get_call_graph_spec

    class __cancel_spec(typing_extensions.Protocol):
        def __call__(self):
            ...

        async def aio(self, *args, **kwargs):
            ...

    cancel: __cancel_spec


async def _gather(*function_calls: _FunctionCall):
    ...


class __gather_spec(typing_extensions.Protocol):
    def __call__(self, *function_calls: FunctionCall):
        ...

    async def aio(self, *args, **kwargs):
        ...

gather: __gather_spec


def current_input_id() -> typing.Union[str, None]:
    ...


def current_function_call_id() -> typing.Union[str, None]:
    ...


def _set_current_context_ids(input_id: str, function_call_id: str) -> typing.Callable[[], None]:
    ...
