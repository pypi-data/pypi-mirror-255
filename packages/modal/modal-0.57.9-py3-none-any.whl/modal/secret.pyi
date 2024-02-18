import modal.object
import typing

class _Secret(modal.object._StatefulObject):
    @staticmethod
    def from_dict(env_dict: typing.Dict[str, typing.Union[str, None]] = {}):
        ...

    @staticmethod
    def from_dotenv(path=None):
        ...


class Secret(modal.object.StatefulObject):
    def __init__(self, *args, **kwargs):
        ...

    @staticmethod
    def from_dict(env_dict: typing.Dict[str, typing.Union[str, None]] = {}):
        ...

    @staticmethod
    def from_dotenv(path=None):
        ...
