class ValidationError(BaseException):
    def __init__(self, message):
        # type: (ValidationError, str) -> None
        super(ValidationError, self).__init__(message)


class FloatValidator:
    def __init__(self, var, name='"Untitled var"'):
        # type: (FloatValidator, float, str) -> None
        if not isinstance(name, str):
            raise TypeError('Name must be an instance of {} but is {}'.format(str, name))
        if not isinstance(var, float):
            raise TypeError('Variable must be an instance of {} but is {}'.format(float, var))
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


class IntValidator:
    def __init__(self, var, name='"Untitled var"'):
        # type: (IntValidator, int, str) -> None
        if not isinstance(name, str):
            raise TypeError('Name must be an instance of {} but is {}'.format(str, name))
        if not isinstance(var, int):
            raise TypeError('Variable must be an instance of {} but is {}'.format(int, var))
        self.__var__ = var
        self.__var_name__ = name

    def less_than(self, value):
        # type: (IntValidator, int) -> IntValidator
        if not self.__var__ < value:
            raise ValidationError('{} must be less than {} but is {}'
                                  .format(self.__var_name__, value, self.__var__))
        return self

    def greater_than(self, value):
        # type: (IntValidator, int) -> IntValidator
        if not self.__var__ > value:
            raise ValidationError('{} must be greater than {} but is {}'
                                  .format(self.__var_name__, value, self.__var__))
        return self

    def less_or_equal(self, value):
        # type: (IntValidator, int) -> IntValidator
        if not self.__var__ <= value:
            raise ValidationError('{} must be less than or equal to {} but is {}'
                                  .format(self.__var_name__, value, self.__var__))
        return self

    def greater_or_equal(self, value):
        # type: (IntValidator, int) -> IntValidator
        if not self.__var__ >= value:
            raise ValidationError('{} must be greater than or equal to {} but is {}'
                                  .format(self.__var_name__, value, self.__var__))
        return self


class StrValidator:
    def __init__(self, var, name='"Untitled var"'):
        # type: (StrValidator, str, str) -> None
        if not isinstance(name, str):
            raise TypeError('Name must be an instance of {} but is {}'.format(str, name))
        if not isinstance(var, str):
            raise TypeError('Variable must be an instance of {} but is {}'.format(int, var))
        self.__var__ = var
        self.__var_name__ = name


class AssureThat:
    def __init__(self, var, name='"Untitled var"'):
        # type: (AssureThat, ..., str) -> None
        if not isinstance(name, str):
            raise TypeError('Name must be an instance of {} but is {}'.format(str, name))
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

    def __validate_type__(self, _type):
        # type: (AssureThat, type) -> None
        if not isinstance(self.__var__, _type):
            raise ValidationError('{} must be an instance of {} but is {}'
                                  .format(self.__var_name__, _type, type(self.__var__)))


if __name__ == '__main__':
    v = 5.0
    try:
        AssureThat(v).is_float().less_than(12.4).greater_than(9.2)
    except ValidationError as e:
        print(e)
