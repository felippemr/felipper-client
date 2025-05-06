"""
   isort:skip_file
   See: https://github.com/ambv/black/issues/250
"""
import unittest
from unittest.mock import MagicMock
from uuid import uuid4

from flipper.conditions.check import OPERATOR_DELIMITER, Check
from flipper.conditions.operators.equality_operator import EqualityOperator
from flipper.conditions.operators.greater_than_operator import GreaterThanOperator
from flipper.conditions.operators.greater_than_or_equal_to_operator import (
    GreaterThanOrEqualToOperator,
)
from flipper.conditions.operators.less_than_operator import LessThanOperator
from flipper.conditions.operators.less_than_or_equal_to_operator import (
    LessThanOrEqualToOperator,
)
from flipper.conditions.operators.negated_set_membership_operator import (
    NegatedSetMembershipOperator,
)
from flipper.conditions.operators.negation_operator import NegationOperator
from flipper.conditions.operators.set_membership_operator import SetMembershipOperator


class BaseTest(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def txt(self):
        return uuid4().hex


class TestCheck(BaseTest):
    def test_calls_operator_with_correct_arguments(self) -> None:
        initial_value = self.txt()
        operator = MagicMock(return_value=True)
        check = Check(self.txt(), initial_value, operator)

        compared_value = self.txt()

        check.check(compared_value)

        operator.compare.assert_called_once_with(compared_value, initial_value)


class TestFactory(BaseTest):
    def test_returns_instance_of_check(self) -> None:
        check = Check.factory("foo", 1)
        assert isinstance(check, Check)

    def test_returns_instance_of_equality_operator(self) -> None:
        check = Check.factory("foo", 1)
        assert isinstance(check.operator, EqualityOperator)

    def test_returns_instance_of_greater_than_operator(self) -> None:
        check = Check.factory("foo__gt", 1)
        assert isinstance(check.operator, GreaterThanOperator)

    def test_returns_instance_of_greater_than_or_equal_to_operator(self) -> None:
        check = Check.factory("foo__gte", 1)
        assert isinstance(check.operator, GreaterThanOrEqualToOperator)

    def test_returns_instance_of_less_than_operator(self) -> None:
        check = Check.factory("foo__lt", 1)
        assert isinstance(check.operator, LessThanOperator)

    def test_returns_instance_of_less_than_or_equal_to_operator(self) -> None:
        check = Check.factory("foo__lte", 1)
        assert isinstance(check.operator, LessThanOrEqualToOperator)

    def test_returns_instance_of_negated_set_membership_operator(self) -> None:
        check = Check.factory("foo__not_in", [1])
        assert isinstance(check.operator, NegatedSetMembershipOperator)

    def test_returns_instance_of_negation_operator(self) -> None:
        check = Check.factory("foo__ne", 1)
        assert isinstance(check.operator, NegationOperator)

    def test_returns_instance_of_set_membership_operator(self) -> None:
        check = Check.factory("foo__in", [1])
        assert isinstance(check.operator, SetMembershipOperator)


class TestToDict(BaseTest):
    def test_includes_expected_fields(self) -> None:
        variable, value, operator = self.txt(), self.txt(), EqualityOperator()

        check = Check(variable, value, operator)

        assert {"variable": variable, "value": value, "operator": operator.SYMBOL} == check.to_dict()


class TestFromDict(BaseTest):
    def test_includes_expected_fields(self) -> None:
        variable, value, operator = self.txt(), self.txt(), EqualityOperator()

        json = {"variable": variable, "value": value, "operator": operator.SYMBOL}

        check = Check.from_dict(json)

        assert json == check.to_dict()


class TestMakeCheckKey(BaseTest):
    def test_returns_variable_and_operator_with_delimiter(self) -> None:
        variable, operator = self.txt(), "gt"
        key = Check.make_check_key(variable, operator)
        assert OPERATOR_DELIMITER.join([variable, operator]) == key

    def test_returns_variable_only_when_operator_is_none(self) -> None:
        variable, operator = self.txt(), None
        key = Check.make_check_key(variable, operator)
        assert variable == key
