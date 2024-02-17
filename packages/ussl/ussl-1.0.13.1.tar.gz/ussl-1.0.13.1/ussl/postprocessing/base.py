import sys
import json
import warnings
import pathlib
from abc import abstractmethod, ABC
from typing import Union, Tuple

from marshmallow import Schema, exceptions, EXCLUDE
from ussl.exceptions import NoSecretsError, BadInputError, BadSecretsError

from ..exceptions import DataError, SOARException

warnings.filterwarnings("ignore")


class BaseFunction(ABC):
    """
    Является базовым классом для всех скриптов, участвующих в обогащении и реагировании.
    При использовании класса необходимо реализовать метод ``function``.
    Автоматически принимаемые значения:
        ``input_json``: Первым аргументом принимает информацию, переданную на вход плейбука;
        ``secrets``: Вторым аргументом приниает секреты.
        ``ensure_ascii``: Указывает, должны ли символы не из набора ASCII быть экранированы. По умолчанию False.
    """
    inputs_model: Schema = None
    secrets_model: Schema = None
    ensure_ascii: bool = False
    _input_json: dict = None
    _secrets: dict = None

    def __init__(self,
                 inputs_model: Schema = None,
                 secrets_model: Schema = None,
                 ensure_ascii: bool = False) -> None:
        """
        Инициализирует экземпляр класса.
        Args:
            ``ensure_ascii (bool)``: Указывает, должны ли символы не из набора ASCII быть экранированы. По умолчанию False
            ``inputs_model (Schema)``: модель входных данных
            ``secrets_model (Schema)``: модель секретов
        Returns:
            ``None``
        """
        self.inputs_model = inputs_model
        self.secrets_model = secrets_model
        self.ensure_ascii = ensure_ascii

        self.inputs_model.Meta.unknown = EXCLUDE
        self.secrets_model.Meta.unknown = EXCLUDE

        try:
            self._set_valid_input_data()
        except DataError as e:
            self._output_json(str(e), e.return_code)

        try:
            result, message = self.function()
        except SOARException as e:
            self._output_json(str(e), e.return_code)
        except (TypeError, NotImplementedError):
            self._output_json("Incorrect script", 1)
        else:
            self._output_json(message, **result)

    def _set_valid_input_data(self):
        inputs = pathlib.Path(sys.argv[1]).read_text(encoding='utf-8')
        secrets = pathlib.Path(sys.argv[2]).read_text(encoding='utf-8')

        self._input_json = json.loads(inputs)
        try:
            self._secrets = json.loads(secrets)['secrets']
        except KeyError:
            raise NoSecretsError("Secrets not found")

        # Валидируем входные данные
        if self.inputs_model is not None:
            try:
                self.input_json = self.inputs_model.load(self._input_json)
            except exceptions.ValidationError as e:
                if isinstance(e.messages, dict):
                    raise BadInputError({f"Input data validation error": e.args})
                else:
                    raise BadInputError({f"Input data validation error: {str(e)}": e.args})
        else:
            self.input_json: dict = self._input_json.copy()
        # Валидируем секреты
        if self.secrets_model is not None:
            try:
                self.secrets = self.secrets_model.load(self._secrets)
            except exceptions.ValidationError as e:
                if isinstance(e.messages, dict):
                    raise BadSecretsError({f"Input data validation error": e.messages})
                else:
                    raise BadSecretsError({f"Input data validation error: {str(e)}": e.messages})
        else:
            self.secrets: dict = self._secrets.copy()


    @abstractmethod
    def function(self) -> Tuple[dict, str]:
        """
        В этом методе необходимо реализовать функцию по обогащению
        или реагированию.

        Методу доступны переменные input_json и secrets.

        Для получения данных используйте переменные input_json и secrets класса BaseFunction.
        Для вывода ошибок необходимо использовать исключения из модуля exceptions.
        Returns:
            (dict, str): Результат обогащения или реагирования и сообщение о результате.
        """
        raise NotImplementedError('Метод function не реализован')

    def _output_json(self,
                     message: Union[str, dict],
                     return_code: int = 0,
                     **kwargs) -> None:
        """
        Выводит результат работы скрипта в формате JSON.

        Args:
            ``message (str)``: Сообщение о результате выполнения скрипта, которое будет выведено.
            ``return_code (int)``: Код возврата, указывающий на успешное выполнение (0) или ошибку (ненулевое значение).
            ``**kwargs``: Дополнительные именованные аргументы. Например, результат сбора данных.

        Returns:
            ``None``
        """
        # Обновляем входной JSON с результатом или сообщением об ошибке
        self._input_json['error' if return_code else 'result'] = message

        # Обновляем входной JSON новыми аргументами
        self._input_json.update(kwargs)

        # Выводим входной JSON в форматированном виде
        print(json.dumps(self._input_json, ensure_ascii=self.ensure_ascii))

        # Завершаем выполнение скрипта с кодом 0 в случае успешного выполнения или ненулевым в случае ошибки
        exit(return_code)
