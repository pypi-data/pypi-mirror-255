from typing import List, Union


class SOARException(Exception):
    """
    Стандартный класс для исключений скриптов.

    Приватные поля:
        ``_return_code``(int): код возврата
        ``_TEMPLATE``(str): шаблон сообщения

    Публичные поля и свойства:
        ``message``(Union[List[str], str, dict]): информация об исключении
        ``return_code``(int): код возврата
    """
    _return_code: int = 1
    _TEMPLATE: str = 'Error: {args}.'

    message: Union[List[str], str, dict] = None

    @property
    def return_code(self):
        return self._return_code

    def __init__(self, message: Union[List[str], str, dict]):
        self.message = message

    def __str__(self):
        if isinstance(self.message, List):
            return self._TEMPLATE.format(args=', '.join(self.message))
        elif isinstance(self.message, str):
            return self._TEMPLATE.format(args=self.message)
        else:
            return self._TEMPLATE.format(args=str(self.message))