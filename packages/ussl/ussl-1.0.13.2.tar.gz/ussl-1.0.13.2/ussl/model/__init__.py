from dataclasses import dataclass
from typing import Optional, Any, Union, List


@dataclass
class Response:
    """
    Класс, описывающий ответ от конечной системы.

        ``result``: содержит исходный ответ от целевой системы;
        ``text``: содержится форматированный ответ от целевой системы;
        ``status``: содержится статус выполнения переданной команды.
    """
    result: str
    text: Optional[str] = None
    status: Optional[bool] = None


@dataclass
class Query:
    """
    Класс, описывающий запросы, передаваемые конечной системе.

        ``command``: содержит командe, которую необходимо выполнить;
        ``timeout``: содержит время, отведенное на выпонение команды;
        ``expects``: содержит регулярные выражения, которые описывают
        ожидаемый ответ от конечной системы;
        ``sudo``: содержит пароль от супер пользователя или enable.
    """
    command: str
    timeout: int = None
    expects: Optional[Union[List[str], str]] = None
    sudo: Optional[str] = None


@dataclass
class Protocol:
    """
    Класс, описывающий протокол для подключения к серверу используя указанный интерфейс.

    Общие для всех интерфейсов поля:
        ``host``: ip-адрес или имя хоста, к которому необходимо подключиться;
        ``username``: имя пользователя, под которым необходимо подключиться;
        ``password``: пароль от указанного пользователя;
        ``interface``: интерфейс, к которому необходимо подключиться (ssh, winrm, и т.д.);
        ``port``: порт, на котором работает интерфейс;
        ``query``: команда или набор команд, которые необходимо выполнить;
        ``encoding``: кодировка запроса;
        ``decoding``: кодировка ответа;
        ``window_width``: ширина окна консоли (влияет на форматирование ответа).

    Поля, специфичные для winrm:
        ``domain``: имя домена к которому необходимо подключиться;
        ``scheme``: схема подключения (http или https);
        ``path``: путь до WS-Management;
        ``transport``: протокол аутентификации.

    Поля, специфичные для ssh:
        ``clean_timeout``: таймаут очищения канала;
        ``look_for_keys``: включить или отключить аутентификацию по ключам;
        ``auth_timeout``: таймаут авторизации;
        ``timeout``: таймаут соединения;
        ``pem_file``: значение закрытого ключа авторизации от указанного пользователя.
    """
    host: str
    interface: str
    username: str
    domain: str

    password: str = None
    port: Optional[int] = None
    query: Optional[Union[List[Query], Query]] = None
    encoding: Optional[str] = None
    decoding: Optional[str] = None
    window_width: Optional[int] = None

    scheme: Optional[str] = None
    path: Optional[str] = None
    transport: Optional[str] = None

    clean_timeout: Optional[int] = None
    look_for_keys: Optional[bool] = None
    auth_timeout: Optional[int] = None
    timeout: Optional[int] = None
    pem_file: Optional[str] = None

    def default(self, key: str, default: Any = None):
        if self.__getattribute__(key) is not None:
            return self.__getattribute__(key)
        else:
            return default
