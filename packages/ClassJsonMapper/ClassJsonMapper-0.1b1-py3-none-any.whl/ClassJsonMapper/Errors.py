class FilePathError(Exception):
     def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class DictKeyError(KeyError):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class ListIndexError(IndexError):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class JsonFileError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)
        

class IncompleteParameters(ValueError):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(message)