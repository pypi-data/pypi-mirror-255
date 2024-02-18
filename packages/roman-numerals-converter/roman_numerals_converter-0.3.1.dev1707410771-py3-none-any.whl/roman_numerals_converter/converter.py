import random
import re
import string

from roman_numerals_converter.roman import ROMAN_REGEX, RomanError, RomanNumeral


def convert_to_roman(number: int) -> str:
    """
    Convert a decimal number to a Roman numeral.

    Args:
        number (int): The decimal number to convert.

    Returns:
        str: The Roman numeral representation.
    """
    try:
        roman_numeral = RomanNumeral.from_decimal(number)
        return str(roman_numeral)
    except RomanError as e:
        raise ValueError(f"Error converting to Roman: {str(e)}") from e


def convert_from_roman(roman: str) -> int:
    """
    Convert a Roman numeral to a decimal number.

    Args:
        roman (str): The Roman numeral to convert.

    Returns:
        int: The decimal number representation.
    """
    try:
        roman_numeral = RomanNumeral(roman)
        return roman_numeral.to_decimal()
    except RomanError:
        raise ValueError("Error converting from Roman: Invalid Roman numeral") from None


def random_roman(min_value: int = 1, max_value: int = 3999) -> tuple[str, int]:
    """
    Generate a random Roman numeral. Raises an exception if input is invalid.

    Args:
        min_value (int): Minimum value for the generated number (inclusive).
        max_value (int): Maximum value for the generated number (inclusive).

    Returns:
        str: A random Roman numeral.

    Raises:
        ValueError: If input values are out of the allowed range or min_value is greater than max_value.
    """  # noqa: E501
    if not (1 <= min_value <= 3999 and 1 <= max_value <= 3999):
        raise ValueError("Input values must be between 1 and 3999.")
    if min_value > max_value:
        raise ValueError("Minimum value cannot be greater than maximum value.")

    number = random.randint(min_value, max_value)
    return convert_to_roman(number), number


def replace_roman_numerals_with_integers_in_text(text: str) -> str:
    """
    Replace all Roman numerals in a given text with their decimal equivalents.

    Args:
        text (str): The text containing Roman numerals.

    Returns:
        str: The text with Roman numerals replaced by decimal numbers.
    """
    non_punctation_text = text.translate(str.maketrans("", "", string.punctuation))
    for word in non_punctation_text.split():
        if re.match(ROMAN_REGEX, word):
            try:
                decimal = convert_from_roman(word)
                text = text.replace(word, str(decimal))
            except ValueError:
                pass
    return text


def replace_integers_with_roman_numerals(text: str) -> str:
    """
    Replace all integers in a given text with their Roman numeral equivalents.

    Args:
        text (str): The text containing integers.

    Returns:
        str: The text with integers replaced by Roman numerals.
    """
    # Regular expression to find integers
    INTEGER_REGEX = r"\b\d+\b"

    # Function to replace each integer with its Roman numeral equivalent
    def replace_integer(match):  # type: ignore
        integer = int(match.group(0))  # type: ignore
        return convert_to_roman(integer)

    return re.sub(INTEGER_REGEX, replace_integer, text)  # type: ignore
