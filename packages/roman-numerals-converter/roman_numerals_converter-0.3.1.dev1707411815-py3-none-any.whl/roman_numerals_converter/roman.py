"""Roman numerals converter.
This script provides a command-line interface to convert numbers to Roman numerals and vice versa.
"""  # noqa: E501

import re
from typing import Union

# Regular expression for validating Roman numerals
ROMAN_REGEX = r"^(?=.)M{0,3}(C[MD]|D?C{0,3})(X[CL]|L?X{0,3})(I[XV]|V?I{0,3})$"


class RomanError(Exception):
    """Base class for exceptions in this module."""

    pass


class RomanNumeral:
    """Class for converting Roman numerals to decimal numbers and vice versa.
    This class provides a constructor for creating a RomanNumeral object from a
    Roman numeral or a decimal number. It also provides methods for converting
    a Roman numeral to a decimal number and vice versa.
    """

    ROMAN_INT_MAP = [
        ("M", 1000),
        ("CM", 900),
        ("D", 500),
        ("CD", 400),
        ("C", 100),
        ("XC", 90),
        ("L", 50),
        ("XL", 40),
        ("X", 10),
        ("IX", 9),
        ("V", 5),
        ("IV", 4),
        ("I", 1),
    ]

    # Mapping of decimal numbers to Roman numerals
    INT_ROMAN_MAP = [
        (1000, "M"),
        (900, "CM"),
        (500, "D"),
        (400, "CD"),
        (100, "C"),
        (90, "XC"),
        (50, "L"),
        (40, "XL"),
        (10, "X"),
        (9, "IX"),
        (5, "V"),
        (4, "IV"),
        (1, "I"),
    ]

    def __init__(self, value: str) -> None:
        """Constructor for RomanNumeral class.
        Args:
            value (str): A Roman numeral or a decimal number.
        """
        # Validate input
        if not isinstance(value, str):  # type: ignore
            raise RomanError("Please enter a string.")

        # Check if the input is a Roman numeral
        if not self.is_valid_roman(value):
            raise RomanError("Please enter a valid Roman numeral.")

        self._value = value

    def to_decimal(self) -> int:
        """Convert a Roman numeral to a decimal number.
        Returns:
            int: The decimal representation of the Roman numeral.
        """
        roman_value = self._value
        # Conversion process
        decimal = 0
        for numeral, value in self.ROMAN_INT_MAP:
            while roman_value.startswith(numeral):
                decimal += value
                roman_value = roman_value[len(numeral) :]

        return decimal

    def __str__(self) -> str:
        """Convert a Roman numeral to a string.
        Returns:
            str: The Roman numeral representation of the object.
        """
        return self._value

    def __repr__(self) -> str:
        """Convert a Roman numeral to a string.
        Returns:
            str: The Roman numeral representation of the object.
        """
        return f"RomanNumeral('{self._value}')"

    def __eq__(self, other: object) -> bool:
        """Compare two RomanNumeral objects.
        Args:
            other (object): Another object.
        Returns:
            bool: True if the two objects are equal, False otherwise.
        """
        if isinstance(other, RomanNumeral):
            return self._value == other._value

        if isinstance(other, str):
            return self._value == other

        if isinstance(other, int):
            return self.to_decimal() == other

        return NotImplemented

    def __ne__(self, other: object) -> bool:
        """Compare two RomanNumeral objects.
        Args:
            other (object): Another object.
        Returns:
            bool: True if the two objects are not equal, False otherwise.
        """
        if isinstance(other, RomanNumeral):
            return self._value != other._value

        if isinstance(other, str):
            return self._value != other

        if isinstance(other, int):
            return self.to_decimal() != other

        return NotImplemented

    def __lt__(self, other: object) -> bool:
        """Compare two RomanNumeral objects.
        Args:
            other (object): Another object.
        Returns:
            bool: True if the first object is less than the second object, False otherwise.
        """  # noqa: E501
        if isinstance(other, RomanNumeral):
            return self.to_decimal() < other.to_decimal()

        if isinstance(other, str):
            return self.to_decimal() < RomanNumeral(other).to_decimal()

        if isinstance(other, int):
            return self.to_decimal() < other

        return NotImplemented

    def __le__(self, other: object) -> bool:
        """Compare two RomanNumeral objects.
        Args:
            other (object): Another object.
        Returns:
            bool: True if the first object is less than or equal to the second object, False otherwise.
        """  # noqa: E501
        if isinstance(other, RomanNumeral):
            return self.to_decimal() <= other.to_decimal()

        if isinstance(other, str):
            return self.to_decimal() <= RomanNumeral(other).to_decimal()

        if isinstance(other, int):
            return self.to_decimal() <= other

        return NotImplemented

    def __gt__(self, other: object) -> bool:
        """Compare two RomanNumeral objects.
        Args:
            other (object): Another object.
        Returns:
            bool: True if the first object is greater than the second object, False otherwise.
        """  # noqa: E501
        if isinstance(other, RomanNumeral):
            return self.to_decimal() > other.to_decimal()

        if isinstance(other, str):
            return self.to_decimal() > RomanNumeral(other).to_decimal()

        if isinstance(other, int):
            return self.to_decimal() > other

        return NotImplemented

    def __ge__(self, other: object) -> bool:
        """Compare two RomanNumeral objects.
        Args:
            other (object): Another object.
        Returns:
            bool: True if the first object is greater than or equal to the second object, False otherwise.
        """  # noqa: E501
        if isinstance(other, RomanNumeral):
            return self.to_decimal() >= other.to_decimal()

        if isinstance(other, str):
            return self.to_decimal() >= RomanNumeral(other).to_decimal()

        if isinstance(other, int):
            return self.to_decimal() >= other

        return NotImplemented

    def __add__(self, other: object) -> "RomanNumeral":
        """Add Int | Str | RomanNumeral to RomanNumeral.
        Args:
            other (object): Another object.
        Returns:
            RomanNumeral: The sum of the two objects.
        """
        if not isinstance(other, (RomanNumeral, str, int)):
            return NotImplemented

        sum: int = 0

        if isinstance(other, RomanNumeral):
            sum = self.to_decimal() + other.to_decimal()

        if isinstance(other, str):
            sum = self.to_decimal() + RomanNumeral(other).to_decimal()

        if isinstance(other, int):
            sum = self.to_decimal() + other

        assert 0 < sum < 4000, "Addition result must be between 1 and 3999."

        return RomanNumeral.from_decimal(sum)

    def __radd__(self, other: object) -> Union[str, int]:
        """Add RomanNumeral to object.
        Args:
            other (object): Another object.
        Returns:
            object: The sum of the two objects.
        """

        if isinstance(other, str):
            return other + self.__str__()

        if isinstance(other, int):
            return other + self.to_decimal()

        return NotImplemented

    def __sub__(self, other: object) -> "RomanNumeral":
        """Subtract Int | Str | RomanNumeral from RomanNumeral.
        Args:
            other (object): Another object.
        Returns:
            RomanNumeral: The difference of the two objects.
        """
        if not isinstance(other, (RomanNumeral, str, int)):
            return NotImplemented

        difference: int = 0

        if isinstance(other, RomanNumeral):
            difference = self.to_decimal() - other.to_decimal()

        if isinstance(other, str):
            difference = self.to_decimal() - RomanNumeral(other).to_decimal()

        if isinstance(other, int):
            difference = self.to_decimal() - other

        assert 0 < difference < 4000, "Subtraction result must be between 1 and 3999."

        return RomanNumeral.from_decimal(difference)

    def __rsub__(self, other: object) -> int:
        """Subtract RomanNumeral from object.
        Args:
            other (object): Another object.
        Returns:
            object: The difference of the two objects.
        """
        if not isinstance(other, int):
            return NotImplemented

        return other - self.to_decimal()

    def __mul__(self, other: object) -> "RomanNumeral":
        """Multiply RomanNumeral by Int | Str | RomanNumeral.
        Args:
            other (object): Another object.
        Returns:
            RomanNumeral: The product of the two objects.
        """
        if not isinstance(other, (RomanNumeral, str, int)):
            return NotImplemented

        product: int = 0

        if isinstance(other, RomanNumeral):
            product = self.to_decimal() * other.to_decimal()

        if isinstance(other, str):
            product = self.to_decimal() * RomanNumeral(other).to_decimal()

        if isinstance(other, int):
            product = self.to_decimal() * other

        assert 0 < product < 4000, "Multiplication result must be between 1 and 3999."

        return RomanNumeral.from_decimal(product)

    def __rmul__(self, other: object) -> "RomanNumeral":
        """Multiply Int | Str | RomanNumeral by RomanNumeral.
        Args:
            other (object): Another object.
        Returns:
            RomanNumeral: The product of the two objects.
        """
        if not isinstance(other, (RomanNumeral, str, int)):
            return NotImplemented

        product: int = 0

        if isinstance(other, RomanNumeral):
            product = self.to_decimal() * other.to_decimal()

        if isinstance(other, str):
            product = self.to_decimal() * RomanNumeral(other).to_decimal()

        if isinstance(other, int):
            product = self.to_decimal() * other

        assert 0 < product < 4000, "Multiplication result must be between 1 and 3999."

        return RomanNumeral.from_decimal(product)

    def __truediv__(self, other: object) -> "RomanNumeral":
        """Divide RomanNumeral by Int | Str | RomanNumeral.
        Args:
            other (object): Another object.
        Returns:
            RomanNumeral: The quotient of the two objects.
        """
        if not isinstance(other, (RomanNumeral, str, int)):
            return NotImplemented

        quotient: int = 0

        if isinstance(other, RomanNumeral):
            quotient = self.to_decimal() // other.to_decimal()

        if isinstance(other, str):
            quotient = self.to_decimal() // RomanNumeral(other).to_decimal()

        if isinstance(other, int):
            quotient = self.to_decimal() // other

        assert 0 < quotient < 4000, "Division result must be between 1 and 3999."

        return RomanNumeral.from_decimal(quotient)

    def __rtruediv__(self, other: object) -> float:
        """Divide Int | Str | RomanNumeral by RomanNumeral.
        Args:
            other (object): Another object.
        Returns:
            RomanNumeral: The quotient of the two objects.
        """
        if not isinstance(other, (RomanNumeral, str, int)):
            return NotImplemented

        quotient: float = 0

        if isinstance(other, RomanNumeral):
            quotient = other.to_decimal() / self.to_decimal()

        if isinstance(other, str):
            quotient = RomanNumeral(other).to_decimal() / self.to_decimal()

        if isinstance(other, int):
            quotient = other / self.to_decimal()

        return quotient

    @staticmethod
    def is_valid_roman(value: str) -> bool:
        """Check if a string is a valid Roman numeral.
        Args:
            value (str): A string to be checked.
        Returns:
            bool: True if the string is a valid Roman numeral, False otherwise.
        """
        return bool(re.search(ROMAN_REGEX, value) is not None)

    @classmethod
    def from_decimal(cls, number: int) -> "RomanNumeral":
        """Convert a decimal number to a Roman numeral.
        Args:
            number (int): A decimal number.
        Returns:
            str: The Roman numeral representation of the decimal number.
        """
        if not isinstance(number, int):  # type: ignore
            raise RomanError("Number must be an integer.")

        # Check that the number is within the valid range
        if not 0 < number < 4000:
            raise RomanError("Number must be between 1 and 3999.")

        # Conversion process
        roman = ""
        for value, numeral in cls.INT_ROMAN_MAP:
            while number >= value:
                roman += numeral
                number -= value

        return cls(roman)
