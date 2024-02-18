import modal.secret
import modal_proto.api_pb2
import typing

class _S3Mount:
    bucket_name: str
    secret: typing.Union[modal.secret._Secret, None]

    def __init__(self, bucket_name: str, secret: typing.Union[modal.secret._Secret, None]) -> None:
        ...

    def __repr__(self):
        ...

    def __eq__(self, other):
        ...


def s3_mounts_to_proto(mounts: typing.List[typing.Tuple[str, _S3Mount]]) -> typing.List[modal_proto.api_pb2.S3Mount]:
    ...


class S3Mount:
    bucket_name: str
    secret: typing.Union[modal.secret.Secret, None]

    def __init__(self, bucket_name: str, secret: typing.Union[modal.secret.Secret, None]) -> None:
        ...

    def __repr__(self):
        ...

    def __eq__(self, other):
        ...
