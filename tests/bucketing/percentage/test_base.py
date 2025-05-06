from unittest import TestCase

from flipper.bucketing import Percentage


class TestLessThanOrEqualTo(TestCase):
    def test_when_comparison_is_greater_than_value_it_returns_false(self) -> None:
        percentage = Percentage(0.5)

        assert not percentage >= 0.6  # noqa: PLR2004

    def test_when_comparison_is_equal_to_value_it_returns_true(self) -> None:
        percentage = Percentage(0.5)

        assert percentage >= 0.5  # noqa: PLR2004

    def test_when_comparison_is_less_then_value_it_returns_true(self) -> None:
        percentage = Percentage(0.5)

        assert percentage >= 0.4  # noqa: PLR2004
