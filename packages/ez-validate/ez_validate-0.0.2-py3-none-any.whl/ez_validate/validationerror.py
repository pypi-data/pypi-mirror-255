class ValidationError(BaseException):
    def __init__(self, message):
        # type: (ValidationError, str) -> None
        super(ValidationError, self).__init__(message)
