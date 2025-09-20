class StorageException(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class MissingRequiredNodeError(StorageException):
    def __init__(self, *args):
        super().__init__(*args)


class NodeTypeMismatchError(StorageException):
    def __init__(self, *args):
        super().__init__(*args)
