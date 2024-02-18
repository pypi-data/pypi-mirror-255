class StrValidator:
    def __init__(self, var, name='"Untitled var"'):
        # type: (StrValidator, str, str) -> None
        if not isinstance(name, str):
            raise TypeError('Name must be an instance of {} but is {}'.format(str, type(name)))
        if not isinstance(var, str):
            raise TypeError('Variable must be an instance of {} but is {}'.format(int, type(var)))
        self.__var__ = var
        self.__var_name__ = name
