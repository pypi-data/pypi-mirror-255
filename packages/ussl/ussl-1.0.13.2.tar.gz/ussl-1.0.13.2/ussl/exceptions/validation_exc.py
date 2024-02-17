from ussl.exceptions import SOARException


class DataError(SOARException):
    """ Базовый класс для ошибок валидации. """
    _return_code: int = 10
    _TEMPLATE = 'Data error: {args}.'


class NoInputError(DataError):
    """ Класс для ошибок отсутствия обязательных входных данных. """
    _return_code: int = 11
    _TEMPLATE = 'Missing input data: {args}.'


class NoSecretsError(DataError):
    """ Класс для ошибок отсутствия обязательных секретов. """
    _return_code: int = 12
    _TEMPLATE = 'Missing secrets: {args}.'


class BadInputError(DataError):
    """ Класс для ошибок неверных входных данных. """
    _return_code: int = 13
    _TEMPLATE = 'Input data validation error: {args}.'


class BadSecretsError(DataError):
    """ Класс для ошибок неверных секретов. """
    _return_code: int = 14
    _TEMPLATE = 'Secrets validation error: {args}.'
