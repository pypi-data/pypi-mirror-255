class RPC:
    PING_COMMAND: str = "__ping__"
    EVENT_COMMAND: str = "__event__"
    SUBSCRIBE_COMMAND: str = "__subscribe__"

    @staticmethod
    def PORT(add: int = 0) -> int:
        return 50051 + add

    TIMEOUT: int | None = None
    TIMEOUT_FOR_PING: int = 20
    LONG_OPERATION_DURATION: int | None = None