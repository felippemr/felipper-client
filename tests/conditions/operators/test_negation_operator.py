import unittest

from flipper.conditions.operators.negation_operator import NegationOperator


class TestCompare(unittest.TestCase):
    def test_returns_true_when_values_are_not_equal(self) -> None:
        operator = NegationOperator()

        assert operator.compare(2, 1)

    def test_returns_false_when_values_equal(self) -> None:
        operator = NegationOperator()

        assert not operator.compare(1, 1)
