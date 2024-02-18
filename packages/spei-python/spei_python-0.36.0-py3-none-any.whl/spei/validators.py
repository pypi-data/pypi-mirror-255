from typing import TYPE_CHECKING, Optional, Type

from pydantic import ConstrainedStr, errors

if TYPE_CHECKING:
    from pydantic.typing import CallableGenerator


def digits(
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
) -> Type[str]:
    namespace = {
        'min_length': min_length,
        'max_length': max_length,
    }
    return type('DigitsValue', (Digits,), namespace)


class Digits(ConstrainedStr):
    @classmethod
    def __get_validators__(cls) -> 'CallableGenerator':
        yield from ConstrainedStr.__get_validators__()
        yield validate_digits


def validate_digits(value: str) -> str:  # noqa: WPS110
    if not value.isdigit():
        raise errors.NotDigitError
    return value
