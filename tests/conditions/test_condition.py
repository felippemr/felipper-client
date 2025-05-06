import unittest
from uuid import uuid4

from flipper import Condition


class BaseTest(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def txt(self):
        return uuid4().hex


class TestCheck(BaseTest):
    def test_can_check_equality_true(self) -> None:
        condition = Condition(foo=True)

        assert condition.check(foo=True)

    def test_can_check_equality_false(self) -> None:
        condition = Condition(foo=True)

        assert not condition.check(foo=False)

    def test_can_check_greater_than_true(self) -> None:
        condition = Condition(foo__gt=5)

        assert condition.check(foo=11)

    def test_can_check_greater_than_false(self) -> None:
        condition = Condition(foo__gt=5)

        assert not condition.check(foo=4)

    def test_can_check_greater_than_false_when_equal(self) -> None:
        condition = Condition(foo__gt=5)

        assert not condition.check(foo=5)

    def test_can_check_greater_than_or_equal_true(self) -> None:
        condition = Condition(foo__gte=5)

        assert condition.check(foo=11)

    def test_can_check_greater_than_or_equal_false(self) -> None:
        condition = Condition(foo__gte=5)

        assert not condition.check(foo=4)

    def test_can_check_greater_than_or_equal_true_when_equal(self) -> None:
        condition = Condition(foo__gte=5)

        assert condition.check(foo=5)

    def test_can_check_less_than_true(self) -> None:
        condition = Condition(foo__lt=5)

        assert condition.check(foo=4)

    def test_can_check_less_than_false(self) -> None:
        condition = Condition(foo__lt=5)

        assert not condition.check(foo=7)

    def test_can_check_less_than_false_when_equal(self) -> None:
        condition = Condition(foo__lt=5)

        assert not condition.check(foo=5)

    def test_can_check_less_than_or_equal_true(self) -> None:
        condition = Condition(foo__lte=5)

        assert condition.check(foo=4)

    def test_can_check_less_than_or_equal_false(self) -> None:
        condition = Condition(foo__lte=5)

        assert not condition.check(foo=8)

    def test_can_check_less_than_or_equal_true_when_equal(self) -> None:
        condition = Condition(foo__lte=5)

        assert condition.check(foo=5)

    def test_can_check_negation_true(self) -> None:
        condition = Condition(foo__ne="abc")

        assert condition.check(foo="def")

    def test_can_check_negation_false(self) -> None:
        condition = Condition(foo__ne="abc")

        assert not condition.check(foo="abc")

    def test_can_check_set_membership_true(self) -> None:
        condition = Condition(foo__in=[1, 2, 3])

        assert condition.check(foo=3)

    def test_can_check_set_membership_false(self) -> None:
        condition = Condition(foo__in=[1, 2, 3])

        assert not condition.check(foo=4)

    def test_can_check_negated_set_membership_true(self) -> None:
        condition = Condition(foo__not_in=[1, 2, 3])

        assert condition.check(foo=5)

    def test_can_check_negated_set_membership_false(self) -> None:
        condition = Condition(foo__not_in=[1, 2, 3])

        assert not condition.check(foo=3)

    def test_returns_true_when_all_checks_are_met(self) -> None:
        condition = Condition(
            foo=True,
            bar=False,
            baz__gt=99,
            baz__lt=103,
            herp__gte=10,
            herp__lte=20,
            derp__ne=2,
            derp__in=[2, 43, 5, 8],
            derp__not_in=[8, 1000],
        )

        assert condition.check(foo=True, bar=False, baz=101, herp=20, derp=5)

    def test_returns_false_when_at_least_one_check_is_not_met(self) -> None:
        condition = Condition(
            foo=True,
            bar=False,
            baz__gt=99,
            baz__lt=103,
            herp__gte=10,
            herp__lte=20,
            derp__ne=2,
            derp__in=[2, 43, 5, 8],
            derp__not_in=[8, 1000],
        )

        assert not condition.check(foo=True, bar=False, baz=101, herp=21, derp=5)


class TestToDict(BaseTest):
    def test_includes_all_checks(self) -> None:
        condition = Condition(
            foo=True,
            bar=False,
            baz__gt=99,
            baz__lt=103,
            herp__gte=10,
            herp__lte=20,
            derp__ne=2,
            derp__in=[2, 43, 5, 8],
            derp__not_in=[8, 1000],
        )

        expected = {
            "foo": [{"variable": "foo", "value": True, "operator": None}],
            "bar": [{"variable": "bar", "value": False, "operator": None}],
            "baz": [
                {"variable": "baz", "value": 99, "operator": "gt"},
                {"variable": "baz", "value": 103, "operator": "lt"},
            ],
            "herp": [
                {"variable": "herp", "value": 10, "operator": "gte"},
                {"variable": "herp", "value": 20, "operator": "lte"},
            ],
            "derp": [
                {"variable": "derp", "value": 2, "operator": "ne"},
                {"variable": "derp", "value": [2, 43, 5, 8], "operator": "in"},
                {"variable": "derp", "value": [8, 1000], "operator": "not_in"},
            ],
        }

        self._compare(expected, condition.to_dict())

    def _compare(self, expected, actual) -> None:
        for key, checks in expected.items():
            for check in checks:
                assert check in actual[key]


class TestFromDict(BaseTest):
    def test_includes_all_checks(self) -> None:
        input = {  # noqa: A001
            "foo": [{"variable": "foo", "value": True, "operator": None}],
            "bar": [{"variable": "bar", "value": False, "operator": None}],
            "baz": [
                {"variable": "baz", "value": 99, "operator": "gt"},
                {"variable": "baz", "value": 103, "operator": "lt"},
            ],
            "herp": [
                {"variable": "herp", "value": 10, "operator": "gte"},
                {"variable": "herp", "value": 20, "operator": "lte"},
            ],
            "derp": [
                {"variable": "derp", "value": 2, "operator": "ne"},
                {"variable": "derp", "value": [2, 43, 5, 8], "operator": "in"},
                {"variable": "derp", "value": [8, 1000], "operator": "not_in"},
            ],
        }

        condition = Condition.from_dict(input)

        self._compare(input, condition.to_dict())

    def _compare(self, expected, actual) -> None:
        for key, checks in expected.items():
            for check in checks:
                assert check in actual[key]
