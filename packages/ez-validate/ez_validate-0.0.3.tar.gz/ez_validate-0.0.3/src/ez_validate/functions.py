from .validationerror import ValidationError


def either(*args):
    # type: (...) -> None
    errors = []
    for f in args:
        try:
            f()
        except ValidationError as error:
            errors.append(error)
    if len(errors) == len(args):
        message = 'Either of this conditions must be true:\n' + '\n'.join(map(str, errors))
        raise ValidationError(message)
