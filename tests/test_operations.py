import pytest
from typing import Union
from app.operations import Operations


Number = Union[int, float]

@pytest.mark.parametrize(
    "a, b, expected",
    [
        (2, 3, 5),           # Test adding two positive integers
        (0, 0, 0),           # Test adding two zeros
        (-1, 1, 0),          # Test adding a negative and a positive integer
        (2.5, 3.5, 6.0),     # Test adding two positive floats
        (-2.5, 3.5, 1.0),    # Test adding a negative float and a positive float
    ],
    ids=[
        "add_two_positive_integers",
        "add_two_zeros",
        "add_negative_and_positive_integer",
        "add_two_positive_floats",
        "add_negative_float_and_positive_float",
    ]
)
def test_addition(a: Number, b: Number, expected: Number) -> None:
    result = Operations.addition(a,b)
    assert result == expected, f"Expected addition({a}, {b}) to be {expected}, but got {result}"
@pytest.mark.parametrize(
   "a, b, expected",
    [
        (5, 3, 2),           # Test subtracting a smaller positive integer from a larger one
        (0, 0, 0),           # Test subtracting two zeros
        (-5, -3, -2),        # Test subtracting a negative integer from another negative integer
        (10.5, 5.5, 5.0),    # Test subtracting two positive floats
        (-10.5, -5.5, -5.0), # Test subtracting two negative floats
    ],
    ids=[
        "subtract_smaller_positive_integer_from_larger",
        "subtract_two_zeros",
        "subtract_negative_integer_from_negative_integer",
        "subtract_two_positive_floats",
        "subtract_two_negative_floats",
    ]
)
def test_subtraction(a: Number, b: Number, expected: Number) -> None:
    result = Operations.subtraction(a,b)
    assert result == expected, f"Expected addition({a}, {b}) to be {expected}, but got {result}"
@pytest.mark.parametrize(
    "a, b, expected",
    [
        (2, 3, 6),           # Test multiplying two positive integers
        (0, 10, 0),          # Test multiplying zero with a positive integer
        (-2, -3, 6),         # Test multiplying two negative integers
        (2.5, 4.0, 10.0),    # Test multiplying two positive floats
        (-2.5, 4.0, -10.0),  # Test multiplying a negative float with a positive float
    ],
    ids=[
        "multiply_two_positive_integers",
        "multiply_zero_with_positive_integer",
        "multiply_two_negative_integers",
        "multiply_two_positive_floats",
        "multiply_negative_float_with_positive_float",
    ]
)
def test_multiplication(a: Number, b: Number, expected: Number) -> None:
    result = Operations.multiplication(a,b)
    assert result == expected, f"Expected addition({a}, {b}) to be {expected}, but got {result}"
@pytest.mark.parametrize(
    "a, b, expected",
    [
        (6, 3, 2.0),           # Test dividing two positive integers
        (-6, -3, 2.0),         # Test dividing two negative integers
        (6.0, 3.0, 2.0),       # Test dividing two positive floats
        (-6.0, 3.0, -2.0),     # Test dividing a negative float by a positive float
        (0, 5, 0.0),            # Test dividing zero by a positive integer
    ],
    ids=[
        "divide_two_positive_integers",
        "divide_two_negative_integers",
        "divide_two_positive_floats",
        "divide_negative_float_by_positive_float",
        "divide_zero_by_positive_integer",
    ]
)
def test_division(a: Number, b: Number, expected: Number) -> None:
    result = Operations.division(a,b)
    assert result == expected, f"Expected addition({a}, {b}) to be {expected}, but got {result}"

@pytest.mark.parametrize(
    "a, b",
    [
        (1, 0),    # Test dividing by zero with positive dividend
        (-1, 0),   # Test dividing by zero with negative dividend
        (0, 0),    # Test dividing zero by zero
    ],
    ids=[
        "divide_positive_dividend_by_zero",
        "divide_negative_dividend_by_zero",
        "divide_zero_by_zero",
    ]
)
def test_division_by_zero(a,b):
    """Test division by zero."""
    with pytest.raises(ValueError, match="Division by zero is not allowed.") as excinfo:
        Operations.division(a, b)

    assert "Division by zero is not allowed." in str(excinfo.value), \
    f"Expected error message 'Division by zero is not allowed.', but got '{excinfo.value}'"


@pytest.mark.parametrize(
    "a, b, expected",
    [
        (2, 3, 8),           # Test multiplying two positive integers
        (0, 10, 0),          # Test multiplying zero with a positive integer
        (5, 0, 1),         # Test multiplying two negative integers
    ],
    ids=[
        "raise_2_to_the_thir",
        "raise_zero_to_any_power",
        "raise_any_to_zero_power",
    ]
)
def test_power(a: Number, b:Number, expected: Number) -> None:
    result = Operations.power(a,b)
    assert result == expected, f"Expected power {a} to the {b} power to be {expected}, but got {result}"