from ussl.exceptions import SOARException


class ProtocolError(SOARException):
    """ Базовый класс, описывающий ошибки удаленного доступа. """
    _return_code: int = 20
    _TEMPLATE = 'Protocol error: {args}.'


class ConnectionFailed(ProtocolError):
    """ Класс, описывающий ошибку подключения к удаленному хосту. """
    _return_code: int = 21
    _TEMPLATE = 'Connection failed: {args}.'


class CredentialsError(ProtocolError):
    """ Класс, описывающий ошибку авторизации. """
    _return_code: int = 22
    _TEMPLATE = 'Invalid credentials: {args}.'


class PermissionsError(ProtocolError):
    """ Класс, описывающий ошибку доступа. """
    _return_code: int = 23
    _TEMPLATE = 'Missing permissions: {args}.'


class ExecutionError(ProtocolError):
    """ Класс, описывающий ошибку выполнения команд. """
    _return_code: int = 24
    _TEMPLATE = 'Command execution error: {args}.'
