from typing import Union

from ..protocol import (
    INTERFACES,
    base
)
from ..model import Protocol, Response, Query
from ..exceptions import ConnectionFailed


class Transport:
    def __init__(self) -> None:
        pass

    def _connect(self, protocol: Protocol):
        if not protocol.interface:
            raise ConnectionFailed('Do not specify the interface on which you want to communicate')
        if protocol.interface not in INTERFACES:
            raise ConnectionFailed('Specified interface not supported')

        self.proto: base.BaseProtocol = INTERFACES[protocol.interface]()
        self.proto.connect(protocol)

    def _execute(self, query: Union[Query, list]) -> Response:
        try:
            if isinstance(query, list):
                for q in range(len(query)):
                    response: Response = self.proto.execute(query[q])
                    if response.status is False:
                        return response
            else:
                response: Response = self.proto.execute(query)

            return response
        finally:
            self.proto.close()

    def connect(self, protocol: Protocol):
        self._connect(protocol)

    def execute(self, query: Union[dict, list]) -> Response:
        return self._execute(query)

    def connect_and_execute(self, protocol: Protocol) -> Response:
        query = protocol.query
        self._connect(protocol)
        return self._execute(query)
