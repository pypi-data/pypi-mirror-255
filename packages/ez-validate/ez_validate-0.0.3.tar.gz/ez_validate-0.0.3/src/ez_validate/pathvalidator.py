import os

from .validationerror import ValidationError


class PathValidator:
    def __init__(self, var, name='"Untitled var"'):
        # type: (PathValidator, str, str) -> None
        if not isinstance(name, str):
            raise TypeError('Name must be an instance of {} but is {}'.format(str, type(name)))
        if not isinstance(var, str):
            raise TypeError('Variable must be an instance of {} but is {}'.format(str, type(var)))
        if not os.path.exists(var):
            raise TypeError('Variable must be an existing path but is {}'.format(float, var))
        self.__var__ = var
        self.__var_name__ = name

    def is_dir(self):
        # type: (PathValidator) -> PathValidator
        if not os.path.isdir(self.__var__):
            raise ValidationError('{} must be a directory but is {}'
                                  .format(self.__var_name__, self.__var__))
        return self

    def is_file(self):
        # type: (PathValidator) -> PathValidator
        if not os.path.isfile(self.__var__):
            raise ValidationError('{} must be a file but is {}'
                                  .format(self.__var_name__, self.__var__))
        return self

