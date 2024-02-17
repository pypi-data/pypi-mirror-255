import re
import ssl
from typing import Any, Union

import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import ReadTimeout
from urllib3 import ProxyManager
from urllib3.util.ssl_ import create_urllib3_context
from winrm.exceptions import (
    AuthenticationError,
    WinRMError,
    WinRMOperationTimeoutError,
    WinRMTransportError,
)
from winrm.protocol import Protocol as WmProtocol

from .base import BaseProtocol
from ..model import Response, Protocol, Query
from ..exceptions import ConnectionFailed, ExecutionError, CredentialsError

WINRM_PORT = 5985
WINRM_SSL_PORT = 5986
VALID_TRANSPORT = {'plaintext', 'ntlm'}


class TLSv1Adapter(HTTPAdapter):
    """
    Включаем поддержку TLSv1.0 для старых версий Windows.
    """

    def init_poolmanager(self, *args: Any, **kwargs: Any) -> None:
        context = create_urllib3_context()
        context.minimum_version = ssl.TLSVersion.TLSv1
        context.options &= (
            ~ssl.OP_NO_TLSv1_3  # pylint: disable=no-member
            & ~ssl.OP_NO_TLSv1_2
            & ~ssl.OP_NO_TLSv1_1
            & ~ssl.OP_NO_TLSv1
        )
        kwargs['ssl_context'] = context
        return super().init_poolmanager(*args, **kwargs)

    def proxy_manager_for(self, *args: Any, **kwargs: Any) -> ProxyManager:
        context = create_urllib3_context()
        context.minimum_version = ssl.TLSVersion.TLSv1
        context.options &= (
            ~ssl.OP_NO_TLSv1_3  # pylint: disable=no-member
            & ~ssl.OP_NO_TLSv1_2
            & ~ssl.OP_NO_TLSv1_1
            & ~ssl.OP_NO_TLSv1
        )
        kwargs['ssl_context'] = context
        return super().proxy_manager_for(*args, **kwargs)


class WinRMProtocol(BaseProtocol):
    name = 'winrm'

    def __init__(self) -> None:
        self._protocol: WmProtocol
        self._shell_id = None
        # self._encoding = 437

    def connect(
        self,
        protocol: Protocol,
    ) -> None:
        host = protocol.host
        username = protocol.username
        domain = protocol.domain
        password = protocol.password
        scheme = protocol.default('scheme', 'https')
        if scheme == 'https':
            port = protocol.default('port', WINRM_SSL_PORT)
        else:
            port = protocol.default('port', WINRM_PORT)
        path = protocol.default('path', 'wsman')
        # Отправка запроса в кодировке 437 даёт ответ на анлийском языке
        # однако при преобразовании байтов в строку и использованием той же
        # кодировки русские символы отображаются некорректно. Для того чтобы
        # обойти эту проблему, для декодирования используется кодировка 866
        encoding = protocol.default('encoding', 437)
        self._decoding = protocol.default('decoding', 866)
        window_width = protocol.default('window_width', 300)
        transport = protocol.default('transport', 'ntlm')

        if transport not in VALID_TRANSPORT:
            raise ConnectionFailed(f'{transport} protocol is not supported')

        # для BasicAuth явно преобразуем 'username' и 'password' из utf8 в cp1251, т.к. requests.auth.HTTPBasicAuth
        # по умолчанию преобразует utf8 строки в latin1, при этом bytes оставляет 'как есть'.
        # https://github.com/requests/requests/pull/3673
        _username: Union[str, bytes] = f'{domain}\\{username}'
        _password: Union[str, bytes] = password
        if transport == 'plaintext':
            _username = f'{domain}\\{username}'.encode('cp1251')
            _password = password.encode('cp1251')
        else:
            _username = f'{domain}\\{username}'
            _password = password

        endpoint = f'{scheme}://{host}:{port}/{path}'
        try:
            self._protocol = WmProtocol(
                endpoint=endpoint,
                username=_username,
                password=_password,
                transport=transport,
                server_cert_validation='ignore'
            )

            self._protocol.transport.build_session()
            self._protocol.transport.session.mount(endpoint, TLSv1Adapter())
            self._shell_id = self._protocol.open_shell(codepage=encoding)

            self.execute(Query(command=f'mode con:cols={window_width}', timeout=10))
        except requests.exceptions.ConnectionError as e:
            raise ConnectionFailed(str(e))

    def close(self) -> None:
        self._protocol.close_shell(self._shell_id)
        self._shell_id = None

    def execute(
            self,
            query: Query
            ) -> Response:
        self._protocol.read_timeout_sec = (
            self._protocol.transport.read_timeout_sec
        ) = query.timeout if query.timeout else 10

        try:
            command_id = self._protocol.run_command(self._shell_id, query.command)
            std_out, std_err, status_code = self._protocol.get_command_output(
                self._shell_id, command_id
            )
            if status_code != 0:
                std_err = std_err.decode(encoding=str(self._decoding)).strip()
                return Response(
                    result=std_err,
                    status=False,
                    text=f'Команда {query.command} не выполнена')

            std_out = std_out.decode(encoding=str(self._decoding)).strip()
            if query.expects is not None:
                for pattern in query.expects:
                    if re.search(pattern, std_out):
                        return Response(
                            result=std_out,
                            text=f'Команда {query.command} выполнена успешно',
                            status=True)
                return Response(
                    result=std_out,
                    text=f'Команда {query.command} вернула неожиданный ответ',
                    status=False)
            else:
                return Response(
                    result=std_out,
                    text=f'Команда {query.command} выполнена успешно',
                    status=True)

        except WinRMTransportError as exc:
            raise ConnectionFailed(exc.__str__())

        except AuthenticationError as exc:
            raise CredentialsError(exc.__str__())

        except (WinRMOperationTimeoutError, ReadTimeout):
            raise ConnectionFailed('Connection timeout')

        except WinRMError as exc:
            raise ExecutionError(
                {"command": query.command, "error": exc.__str__()}
            ) from exc

        finally:
            self._protocol.cleanup_command(self._shell_id, command_id)
