from ..model import Response, Query, Protocol


class BaseProtocol:

    def connect(self, protocol: Protocol) -> None:
        raise NotImplementedError('Метод connect не реализован')

    def execute(self, query: Query) -> Response:
        raise NotImplementedError('Метод execute не реализован')

    def close(self) -> None:
        raise NotImplementedError('Метод close не реализован')
