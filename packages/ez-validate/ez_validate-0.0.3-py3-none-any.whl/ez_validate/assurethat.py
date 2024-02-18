import os

from .validationerror import ValidationError
from .intvalidator import IntValidator
from .floatvalidator import FloatValidator
from .strvalidator import StrValidator
from .pathvalidator import PathValidator


class AssureThat:
    def __init__(self, var, name='"Untitled var"'):
        # type: (AssureThat, ..., str) -> None
        if not isinstance(name, str):
            raise TypeError('Name must be an instance of {} but is {}'.format(str, type(name)))
        self.__var__ = var
        self.__var_name__ = name

    def is_float(self):
        # type: (AssureThat) -> FloatValidator
        self.__validate_type__(float)
        return FloatValidator(self.__var__, name=self.__var_name__)

    def is_int(self):
        # type: (AssureThat) -> IntValidator
        self.__validate_type__(int)
        return IntValidator(self.__var__, name=self.__var_name__)

    def is_str(self):
        # type: (AssureThat) -> StrValidator
        self.__validate_type__(str)
        return StrValidator(self.__var__, name=self.__var_name__)

    def is_existing_path(self):
        # type: (AssureThat) -> PathValidator
        if (not isinstance(self.__var__, str)) or (not os.path.exists(self.__var__)):
            raise ValidationError('{} must be an existing path but is {}'
                                  .format(self.__var_name__, self.__var__))
        return PathValidator(self.__var__, name=self.__var_name__)

    def is_none(self):
        # type: (AssureThat) -> None
        if self.__var__ is not None:
            raise ValidationError('{} must be None but is {}'.format(self.__var_name__, self.__var__))

    def __validate_type__(self, _type):
        # type: (AssureThat, type) -> None
        if not isinstance(self.__var__, _type):
            raise ValidationError('{} must be an instance of {} but is {}'
                                  .format(self.__var_name__, _type, type(self.__var__)))
