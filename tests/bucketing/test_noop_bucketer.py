import unittest

from flipper.bucketing import NoOpBucketer


class TestGetType(unittest.TestCase):
    def test_is_correct_value(self) -> None:
        bucketer = NoOpBucketer()
        assert bucketer.get_type() == "NoOpBucketer"


class TestCheck(unittest.TestCase):
    def test_always_returns_true_with_no_checks(self) -> None:
        bucketer = NoOpBucketer()
        assert bucketer.check()

    def test_always_returns_true_with_checks(self) -> None:
        bucketer = NoOpBucketer()
        assert bucketer.check(foo=1)


class TestToDict(unittest.TestCase):
    def test_returns_correct_data(self) -> None:
        bucketer = NoOpBucketer()
        expected = {"type": NoOpBucketer.get_type()}
        assert expected == bucketer.to_dict()


class TestFromDict(unittest.TestCase):
    def test_sets_correct_data(self) -> None:
        data = {"type": NoOpBucketer.get_type()}
        bucketer = NoOpBucketer.from_dict(data)
        assert data == bucketer.to_dict()
