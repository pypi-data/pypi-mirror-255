"""Roman numerals converter.
This script provides a command-line interface to convert numbers to Roman numerals and vice versa.
"""  # noqa: E501

import click

from .roman import RomanNumeral


@click.group()
def cli() -> None:
    """Click group for the CLI.
    This group bundles the commands for converting to and from Roman numerals.
    """
    pass


@cli.command()
@click.argument("number", type=int)
def to_roman(number: int) -> None:
    """
    Convert a number to a Roman numeral.

    Args:
        number (int): A decimal number to be converted into Roman numeral.

    This function takes an integer and converts it into its Roman numeral representation.
    It checks if the number is within the permissible range (1-3999) and then converts it
    using defined Roman numeral mappings.
    """  # noqa: E501
    # Check that the number is within the valid range
    if not 0 < number < 4000:
        raise click.BadParameter("Please enter a number between 1 and 3999.")

    # Convert the number to a Roman numeral
    roman: RomanNumeral = RomanNumeral.from_decimal(number)
    click.echo(roman)


@cli.command()
@click.argument("roman", type=str)
def from_roman(roman: str) -> None:
    """
    Convert a Roman numeral to a number.

    Args:
        roman (str): A Roman numeral to be converted into a decimal number.

    This function takes a Roman numeral and converts it into its decimal representation.
    It first validates the Roman numeral using a regular expression and then performs
    the conversion using defined mappings from Roman numerals to decimal numbers.
    """
    # Validate Roman numeral input
    if not RomanNumeral.is_valid_roman(roman):
        raise click.BadParameter("Please enter a valid Roman numeral.")

    # Mapping of Roman numerals to decimal numbers
    rn = RomanNumeral(roman)
    num: int = rn.to_decimal()
    click.echo(num)
