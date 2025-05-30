import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

from flipper.bucketing import LinearRampPercentage


class TestGetType(unittest.TestCase):
    def test_is_correct_value(self) -> None:
        percentage = LinearRampPercentage()
        assert percentage.get_type() == "LinearRampPercentage"


class TestValue(unittest.TestCase):
    def test_matches_initial_value_when_there_is_no_ramp_delta(self) -> None:
        value = 0.8
        percentage = LinearRampPercentage(initial_value=value, final_value=value)
        assert value == percentage.value

    def test_matches_final_value_when_there_is_no_ramp_duration(self) -> None:
        initial_value = 0.2
        final_value = 0.6
        percentage = LinearRampPercentage(
            initial_value=initial_value,
            final_value=final_value,
            ramp_duration=0,
        )
        assert final_value == percentage.value

    @patch("flipper.bucketing.percentage.linear_ramp_percentage.datetime")
    def test_returns_a_value_that_is_linearly_interpolated_between_initial_and_final_value_by_time(
        self,
        mock_datetime,
    ) -> None:
        now = datetime(2018, 1, 1)  # noqa: DTZ001

        mock_datetime.now.return_value = now
        mock_datetime.fromtimestamp = datetime.fromtimestamp

        initial_value = 0.2
        final_value = 0.6
        ramp_duration = 60
        expected_percentage = 0.5

        dt = timedelta(seconds=ramp_duration * expected_percentage)
        initial_time = int((now - dt).timestamp())

        percentage = LinearRampPercentage(
            initial_value=initial_value,
            final_value=final_value,
            ramp_duration=ramp_duration,
            initial_time=initial_time,
        )

        value_delta = final_value - initial_value
        expected = value_delta * expected_percentage + initial_value

        assert expected == percentage.value

    @patch("flipper.bucketing.percentage.linear_ramp_percentage.datetime")
    def test_when_ramp_duration_is_longer_than_one_hour_and_ramp_has_completed_it_computes_value_correctly(
        self,
        mock_datetime,
    ) -> None:
        now = datetime(2020, 10, 28)  # noqa: DTZ001

        mock_datetime.now.return_value = now
        mock_datetime.fromtimestamp = datetime.fromtimestamp

        initial_value = 0.1
        final_value = 1
        ramp_duration = 1601314960
        expected_percentage = 1

        dt = timedelta(seconds=ramp_duration * expected_percentage)
        initial_time = int((now - dt).timestamp())

        percentage = LinearRampPercentage(
            initial_value=initial_value,
            final_value=final_value,
            ramp_duration=ramp_duration,
            initial_time=initial_time,
        )

        value_delta = final_value - initial_value
        expected = value_delta * expected_percentage + initial_value

        assert expected == percentage.value


class TestToDict(unittest.TestCase):
    def test_returns_correct_values(self) -> None:
        initial_value = 0.2
        final_value = 0.6
        ramp_duration = 60
        initial_time = int(datetime(2018, 1, 1).timestamp())  # noqa: DTZ001

        percentage = LinearRampPercentage(
            initial_value=initial_value,
            final_value=final_value,
            ramp_duration=ramp_duration,
            initial_time=initial_time,
        )
        expected = {
            "type": LinearRampPercentage.get_type(),
            "initial_value": initial_value,
            "final_value": final_value,
            "ramp_duration": ramp_duration,
            "initial_time": initial_time,
        }
        assert expected == percentage.to_dict()


class TestFromDict(unittest.TestCase):
    def test_sets_correct_data(self) -> None:
        initial_value = 0.2
        final_value = 0.6
        ramp_duration = 60
        initial_time = int(datetime(2018, 1, 1).timestamp())  # noqa: DTZ001

        data = {
            "type": LinearRampPercentage.get_type(),
            "initial_value": initial_value,
            "final_value": final_value,
            "ramp_duration": ramp_duration,
            "initial_time": initial_time,
        }
        percentage = LinearRampPercentage.from_dict(data)
        assert data == percentage.to_dict()
