class RpcError(Exception):
    pass


class TemporaryError(RpcError):
    pass


class FinalError(RpcError):
    pass


class UnknownError(FinalError):
    pass


class UnhandledError(FinalError):
    pass


class ParsingError(FinalError):
    pass


class UnknownServiceError(FinalError):
    pass


class UnknownMethodError(FinalError):
    pass


class ExecutionError(FinalError):
    pass
