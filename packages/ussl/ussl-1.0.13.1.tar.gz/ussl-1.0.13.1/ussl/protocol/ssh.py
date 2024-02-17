import io
import re
import socket
import time
from paramiko import AutoAddPolicy, Channel, SSHClient, RSAKey
from paramiko.config import SSH_PORT
from paramiko.ssh_exception import SSHException


from ..model import Query, Response, Protocol
from .base import BaseProtocol
from ..exceptions import ConnectionFailed, ExecutionError


class SSHProtocol(BaseProtocol):
    name = 'ssh'

    def __init__(self) -> None:
        self._chan: Channel
        self._client = SSHClient()
        self._client.set_missing_host_key_policy(AutoAddPolicy())

    def _clean_channel(self) -> None:
        prev_timeout = self._chan.gettimeout()
        self._chan.settimeout(self._clean_timeout)
        # pylint: disable=too-many-nested-blocks
        try:
            while self._chan.get_transport().is_active():
                try:
                    tmp = self._chan.recv(1024)
                    if len(tmp) == 0:
                        break
                except socket.timeout:
                    break
        finally:
            self._chan.settimeout(prev_timeout)

    def connect(
            self,
            protocol: Protocol,
            ) -> None:
        self._encoding = protocol.default('encoding', 'utf-8')
        self._clean_timeout = protocol.default('clean_timeout', 2)
        port = protocol.default('port', SSH_PORT)
        timeout = protocol.default('timeout', 10)
        look_for_keys = protocol.default('look_for_keys', False)
        window_width = protocol.default('window_width', 300)
        auth_timeout = protocol.default('auth_timeout', 60)

        if protocol.password:
            try:
                self._client.connect(
                    protocol.host,
                    port,
                    protocol.username,
                    protocol.password,
                    timeout=timeout,
                    look_for_keys=look_for_keys,
                    auth_timeout=auth_timeout
                )
                self._chan = self._client.invoke_shell(width=window_width)
                self._clean_channel()
            except (SSHException, socket.timeout) as exc:
                raise ConnectionFailed(str(exc))

        elif protocol.pem_file:
            try:
                keyfile = io.StringIO(protocol.pem_file)
                self._client.connect(
                    protocol.host,
                    port,
                    protocol.username,
                    pkey=RSAKey.from_private_key(keyfile),
                    timeout=timeout,
                    look_for_keys=look_for_keys,
                    auth_timeout=auth_timeout
                )
                self._chan = self._client.invoke_shell(width=window_width)
                self._clean_channel()
            except (SSHException, socket.timeout) as exc:
                raise ConnectionFailed(str(exc))

    def close(self) -> None:
        if self._chan is not None:
            self._chan.close()
        self._client.close()

    def execute(
            self,
            query: Query
            ) -> Response:
        data = b''

        prev_timeout = self._chan.gettimeout()

        if query.sudo is not None:
            try:
                self._chan.send(f'{query.command}\n')
                self._chan.send(f'{query.sudo}\n')
            except SSHException as exc:
                raise ExecutionError(
                    {"command": query.command, "error": str(exc)}
                ) from exc
        else:
            try:
                self._chan.send(f'{query.command}\n')
            except SSHException as exc:
                raise ExecutionError(
                    {"command": query.command, "error": exc.__str__()}
                ) from exc

        while True:
            self._chan.settimeout(query.timeout)
            try:
                data = data + self._chan.recv(1024)
                time.sleep(0.5)
            except socket.timeout:
                break
            finally:
                self._chan.settimeout(prev_timeout)

        # На линукс (ubuntu) системах помимо результата в ответ попадает лишняя
        # информация (Имя пользователя, сама команда и т.д.). Этот костыль нужен
        # для того чтобы оставить в выводе только результат работы команды.
        if len(data.splitlines()) > 2:
            result_list = data.splitlines()
            del result_list[0], result_list[-1]
            result = ''.join([i.decode(self._encoding) for i in result_list])
        else:
            result = data

        if query.expects is not None:
            for pattern in query.expects:
                if re.search(pattern, result):
                    return Response(
                        result=result,
                        text=f'Команда {query.command} выполнена успешно',
                        status=True)

            return Response(
                result=result,
                text=f'Команда {query.command} вернула неожиданный ответ',
                status=False)
        else:
            return Response(
                result=result,
                text=f'Команда {query.command} выполнена успешно',
                status=True)
