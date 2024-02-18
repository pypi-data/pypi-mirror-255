from .validationerror import ValidationError


class FloatValidator:
    def __init__(self, var, name='"Untitled var"'):
        # type: (FloatValidator, float, str) -> None
        if not isinstance(name, str):
            raise TypeError('Name must be an instance of {} but is {}'.format(str, type(name)))
        if not isinstance(var, float):
            raise TypeError('Variable must be an instance of {} but is {}'.format(float, type(var)))
        self.__var__ = var
        self.__var_name__ = name

    def less_than(self, value):
        # type: (FloatValidator, float) -> FloatValidator
        if not self.__var__ < value:
            raise ValidationError('{} must be less than {} but is {}'
                                  .format(self.__var_name__, value, self.__var__))
        return self

    def greater_than(self, value):
        # type: (FloatValidator, float) -> FloatValidator
        if not self.__var__ > value:
            raise ValidationError('{} must be greater than {} but is {}'
                                  .format(self.__var_name__, value, self.__var__))
        return self

    def less_or_equal(self, value):
        # type: (FloatValidator, float) -> FloatValidator
        if not self.__var__ <= value:
            raise ValidationError('{} must be less than or equal to {} but is {}'
                                  .format(self.__var_name__, value, self.__var__))
        return self

    def greater_or_equal(self, value):
        # type: (FloatValidator, float) -> FloatValidator
        if not self.__var__ >= value:
            raise ValidationError('{} must be greater than or equal to {} but is {}'
                                  .format(self.__var_name__, value, self.__var__))
        return self
