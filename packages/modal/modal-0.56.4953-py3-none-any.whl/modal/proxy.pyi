import modal.object

class _Proxy(modal.object._StatefulObject):
    ...

class Proxy(modal.object.StatefulObject):
    def __init__(self, *args, **kwargs):
        ...
