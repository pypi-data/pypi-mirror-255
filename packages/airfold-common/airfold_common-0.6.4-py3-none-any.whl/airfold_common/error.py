class AirfoldError(Exception):
    pass


class AirfoldKeyError(AirfoldError, KeyError):
    pass


class AirfoldTypeError(AirfoldError, TypeError):
    pass


class MethodNotImplementedError(AirfoldError, NotImplementedError):
    pass


class DefaultMessageError(AirfoldError):
    message = "Error"

    def __init__(self, *args):
        if not args:
            args = (type(self).message,)
        super().__init__(*args)


class AirfoldWriteDeniedError(DefaultMessageError):
    message = "Write operation denied in read-only mode"


class AirfoldConflictError(DefaultMessageError):
    message = "Read operation conflict or database is locked: please retry"
